#!/usr/bin/env python3

import os, sys

from termcolor import colored, cprint
from datetime import datetime

LINKREC='.created-links'

def write_linkrec(linkname, target):
    linkrec = LINKREC
    if os.path.exists(linkrec):
        with open(linkrec, 'r') as f:
            all_link = f.readlines()
    else:
        all_link = []
    all_link.append('{0} -> {1}\n'.format(linkname, target))
    all_link = set(all_link)

    with open(linkrec, 'w') as f:
       f.writelines(all_link)

def do_actions(actions, fake_operate=True):
    def rm(file):
        if fake_operate:
            print('rm ', file)
        else:
            os.system('rm -rf {0}'.format(file))

    def link(linkname, target):
        parent_dir = os.path.dirname(os.path.realpath(linkname))
        if fake_operate:
            if os.path.realpath(linkname) == target:
                return False

            if os.path.lexists(linkname):
                postfix = str(datetime.timestamp(datetime.now()))
                print('mv {0} {1}'.format(linkname, linkname + '.' + postfix))

            print('mkdir -p {0}'.format(parent_dir))
            print('ln -s {0} {1}'.format(target, linkname))
        else:
            if os.path.realpath(linkname) == target:
                return False

            if os.path.lexists(linkname):
                postfix = str(datetime.timestamp(datetime.now()))
                os.system('mv {0} {1}'.format(linkname, linkname + '.' + postfix))

            os.system('mkdir -p {0}'.format(parent_dir))
            os.system('ln -s {0} {1}'.format(target, linkname))
            write_linkrec(linkname, target)

    def linkdir(linkname, target):
        parent_dir = os.path.dirname(os.path.realpath(linkname))
        if fake_operate:
            if os.path.realpath(linkname) == target:
                return False

            if os.path.lexists(linkname):
                postfix = str(datetime.timestamp(datetime.now()))
                print('mv {0} {1}'.format(linkname, linkname + '.' + postfix))

            print('mkdir -p {0}'.format(parent_dir))
            print('ln -s {0} {1}'.format(target, linkname))
        else:
            if os.path.realpath(linkname) == target:
                return False

            if os.path.lexists(linkname):
                postfix = str(datetime.timestamp(datetime.now()))
                os.system('mv {0} {1}'.format(linkname, linkname + '.' + postfix))

            os.system('mkdir -p {0}'.format(parent_dir))
            os.system('ln -s {0} {1}'.format(target, linkname))
            write_linkrec(linkname, target)

    local_mappings = locals()
    for action in actions:
        cmd_str = action[0].replace('-', '_')
        if cmd_str not in local_mappings:
            cprint('unknown cmd: {0}'.format(cmd_str), color='red')
            continue
        local_mappings[cmd_str](*action[1:])


def remove_broken_symlinks_stack(created_symlinks):
    results = []
    for linkname, dst in created_symlinks.items():
        if os.path.lexists(linkname) \
                and os.path.islink(linkname) \
                and os.path.realpath(linkname) == dst \
                and not os.path.lexists(dst):
            results.append(('rm', linkname))
    return results


def make_symlink_stack(origdir, dstdir, top_level=True):
    results = []
    if dstdir.endswith('/'):
        dstdir = dstdir[:-1]
    if origdir.endswith('/'):
        origdir = origdir[:-1]

    if top_level:
        for dirpath, dirnames, targets in os.walk(origdir):
            for dirname in dirnames:
                linkname = dirname
                if not dirname.startswith('.'):
                    linkname = '.' + linkname
                dirname = os.path.join(dirpath, dirname)
                linkname = os.path.join(dstdir, linkname)
                results.append(('linkdir', linkname, dirname))
            for target in targets:
                linkname = target
                if not target.startswith('.'):
                    linkname = '.' + linkname
                target = os.path.join(dirpath, target)
                linkname = os.path.join(dstdir, linkname)
                results.append(('link', linkname, target))
            break
    else:
        for dirpath, dirnames, targets in os.walk(origdir):
            for target in targets:
                linkname = target
                target = os.path.join(dirpath, target)
                linkdir_name = dirpath[len(origdir)+1:]
                if not linkdir_name.startswith('.'):
                    linkdir_name = '.' + linkdir_name
                linkname = os.path.join(linkdir_name, linkname)
                linkname = os.path.join(dstdir, linkname)

                results.append(('link', linkname, target))


    return results


def remove_bad_symlink(linkrec):
    # 删除损坏的链接文件
    if os.path.exists(linkrec):
        with open(linkrec) as f:
            created_links = dict((line.strip().split(' -> ')) for line in f.readlines())
        remove_actions = remove_broken_symlinks_stack(created_links)
        do_actions(remove_actions)

if __name__ == '__main__':
    LINKDOT_DIRNAME = ''
    HOME_PATH = os.environ['HOME']
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
    LINKDOT_PATH = os.path.join(BASE_PATH, LINKDOT_DIRNAME)

    linkrec = os.path.join(BASE_PATH, LINKREC)
    remove_bad_symlink(linkrec)
    actions = make_symlink_stack(LINKDOT_PATH, HOME_PATH)
    do_actions(actions)
    actions = make_symlink_stack(LINKDOT_PATH, HOME_PATH, top_level=False)
