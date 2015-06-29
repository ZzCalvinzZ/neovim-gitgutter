# -*- coding: utf-8 -*-

import os
import subprocess
import re
import codecs
import tempfile
import git_helper

import neovim

class GitGutterHandler(object):
	def __init__(self, buffer,vim=None):
		self.vim = vim
		self.buffer = buffer
		self.file_name = buffer.name
		self.git_tree = None
		self.git_dir = None
		self.git_path = None
		self.git_binary_path = 'git'

		#settings to add in support for later
		self.show_untracked = ''
		self.show_status = ''


	def _get_view_encoding(self):
		pattern = re.compile(r'.+\((.*)\)')
		encoding = self.buffer.options['fileencoding']

		if pattern.match(encoding):
			encoding = pattern.sub(r'\1', encoding)

		encoding = encoding.replace('with BOM', '')
		encoding = encoding.replace('Windows', 'cp')
		encoding = encoding.replace('-', '_')
		encoding = encoding.replace(' ', '')

		return encoding

	def on_disk(self):
		# if the view is saved to disk
		on_disk = self.file_name is not None
		if on_disk:
			self.git_tree = self.git_tree or git_helper.git_tree(self.file_name)
			self.git_dir = self.git_dir or git_helper.git_dir(self.git_tree)
			self.git_path = self.git_path or git_helper.git_file_path(
				self.file_name, self.git_tree
			)
		return on_disk

	def get_git_contents(self):
		#temp git file args
		args = [
			self.git_binary_path,
			'--git-dir=' + self.git_dir,
			'--work-tree=' + self.git_tree,
			'show',
			'HEAD:' + self.git_path,
		]

		git_contents = self.run_command(args)
		git_contents = git_contents.replace(b'\r\n', b'\n')
		return git_contents.replace(b'\r', b'\n')

	def get_buf_contents(self):
		return "\n".join(self.buffer[:])

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

			git_contents = self.get_git_contents()
			buf_contents = self.get_buf_contents()

			with tempfile.NamedTemporaryFile() as git_temp, tempfile.NamedTemporaryFile() as buf_temp:
				git_temp.write(git_contents)
				buf_temp.write(buf_contents)

				args = ['git', 'diff', '-U0', '--no-color', '--no-index', git_temp.name, buf_temp.name]
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

	def run_command(self, args):
		startupinfo = None
		if os.name == 'nt':
			startupinfo = subprocess.STARTUPINFO()
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
		proc = subprocess.Popen(args, stdout=subprocess.PIPE,
								startupinfo=startupinfo, stderr=subprocess.PIPE)
		err = proc.stderr.read()
		if not err == '':
			raise Exception(err)
		return proc.stdout.read()

	#expect each line as a dict like {number: 2, type: add}
	def show_signs(modified_lines, buffer):
		for line in modified_lines:
			if line.type == 'inserted':
				self.place_add_sign(line.number, buffer)
			if line.type == 'modified':
				self.place_modified_sign(line.number, buffer)
			if line.type == 'deleted':
				self.place_deleted_sign(line.number, buffer)

	def _place_sign(self, sign=None, line_no=None):
		self.vim.command('sign place {line} line={line} name={sign} file={file}'.format(line=line_no, sign=sign, file=self.buffer.name))

	def unplace_sign(self, line_no=None):
		self.vim.command('sign place {line} file={file}'.format(line=line_no, file=self.buffer.name))

	def place_add_sign(self, line_no=None):
		self._place_sign(sign="line_added", line_no=line_no)

	def place_modified_sign(self, line_no=None):
		self._place_sign(sign="line_modified", line_no=line_no)

	def place_remove_sign(self, line_no=None):
		self._place_sign(sign="line_removed", line_no=line_no)

	def place_remove_above_sign(self, line_no=None):
		self._place_sign(sign="line_above_removed", line_no=line_no)

@neovim.plugin
class GitGutter(object):
	def __init__(self, vim):
		self.vim = vim

	@neovim.autocmd('VimEnter')
	def init_signs(self):
		# define sign characters
		self.vim.command('sign define line_added text=+ texthl=lineAdded')
		self.vim.command(u'sign define line_modified text=■ texthl=lineModified')
		self.vim.command('sign define line_removed text=ʌ texthl=lineRemoved')
		self.vim.command('sign define line_above_removed text=v texthl=lineAboveRemoved')
		#set coloring on signs
		self.vim.command('highlight lineAdded guifg=#009900 guibg=NONE ctermfg=2 ctermbg=NONE')
		self.vim.command('highlight lineModified guifg=#bbbb00 guibg=NONE ctermfg=3 ctermbg=NONE')
		self.vim.command('highlight lineRemoved guifg=#ff2222 guibg=NONE ctermfg=1 ctermbg=NONE')
		self.vim.command('highlight lineAboveRemoved guifg=#ff2222 guibg=NONE ctermfg=1 ctermbg=NONE')

	#@neovim.autocmd('BufReadPost')
	#@neovim.autocmd('BufWritePost')
	#@neovim.autocmd('FileReadPost')
	#@neovim.autocmd('FileWritePost')
	#@neovim.autocmd('BufEnter')
	#def run(self):
		#pass

	@neovim.command('Test', sync=True)
	def test(self):
		if self.vim.current.buffer.name:
			gutter = GitGutterHandler(self.vim.current.buffer, vim=self.vim)
			inserted, modified, deleted = gutter.diff()
			for line in inserted:
				gutter.place_add_sign(line)
			for line in modified:
				gutter.place_modified_sign(line)
			for line in deleted:
				gutter.place_remove_sign(line)
				if line > 1:
					gutter.place_remove_above_sign(line - 1)
