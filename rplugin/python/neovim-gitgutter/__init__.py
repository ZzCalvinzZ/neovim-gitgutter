import neovim

@neovim.plugin
class Snake(object):
	def __init__(self, vim):
		self.vim = vim

	@neovim.command('Test', sync=True)
	def snake_start(self):
		self.vim.current.buffer[0] = 'Hi mama'
