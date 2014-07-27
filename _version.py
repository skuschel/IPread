import os.path


__version__ = 'unknown'
__version_gitsha__ = 'unknown'

__all__ = ['__version__', '__version_gitsha__']


_filedir = os.path.dirname(os.path.realpath(__file__))
_versionfile = os.path.join(_filedir, '_version.txt')
# Use Git description for __version__ if present
try:
    import subprocess as sub
    p = sub.Popen(['git', 'describe', '--tags', '--always', '--dirty'],
                  stdout=sub.PIPE,
                  stderr=sub.PIPE, cwd=_filedir)
    out, err = p.communicate()
    if not p.returncode:  # git exited without error
        # if version tag starts with 'v'
        if out[0] == 'v':
            out = out[1:]
        __version__ = out.replace('\n', '')

    p = sub.Popen(['git', 'rev-parse', 'HEAD'],
                  stdout=sub.PIPE,
                  stderr=sub.PIPE, cwd=_filedir)
    out, err = p.communicate()
    if not p.returncode:
        __version_gitsha__ = out.replace('\n', '')
        # write version string to file
        with open(_versionfile, 'w') as f:
            f.write(__version__ + '\n')
            f.write(__version_gitsha__)

except OSError as err:
    # 'git' command not found
    pass

# Alernatively read from versionfile
if __version__ == 'unknown':
    with open(_versionfile) as f:
        __version__ = f.readline().replace('\n', '')
        __version_gitsha__ = f.readline().replace('\n', '')
