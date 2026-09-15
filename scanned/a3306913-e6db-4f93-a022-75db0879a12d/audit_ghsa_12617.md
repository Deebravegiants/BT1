# [H] jcvi vulnerable to Configuration Injection due to unsanitized user input 

## Summary
Severity: High
Advisory: GHSA-x49m-3cw7-gq5q
CVE: CVE-2023-35932
CWE: CWE-1284, CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2023-06-23
Source: https://github.com/advisories/GHSA-x49m-3cw7-gq5q
Type: github-advisory

## Affected
- PyPI: `jcvi` — affected >=0

## Details
### Summary
A configuration injection happens when user input is considered by the application in an unsanitized format and can reach the configuration file. A malicious user may craft a special payload that may lead to a command injection.

### PoC

The vulnerable code snippet is [/jcvi/apps/base.py#LL2227C1-L2228C41](https://github.com/tanghaibao/jcvi/blob/cede6c65c8e7603cb266bc3395ac8f915ea9eac7/jcvi/apps/base.py#LL2227C1-L2228C41). Under some circumstances a user input is retrieved and stored within the `fullpath` variable which reaches the configuration file `~/.jcvirc`.

```python
        fullpath = input(msg).strip()
        config.set(PATH, name, fullpath)
```

I ripped a part of the codebase into a runnable PoC as follows. All the PoC does is call the `getpath()` function under some circumstances.

```python
from configparser import (
    ConfigParser,
    RawConfigParser,
    NoOptionError,
    NoSectionError,
    ParsingError,
)

import errno
import os
import sys
import os.path as op
import shutil
import signal
import sys
import logging


def is_exe(fpath):
    return op.isfile(fpath) and os.access(fpath, os.X_OK)


def which(program):
    """
    Emulates the unix which command.

    >>> which("cat")
    "/bin/cat"
    >>> which("nosuchprogram")
    """
    fpath, fname = op.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = op.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def getpath(cmd, name=None, url=None, cfg="~/.jcvirc", warn="exit"):
    """
    Get install locations of common binaries
    First, check ~/.jcvirc file to get the full path
    If not present, ask on the console and store
    """
    p = which(cmd)  # if in PATH, just returns it
    if p:
        return p

    PATH = "Path"
    config = RawConfigParser()
    cfg = op.expanduser(cfg)
    changed = False
    if op.exists(cfg):
        config.read(cfg)

    assert name is not None, "Need a program name"

    try:
        fullpath = config.get(PATH, name)
    except NoSectionError:
        config.add_section(PATH)
        changed = True

    try:
        fullpath = config.get(PATH, name)
    except NoOptionError:
        msg = "=== Configure path for {0} ===\n".format(name, cfg)
        if url:
            msg += "URL: {0}\n".format(url)
        msg += "[Directory that contains `{0}`]: ".format(cmd)
        fullpath = input(msg).strip()
        config.set(PATH, name, fullpath)
        changed = True

    path = op.join(op.expanduser(fullpath), cmd)
    if warn == "exit":
        try:
            assert is_exe(path), "***ERROR: Cannot execute binary `{0}`. ".format(path)
        except AssertionError as e:
            sys.exit("{0!s}Please verify and rerun.".format(e))

    if changed:
        configfile = open(cfg, "w")
        config.write(configfile)
        logging.debug("Configuration written to `{0}`.".format(cfg))

    return path


# Call to getpath
path = getpath("not-part-of-path", name="CLUSTALW2", warn="warn")
print(path)

```

To run the PoC, you need to remove the config file `~/.jcvirc` to emulate the first run, 

```bash
# Run the PoC with the payload
echo -e "e\rvvvvvvvv = zzzzzzzz\n" | python3 poc.py
```

![image](https://user-images.githubusercontent.com/13036531/247852364-f8a384a3-fc62-41ca-b467-877d197ac6ff.png)

You can notice the random key/value characters `vvvvvvvv = zzzzzzzz` were successfully injected.

### Impact

The impact of a configuration injection may vary. Under some conditions, it may lead to command injection if there is for instance shell code execution from the configuration file values.

## References
- https://github.com/tanghaibao/jcvi/security/advisories/GHSA-x49m-3cw7-gq5q
- https://nvd.nist.gov/vuln/detail/CVE-2023-35932
- https://github.com/tanghaibao/jcvi
- https://github.com/tanghaibao/jcvi/blob/cede6c65c8e7603cb266bc3395ac8f915ea9eac7/jcvi/apps/base.py#LL2227C1-L2228C41
