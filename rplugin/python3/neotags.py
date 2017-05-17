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

    # Check whether 'FileWritePost' is necessary
    @neovim.autocmd('BufWritePost', pattern='*', eval='expand("<afile>:p")')
    def update_tags_for_file(self, filename):
        self.log('Triggered for "%s"' % filename)

        pwd = self.nvim.funcs.execute('pwd').strip()
        relative_filename = filename.replace(pwd, '').lstrip('\/')
        tags_file = self.get_tags_file(filename)

        try:
            self.log('Start updating tags for "%s"' % filename)
            self.strip_existing_tags(tags_file, relative_filename)
            self.generate_tags(tags_file, relative_filename)
            self.log('Tags for file "%s"' % filename)
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

        self.log('Test: ' + str(path.with_name(self.tags_filename)))
        if path.with_name(self.tags_filename).is_file():
            return str(path.with_name(self.tags_filename))

        for folder in path.parents:
            self.log('Test: ' + str(folder.with_name(self.tags_filename)))
            if folder.with_name(self.tags_filename).is_file():
                return str(folder.with_name(self.tags_filename))

        raise ValueError('No tags file found in parent folders of given file')

    def log(self, message):
        self.nvim.out_write('neotags > ' + message + "\n")
