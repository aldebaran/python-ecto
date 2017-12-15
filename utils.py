import fnmatch
import os
import shutil
import subprocess

from distutils import log

try:
    WindowsError
except NameError:
    WindowsError = None

def filter_match(name, patterns):
    for pattern in patterns:
        if pattern is None:
            continue
        if fnmatch.fnmatch(name, pattern):
            return True
    return False

def check_call(arg):
    subprocess.check_call(arg)

def get_version_from_tag():
    cmd = "git describe --tags --dirty"
    git_description = subprocess.check_output(cmd.split())
    # Will return the closest tag: e.g. 0.1.0
    # then add -X-SHA-1 where X is the number of commit
    # between HEAD and that tag, SHA--1 is the current head SHA-1
    # e.g: 0.1.0-10-g48b85
    # If HEAD is on the tag, nothing is added
    # Finally, it adds -dirty if changes are not commited
    # e.g: 0.0.1-10-g48b85f5-dirty

    git_description = git_description.split('\n')[0].split("-")
    version = git_description[0]
    if len(git_description) >= 3:
        # There is a number of commits and a SHA-1
        version += "-" + git_description[1]
    if git_description[-1] == "dirty":
        # The project is modified
        version += "-dev"
    return version

def copyfile(src, dst, force=True, vars=None):
    if vars is not None:
        src = src.format(**vars)
        dst = dst.format(**vars)

    if not os.path.exists(src) and not force:
        log.info("**Skiping copy file %s to %s. Source does not exists." % (src, dst))
        return

    log.info("Copying file %s to %s." % (src, dst))

    shutil.copy2(src, dst)

    return dst

def copydir(src, dst, filter=None, ignore=None, force=True,
    recursive=True, vars=None):

    if vars is not None:
        src = src.format(**vars)
        dst = dst.format(**vars)
        if filter is not None:
            for i in range(len(filter)):
                filter[i] = filter[i].format(**vars)
        if ignore is not None:
            for i in range(len(ignore)):
                ignore[i] = ignore[i].format(**vars)

    if not os.path.exists(src):
        log.info("**Skiping copy tree %s to %s. Source does not exists. filter=%s. ignore=%s." % \
            (src, dst, filter, ignore))
        return []

    log.info("Copying tree %s to %s. filter=%s. ignore=%s." % \
        (src, dst, filter, ignore))

    names = os.listdir(src)

    results = []
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                if recursive:
                    results.extend(copydir(srcname, dstname, filter, ignore, force, recursive, vars))
            else:
                if (filter is not None and not filter_match(name, filter)) or \
                    (ignore is not None and filter_match(name, ignore)):
                    continue
                if not os.path.exists(dst):
                    os.makedirs(dst)
                results.append(copyfile(srcname, dstname, True, vars))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error as err:
            errors.extend(err.args[0])
        except EnvironmentError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        if os.path.exists(dst):
            shutil.copystat(src, dst)
    except OSError as why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise EnvironmentError(errors)
    return results

if __name__=="__main__":
    get_version_from_tag()