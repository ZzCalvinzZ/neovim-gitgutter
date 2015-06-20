import neovim

class GitGutterHandler(object):
	def __init__(self, file_name=None):
		self.file_name = file_name

    def on_disk(self):
        # if the view is saved to disk
        on_disk = self.file_name() is not None
        if on_disk:
            self.git_tree = self.git_tree or git_helper.git_tree(self.view)
            self.git_dir = self.git_dir or git_helper.git_dir(self.git_tree)
            self.git_path = self.git_path or git_helper.git_file_path(
                self.view, self.git_tree
            )
        return on_disk

	#expect each line as a dict like {number: 2, type: add}
	def show_signs(modified_lines, buffer):
		for line in modified_lines:
			if line.type == 'inserted':
				self.place_add_sign(line.number, buffer)
			if line.type == 'modified':
				self.place_modified_sign(line.number, buffer)
			if line.type == 'deleted':
				self.place_deleted_sign(line.number, buffer)

	def process_diff(self, diff_str):
		inserted = []
		modified = []
		deleted = []
		hunk_re = '^@@ \-(\d+),?(\d*) \+(\d+),?(\d*) @@'
		hunks = re.finditer(hunk_re, diff_str, re.MULTILINE)
		for hunk in hunks:
			start = int(hunk.group(3))
			old_size = int(hunk.group(2) or 1)
			new_size = int(hunk.group(4) or 1)
			if not old_size:
				inserted += range(start, start + new_size)
			elif not new_size:
				deleted += [start + 1]
			else:
				modified += range(start, start + new_size)
		return (inserted, modified, deleted)

	 def diff(self):
        if self.on_disk() and self.git_path:
            self.update_git_file()
            self.update_buf_file()
            args = [
                self.git_binary_path, 'diff', '-U0', '--no-color', '--no-index',
                self.ignore_whitespace,
                self.patience_switch,
                self.git_temp_file.name,
                self.buf_temp_file.name,
            ]
            args = list(filter(None, args))  # Remove empty args
            results = self.run_command(args)
            encoding = self._get_view_encoding()
            try:
                decoded_results = results.decode(encoding.replace(' ', ''))
            except UnicodeError:
                try:
                    decoded_results = results.decode("utf-8")
                except UnicodeDecodeError:
                    decoded_results = ""
            except LookupError:
                try:
                    decoded_results = codecs.decode(results)
                except UnicodeDecodeError:
                    decoded_results = ""
            return self.process_diff(decoded_results)
        else:
            return ([], [], [])

	def _place_sign(self, sign=None, line_no=None, buffer=None):
		self.vim.command('sign place {line} line={line} name={sign} file={file}'.format(line=line_no, sign=sign, file=buffer.name))

	def unplace_sign(self, line_no=None, buffer=None):
		self.vim.command('sign place {line} file={file}'.format(line=line_no, file=buffer.name))

	def place_add_sign(self, line_no=None, buffer=None):
		self._place_sign(sign="line_added", line_no=line_no, buffer=buffer)

	def place_modified_sign(self, line_no=None, buffer=None):
		self._place_sign(sign="line_modified", line_no=line_no, buffer=buffer)

	def place_remove_sign(self, line_no=None, buffer=None):
		self._place_sign(sign="line_removed", line_no=line_no, buffer=buffer)

@neovim.plugin
class GitGutter(object):
	def __init__(self, vim):
		self.vim = vim

	@neovim.autocmd('VimEnter')
	def init_signs(self):
		# define sign characters
		self.vim.command('sign define line_added text=+ texthl=lineAdded')
		self.vim.command('sign define line_modified text=~ texthl=lineModified')
		self.vim.command('sign define line_removed text=_ texthl=lineRemoved')
		#set coloring on signs
		self.vim.command('highlight lineAdded guifg=#009900 guibg=NONE ctermfg=2 ctermbg=NONE')
		self.vim.command('highlight lineModified guifg=#bbbb00 guibg=NONE ctermfg=3 ctermbg=NONE')
		self.vim.command('highlight lineRemoved guifg=#ff2222 guibg=NONE ctermfg=1 ctermbg=NONE')

	@neovim.autocmd('BufReadPost')
	@neovim.autocmd('BufWritePost')
	@neovim.autocmd('FileReadPost')
	@neovim.autocmd('FileWritePost')
	@neovim.autocmd('BufEnter')
	def run(self):
		pass
