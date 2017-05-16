import neovim
import os
import sys
import fileinput
import subprocess
import locket


@neovim.plugin
class NeotagsPlugin(object):

    def __init__(self, nvim):
        self.nvim = nvim
        # TODO: Make configurable
        self.tags_filename = 'tags'
        # TODO: Make configurable
        self.ctags_cmd = 'ctags'
        # Perhaps fetch debugging settings?

    # Check whether 'FileWritePost' is necessary
    @neovim.autocmd('BufWritePost', pattern='*', eval='expand("<afile>:p")')
    def update_tags_for_file(self, filename):
        self.filename = filename
        pwd = self.nvim.funcs.execute('pwd').strip()
        self.relative_filename = self.filename.replace(pwd, '').lstrip('\/')

        try:
            with locket.lock_file(self.get_tags_file() + '.lock'):
                self.log('Start updating tags')
                self.strip_existing_tags()
                self.generate_tags()
                self.log('Tags for file: "%s"' % self.relative_filename)
        except ValueError:
            self.log('No tags file found')

    def strip_existing_tags(self):
        with fileinput.input(files=self.get_tags_file(), inplace=True, backup='.bak') as f:
            for line in f:
                if self.relative_filename not in line:
                    sys.stdout.write(line)

    def generate_tags(self):
        subprocess.run([
            self.ctags_cmd,
            '-f',
            self.get_tags_file(),
            '-a',
            "%s" % self.relative_filename
        ])

    def get_tags_file(self):
        start_dir = os.path.dirname(self.filename)
        self.log('tst: ' + start_dir)
        # TODO: Why does it find the file?
        for dirpath, __, filenames in os.walk(start_dir, topdown=False):
            if self.tags_filename in filenames:
                return os.path.join(dirpath, self.tags_filename)

        raise ValueError('No tags file found in parent folders of given file')

    def log(self, message):
        self.nvim.out_write(message + "\n")
