#!/usr/bin/env python3

import sys, os
from pylibs.linkdot import remove_bad_symlink, make_symlink_stack, do_actions, LINKREC


HOME_PATH = os.environ['HOME']
BASE_PATH = os.path.dirname(os.path.realpath(sys.argv[0]))

def make_all_links(fake_operate):
    linkrec = os.path.join(BASE_PATH, LINKREC)
    remove_bad_symlink(linkrec)

    linkdirs = os.path.join(BASE_PATH, 'linkdirs')
    linkfiles = os.path.join(BASE_PATH, 'linkfiles')

    actions = make_symlink_stack(linkdirs, HOME_PATH)
    actions += make_symlink_stack(linkfiles, HOME_PATH, top_level=False)
    do_actions(actions, fake_operate)


def do_post_install():
    # chsh to zsh
    os.system("chsh -s /bin/zsh")

    # vim post installs
    os.system("mkdir ~/.vim/.backup")
    os.system("mkdir ~/.vim/.swap")
    os.system("mkdir ~/.vim/.undofiles")
    os.system("git clone https://github.com/gmarik/vundle.git ~/.vim/bundle/vundle")
    os.system("ln -s ~/.vim/vimrc ~/.vimrc")
    os.system("vim +PluginInstall +qall")


if __name__ == '__main__':
    fake_option = False
    make_all_links(fake_option)
    if not fake_option:
        do_post_install()
