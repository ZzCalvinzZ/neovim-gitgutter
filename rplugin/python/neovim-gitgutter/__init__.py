import neovim

@neovim.plugin
class SignHandler(object):
	def __init__(self, vim):
		self.vim = vim

	@neovim.autocmd('VimEnter')
	def _init_signs(self):
		# define sign characters
		self.vim.command('sign define line_added text=+ texthl=lineAdded')
		self.vim.command('sign define line_modified text=~ texthl=lineModified')
		self.vim.command('sign define line_removed text=_ texthl=lineRemoved')
		#set coloring on signs
		self.vim.command('highlight lineAdded guifg=#009900 guibg=NONE ctermfg=2 ctermbg=NONE')
		self.vim.command('highlight lineModified guifg=#bbbb00 guibg=NONE ctermfg=3 ctermbg=NONE')
		self.vim.command('highlight lineRemoved guifg=#ff2222 guibg=NONE ctermfg=1 ctermbg=NONE')

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

	@neovim.command('Test', nargs=1)
	def test(self, args):
		sign = args[0]
		self.vim.command('echom "{0}"'.format(sign))
		if sign == 'add':
			self.vim.command('echom "weee"')
			self.place_add_sign(line_no=self.vim.current.window.cursor[0], buffer=self.vim.current.buffer)
			self.vim.command('echom "bloody"')
		else:
			pass
