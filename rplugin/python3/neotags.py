import neovim
import fileinput
import pathlib
import subprocess
import sys
import traceback


@neovim.plugin
class NeotagsPlugin(object):

    def __init__(self, nvim):
        self.nvim = nvim
        # Perhaps debugging settings?
        self.options = {
            'tags_filename': 'tags',
            'ctags_cmd': 'ctags',
            'logging': False,
        }

    def update_settings(self):
        for option, default in self.options.items():
            try:
                variable = 'neotags_%s' % option
                self.options[option] = self.nvim.vars[variable]
            except neovim.api.nvim.NvimError:
                self.options[option] = default

    # Check whether 'FileWritePost' is necessary
    @neovim.autocmd('BufWritePost', pattern='*', eval='expand("<afile>:p")')
    def update_tags_for_file(self, filename):
        self.update_settings()

        self.debug('Triggered for "%s"' % filename)

        pwd = self.nvim.funcs.execute('pwd').strip()
        relative_filename = filename.replace(pwd, '').lstrip('\/')

        try:
            tags_file = self.get_tags_file(filename)
        except:
            self.error(
                'Could not determine tags file to update for "%s"' % (
                    filename
                )
            )
            return

        try:
            self.debug('Start updating tags for "%s"' % filename)
            self.strip_existing_tags(tags_file, relative_filename)
            self.generate_tags(tags_file, relative_filename)
            self.debug('Tags updated for "%s"' % filename)
        except:
            self.error(
                'Failed to update tags for "%s", reason: %s' % (
                    filename, traceback.format_exc()
                )
            )

    def strip_existing_tags(self, tags_f, filename):
        with fileinput.input(files=tags_f, inplace=True, backup='.bak') as f:
            for line in f:
                if filename not in line:
                    sys.stdout.write(line)

    def generate_tags(self, tags_file, filename):
        subprocess.run([
            self.options['ctags_cmd'],
            '-f',
            tags_file,
            '-a',
            "%s" % filename
        ])

    def get_tags_file(self, filename):
        path = pathlib.Path(filename)
        possible_file = path.with_name(self.options['tags_filename'])

        self.debug('Search tags file: "%s"' % possible_file)
        if possible_file.is_file():
            return str(possible_file)

        for folder in path.parents:
            possible_file = folder.with_name(self.options['tags_filename'])
            self.debug('Search tags file: "%s"' % possible_file)
            if possible_file.is_file():
                return str(possible_file)

        raise ValueError('No tags file found in parent folders of given file')

    def debug(self, message):
        if self.options['logging']:
            self.nvim.out_write('neotags > ' + message + "\n")

    def error(self, message):
        if self.options['logging']:
            self.nvim.err_write('neotags > ' + message + "\n")
