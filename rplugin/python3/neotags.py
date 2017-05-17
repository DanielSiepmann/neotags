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
        # TODO: Make configurable
        self.tags_filename = 'tags'
        # TODO: Make configurable
        self.ctags_cmd = 'ctags'
        # Perhaps fetch debugging settings?

    def update_settings(self):
        try:
            self.logging = bool(self.nvim.vars['neotags_logging'])
        except neovim.api.nvim.NvimError:
            self.logging = false

    # Check whether 'FileWritePost' is necessary
    @neovim.autocmd('BufWritePost', pattern='*', eval='expand("<afile>:p")')
    def update_tags_for_file(self, filename):
        self.update_settings()

        self.log('Triggered for "%s"' % filename)

        pwd = self.nvim.funcs.execute('pwd').strip()
        relative_filename = filename.replace(pwd, '').lstrip('\/')
        tags_file = self.get_tags_file(filename)

        try:
            self.log('Start updating tags for "%s"' % filename)
            self.strip_existing_tags(tags_file, relative_filename)
            self.generate_tags(tags_file, relative_filename)
            self.log('Tags updated for "%s"' % filename)
        except:
            self.log(
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
            self.ctags_cmd,
            '-f',
            tags_file,
            '-a',
            "%s" % filename
        ])

    def get_tags_file(self, filename):
        path = pathlib.Path(filename)
        possible_file = path.with_name(self.tags_filename)

        self.log('Search tags file: "%s"' % possible_file)
        if possible_file.is_file():
            return str(possible_file)

        for folder in path.parents:
            possible_file = folder.with_name(self.tags_filename)
            self.log('Search tags file: "%s"' % possible_file)
            if possible_file.is_file():
                return str(possible_file)

        raise ValueError('No tags file found in parent folders of given file')

    def log(self, message):
        if self.logging:
            self.nvim.out_write('neotags > ' + message + "\n")
