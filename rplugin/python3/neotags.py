import neovim
import os
import fileinput
import subprocess


@neovim.plugin
class NeotagsPlugin(object):

    def __init__(self, nvim):
        self.nvim = nvim
        # TODO: Make configurable
        self.tags_filename = 'tags'
        # TODO: Make configurable
        self.ctags_cmd = 'ctags'
        # Perhaps fetch debugging settings?

    # Check whether a single command is enough as it's triggered twice.
    @neovim.autocmd(
        'BufWritePost,FileWritePost',
        pattern='*',
        eval='expand("<afile>:p")'
    )
    def update_tags_for_file(self, filename):
        self.filename = filename
        pwd = self.nvim.funcs.execute('pwd').strip()
        self.relative_filename = self.filename.replace(pwd, '').lstrip('\/')
        self.log('Start updating tags for abs: ' + self.filename)
        self.log('Start updating tags for rel: ' + self.relative_filename)

        # TODO: Add locking

        try:
            self.strip_existing_tags()
            self.generate_tags()
        except ValueError:
            self.log('No tags file found')

    def strip_existing_tags(self):
        tagsf = self.get_tags_file()
        backup = '.bak'

        file = fileinput.FileInput(files=tagsf, inplace=True, backup=backup)
        try:
            for line in file:
                if self.relative_filename not in line:
                    self.log('Keep line: ' + line)
                    print(line)
                else:
                    self.log('Remove line: ' + line)
        finally:
            file.close()
            try:
                os.unlink(tagsf + backup)
            except FileNotFoundError:
                pass
        # with fileinput.input(files=tagsf, inplace=True, backup=backup) as f:
        #     self.log('Lookup' + self.relative_filename)
        #     for line in f:
        #         self.log('Line: ' + line)
        #         if self.relative_filename not in line:
        #             self.log('Keep line')
        #             print(line)
        #         else:
        #             self.log('Remove line')

    def generate_tags(self):
        finished = subprocess.run([
            self.ctags_cmd,
            '-f',
            self.get_tags_file(),
            '-a',
            "%s" % self.relative_filename
        ])

        if finished.stderr:
            self.log('Error:' + finished.stderr)
        if finished.stdout:
            self.log('Output:' + finished.stdout)
        if finished.returncode:
            self.log('Code:' + finished.returncode)

    def get_tags_file(self):
        start_dir = os.path.dirname(self.filename)
        for dirpath, __, filenames in os.walk(start_dir, topdown=False):
            if self.tags_filename in filenames:
                return os.path.join(dirpath, self.tags_filename)

        raise ValueError('No tags file found in parent folders of given file')

    def log(self, message):
        self.nvim.out_write(message + "\n")
