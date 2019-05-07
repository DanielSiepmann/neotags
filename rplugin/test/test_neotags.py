from unittest.mock import Mock
from unittest.mock import MagicMock
from pyfakefs import fake_filesystem_unittest
import pynvim
import os

from python3.neotags import NeotagsPlugin


class TestNeotagsPlugin(fake_filesystem_unittest.TestCase):

    def setUp(self):
        self.templates_dirname = os.path.join(
            os.path.dirname(__file__),
            'templates'
        )
        self.setUpPyfakefs()
        self.plugin = NeotagsPlugin(Mock(pynvim.api.nvim))

    def test_default_options(self):
        self.assertEqual('ctags', self.plugin.options['ctags_cmd'])
        self.assertEqual('tags', self.plugin.options['tags_filename'])
        self.assertEqual(False, self.plugin.options['logging'])

    def test_custom_options(self):
        self.plugin.nvim.configure_mock(vars={})
        self.plugin.nvim.vars['neotags_tags_filename'] = 'new_tags'
        self.plugin.nvim.vars['neotags_ctags_cmd'] = 'new_ctags'
        self.plugin.nvim.vars['neotags_logging'] = True

        self.plugin.update_settings()

        self.assertEqual('new_tags', self.plugin.options['tags_filename'])
        self.assertEqual('new_ctags', self.plugin.options['ctags_cmd'])
        self.assertEqual(True, self.plugin.options['logging'])

    def test_debug_logs_to_nvim_when_logging_is_active(self):
        self.plugin.options['logging'] = True
        self.plugin.nvim.out_write = MagicMock()

        self.plugin.debug('some message')
        self.plugin.nvim.out_write.assert_called_once_with(
            "neotags > some message\n"
        )

    def test_debug_does_not_log_to_nvim_when_logging_is_inactive(self):
        self.plugin.options['logging'] = False
        self.plugin.nvim.out_write = MagicMock()

        self.plugin.debug('some message')
        self.plugin.nvim.out_write.assert_not_called()

    def test_error_logs_to_nvim_when_logging_is_active(self):
        self.plugin.options['logging'] = True
        self.plugin.nvim.err_write = MagicMock()

        self.plugin.error('some message')
        self.plugin.nvim.err_write.assert_called_once_with(
            "neotags > some message\n"
        )

    def test_error_does_not_log_to_nvim_when_logging_is_inactive(self):
        self.plugin.options['logging'] = False
        self.plugin.nvim.err_write = MagicMock()

        self.plugin.error('some message')
        self.plugin.nvim.err_write.assert_not_called()

    def test_get_tags_file_in_same_folder(self):
        filename = '/var/data/some_file.py'
        expected_tags_filename = '/var/data/tags'

        self.fs.CreateFile(filename)
        self.fs.CreateFile(expected_tags_filename)

        self.assertEqual(
            expected_tags_filename,
            self.plugin.get_tags_file(filename)
        )

    def test_get_tags_file_in_parent_folder(self):
        filename = '/var/data/some_file.py'
        expected_tags_filename = '/var/tags'

        self.fs.CreateFile(filename)
        self.fs.CreateFile(expected_tags_filename)

        self.assertEqual(
            expected_tags_filename,
            self.plugin.get_tags_file(filename)
        )

    def test_get_tags_file_in_root_folder(self):
        filename = '/var/data/some_file.py'
        expected_tags_filename = '/tags'

        self.fs.CreateFile(filename)
        self.fs.CreateFile(expected_tags_filename)

        self.assertEqual(
            expected_tags_filename,
            self.plugin.get_tags_file(filename)
        )

    def test_strips_existing_tags(self):
        filename = '/var/data/example.py'
        tags_file = '/var/data/tags'
        expected_tags_file = os.path.join(
            self.templates_dirname,
            'expected_tags'
        )

        self.copyRealFile(
            expected_tags_file,
            expected_tags_file
        )
        self.copyRealFile(
            os.path.join(self.templates_dirname, 'example.py'),
            os.path.join(os.path.dirname(filename), os.path.basename(filename))
        )
        self.copyRealFile(
            os.path.join(self.templates_dirname, 'tags'),
            os.path.join(
                os.path.dirname(tags_file), os.path.basename(tags_file)
            )
        )

        self.plugin.strip_existing_tags(tags_file, os.path.basename(filename))
        with open(tags_file) as f, open(expected_tags_file) as e:
            self.assertEqual(e.read(), f.read())
