import os


def git_file_path(file_name, git_path):
	if not git_path:
		return False
	full_file_path = os.path.realpath(file_name)
	git_path_to_file = full_file_path.replace(git_path, '').replace('\\', '/')
	if git_path_to_file[0] == '/':
		git_path_to_file = git_path_to_file[1:]
	return git_path_to_file


def git_root(directory):
	if os.path.exists(os.path.join(directory, '.git')):
		return directory
	else:
		parent = os.path.realpath(os.path.join(directory, os.path.pardir))
		if parent == directory:
			# we have reached root dir
			return False
		else:
			return git_root(parent)


def git_tree(file_name):
	full_file_path = file_name
	file_parent_dir = os.path.realpath(os.path.dirname(full_file_path))
	return git_root(file_parent_dir)


def git_dir(directory):
	if not directory:
		return False
	pre_git_dir = os.path.join(directory, '.git')
	if os.path.isfile(pre_git_dir):
		submodule_path = ''
		with open(pre_git_dir) as submodule_git_file:
			submodule_path = submodule_git_file.read()
			submodule_path = os.path.join('..', submodule_path.split()[1])

			submodule_git_dir = os.path.abspath(
				os.path.join(pre_git_dir, submodule_path))

		return submodule_git_dir
	else:
		return pre_git_dir
