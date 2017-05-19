import unittest
from unittest.mock import Mock
from unittest.mock import MagicMock
import neovim

from python3.neotags import NeotagsPlugin


class TestNeotagsPlugin(unittest.TestCase):

    def setUp(self):
        self.plugin = NeotagsPlugin(Mock(neovim.api.nvim))

    def test_default_options(self):
        self.assertEqual('ctags', self.plugin.options['ctags_cmd'])
        self.assertEqual('tags', self.plugin.options['tags_filename'])
        self.assertEqual(False, self.plugin.options['logging'])

    def test_default_options(self):
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
