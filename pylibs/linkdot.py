#!/usr/bin/env python3

import os, sys

from termcolor import colored, cprint

LINKREC='.created-links'

def write_linkrec(src, dst):
    linkrec = LINKREC
    if os.path.exists(linkrec):
        with open(linkrec, 'r') as f:
            all_link = f.readlines()
    else:
        all_link = []
    all_link.append('{0} -> {1}'.format(src, dst))
    all_link = set(all_link)
    print(all_link)

    #with open(linkrec, 'w') as f:
    #   f.writelines(all_link)

def do_actions(actions, fake_operate=True):
    def rm(file):
        if fake_operate:
            print('rm ', file)
        else:
            os.system('rm -rf {0}'.format(file))

    def link(src, dst):
        if fake_operate:
            print('link ', dst, src)
        else:
            parent_dir = os.path.dirname(os.path.realpath(src))
            os.system('mkdir -p {0}'.format(parent_dir))
            os.system('ln -s {0} {1}'.format(dst, src))
            write_linkrec(src, dst)

    def linkdir(src, dst):
        if fake_operate:
            print('linkdir ', dst, src)
        else:
            parent_dir = os.path.dirname(os.path.realpath(src))
            os.system('mkdir -p {0}'.format(parent_dir))
            os.system('ln -s {0} {1}'.format(dst, src))
            write_linkrec(src, dst)

    local_mappings = locals()
    for action in actions:
        cmd_str = action[0].replace('-', '_')
        if cmd_str not in local_mappings:
            cprint('unknown cmd: {0}'.format(cmd_str), color='red')
            continue
        local_mappings[cmd_str](*action[1:])


def remove_broken_symlinks_stack(created_symlinks):
    results = []
    for src, dst in created_symlinks.items():
        if os.path.lexists(src) \
                and os.path.islink(src) \
                and os.path.realpath(src) == dst \
                and not os.path.lexists(dst):
            results.append(('rm', src))
    return results


def make_symlink_stack(origdir, dstdir, top_level=True):
    results = []
    if dstdir.endswith('/'):
        dstdir = dstdir[:-1]
    if origdir.endswith('/'):
        origdir = origdir[:-1]

    if top_level:
        for dirpath, dirnames, filenames in os.walk(origdir):
            for dirname in dirnames:
                new_name = dirname
                if not dirname.startswith('.'):
                    new_name = '.' + new_name
                dirname = os.path.join(dirpath, dirname)
                new_name = os.path.join(dstdir, new_name)
                results.append(('linkdir', new_name, dirname))
            for filename in filenames:
                new_name = filename
                if not filename.startswith('.'):
                    new_name = '.' + new_name
                filename = os.path.join(dirpath, filename)
                new_name = os.path.join(dstdir, new_name)
                results.append(('link', new_name, filename))
            break
    else:
        for dirpath, dirnames, filenames in os.walk(origdir):
            for filename in filenames:
                new_name = filename
                if not filename.startswith('.'):
                    new_name = '.' + new_name
                filename = os.path.join(dirpath, filename)
                new_name = os.path.join(dirpath[len(origdir)+1:], new_name)
                new_name = os.path.join(dstdir, new_name)
                results.append(('link', new_name, filename))


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
