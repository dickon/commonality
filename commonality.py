#! /usr/bin/env python

"""Quick and dirty"""

from sys import argv, stderr, stdout
from os import chdir, listdir
from os.path import join, isdir, split
from time import asctime

try:
    from subprocess import check_output
except ImportError:
    # from https://gist.github.com/1027906
    import subprocess
    def check_output(*popenargs, **kwargs):
        r"""Run command with arguments and return its output as a byte string.

        Backported from Python 2.7 as it's implemented as pure python on stdlib.

        >>> check_output(['/usr/bin/python', '--version'])
        Python 2.6.2
        """
        process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            error = subprocess.CalledProcessError(retcode, cmd)
            error.output = output
            raise error
        return output

if len(argv) not in [3,4]:
    print >>stderr, 'USAGE: commonality git_repos_parent_directory_or_git_directory branch1 [branch2]'
    print >>stderr
    print >>stderr, 'print a list of commits that vary between the two branches'
    print >>stderr, 'branch2 defaults to master'
    exit(1)

target = argv[2]
base = argv[3] if len(argv) >= 4 else 'master'
parent = argv[1]

print 'differences between', base, 'and', target, 'in all git repos in', parent
print

def isgit(directory):
    return isdir(join(directory, '.git')) or directory.endswith('.git')

if isgit(parent):
    workds = [parent]
else:
    workds = [join(parent, out) for out in sorted(listdir(parent))]

for fout in workds:
    if not isgit(fout):
        continue
    out = split(fout)[1]
    chdir(fout)
    branches = check_output(['git', 'branch', '-a']).split()
    if target not in branches:
        continue
    common = check_output(['git', 'merge-base', target, 'master']).split()[0]
    identical = True
    for primary, secondary  in [(base, target), (target, base)]:
        text = primary.split('/')[-1].upper() + '-ONLY'
        altstuff = check_output(['git', 'log', common+'..'+secondary])
        pristuff = check_output(['git', 'log', common+'..'+secondary])
        for change in check_output(['git', 'log', '--format=%H', 
                                    common+'..'+primary]).split():
            if '(cherry picked from commit '+change+')' in altstuff:
                status = 'CHERRYPICKED'
            else:
                status = text
                identical = False
            stuff = [check_output(['git', 'log', '--format='+fmt, change]).splitlines()[0] for fmt in ['%aD', '%aN', '%s']]
            print ('%20s' % status), out, change[:8], ' '.join(stuff)
    if identical:
        print ' '*20, out, 'IDENTICAL!'
    stdout.flush()

print 'finished generating', asctime()
