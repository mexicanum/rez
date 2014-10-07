from rez.contrib.animallogic.launcher.operatingsystem import OperatingSystem
from rez.contrib.animallogic.launcher.settingtype import SettingType
from rez.contrib.animallogic.launcher.mode import Mode
from rez.contrib.animallogic.launcher.setting import Setting
from rez.contrib.animallogic.launcher.service import LauncherHessianService
from rez.contrib.animallogic.launcher.exceptions import LauncherError
from rez.contrib.animallogic.launcher.tests.stubs import StubPresetProxy, StubToolsetProxy
import rez.vendor.unittest2 as unittest
import datetime


class BaseTestLauncherHessianService(unittest.TestCase):

    def setUp(self):

        self.username = 'username'
        self.operating_system = OperatingSystem.get_current_operating_system()
        self.now = datetime.datetime.now()
        self.mode = Mode.shell

    def assert_settings(self, expected_settings, settings):

        self.assertEqual(len(expected_settings), len(settings))
        for expected_setting, setting in zip(expected_settings, settings):
            self.assert_setting(expected_setting, setting)

    def assert_setting(self, expected, setting):

        self.assertEqual(expected['name'], setting.name)
        self.assertEqual(expected['value'], setting.value)
        
        if expected['opSystem']:
            self.assertEqual(expected['opSystem']['name'], setting.operating_system.value)
        else:
            self.assertEqual(expected['opSystem'], setting.operating_system.value)

        self.assertEqual(expected['type']['name'], setting.setting_type.launcher_type)
        self.assertEqual(expected['id'], setting.id)
        self.assertEqual(expected['sourcePresetId']['key'], setting.source_preset_id)

    def assert_preset(self, expected, preset):

        self.assertEqual(expected['name'], preset.name)
        self.assertEqual(expected['description'], preset.description)
        self.assertEqual(expected['parentId']['key'], preset.parent_id)
        self.assertEqual(expected['id']['key'], preset.id)


class TestLauncherHessianService_GetSettings(BaseTestLauncherHessianService):

    def setUp(self):

        BaseTestLauncherHessianService.setUp(self)

        self.preset_settings = [{'name':'preset_setting', 'value':'1.2.3', 'opSystem':None, 'type':{'name':'tPackage'}, 'id': 123, 'sourcePresetId':{'key':999}}]
        self.preset_path = '/presets/Rez/test'
        self.toolset_settings = [{'name':'preset_setting', 'value':'4.5.6', 'opSystem':{'name':'linux'}, 'type':{'name':'tVersion'}, 'id': 456, 'sourcePresetId':{'key':998}}]
        self.toolset_path = '/toolsets/Rez/test'

    def test_get_settings_from_preset_path(self):

        launcher_service = LauncherHessianService(StubPresetProxy(self.preset_settings, self.preset_path), StubToolsetProxy({}, ""))

        settings = launcher_service.get_settings_from_path(self.preset_path, self.mode, username=self.username, operating_system=self.operating_system, date=self.now)
        self.assert_settings(self.preset_settings, settings)

    def test_get_settings_from_toolset_path(self):

        launcher_service = LauncherHessianService(StubPresetProxy({}, ""), StubToolsetProxy(self.toolset_settings, self.toolset_path))

        settings = launcher_service.get_settings_from_path(self.toolset_path, self.mode, username=self.username, operating_system=self.operating_system, date=self.now)
        self.assert_settings(self.toolset_settings, settings)

    def test_get_settings_from_preset_path_that_does_not_exist(self):

        launcher_service = LauncherHessianService(StubPresetProxy(self.preset_settings, self.preset_path), StubToolsetProxy({}, ""))

        self.assertRaises(LauncherError, launcher_service.get_settings_from_path, "/presets/path/does/not/exist", self.mode, username=self.username, operating_system=self.operating_system, date=self.now)

    def test_get_settings_from_toolset_path_that_does_not_exist(self):

        launcher_service = LauncherHessianService(StubPresetProxy({}, ""), StubToolsetProxy(self.toolset_settings, self.toolset_path))

        self.assertRaises(LauncherError, launcher_service.get_settings_from_path, "/path/does/not/exist", self.mode, username=self.username, operating_system=self.operating_system, date=self.now)


class TestLauncherHessianService_AddSettingToPreset(BaseTestLauncherHessianService):

    def setUp(self):

        BaseTestLauncherHessianService.setUp(self)

        self.new_setting = Setting('new', 'value', SettingType.string)

    def test_add_setting_to_preset(self):

        launcher_service = LauncherHessianService(StubPresetProxy({}, ""), StubToolsetProxy({}, ""))

        name, value, setting_type_as_dict = launcher_service.add_setting_to_preset(self.new_setting, "/preset/path", username=self.username)
        self.assertEqual(self.new_setting.name, name)
        self.assertEqual(self.new_setting.value, value)
        self.assertEqual({'name':self.new_setting.setting_type.launcher_type}, setting_type_as_dict)


class TestLauncherHessianService_CreatePreset(BaseTestLauncherHessianService):

    def setUp(self):

        BaseTestLauncherHessianService.setUp(self)

        self.new_preset = {'fullyQualifiedName':'/presets/Rez/test_new', 'description':'bar', 'parentId':{'key':43325883}, 'id':{'key':4077}, 'name':'test_new'}

    def test_create_preset(self):

        launcher_service = LauncherHessianService(StubPresetProxy({}, "", self.new_preset), StubToolsetProxy({}, ""))

        preset = launcher_service.create_preset(self.new_preset['fullyQualifiedName'], 'hello', username=self.username)
        self.assert_preset(self.new_preset, preset)
