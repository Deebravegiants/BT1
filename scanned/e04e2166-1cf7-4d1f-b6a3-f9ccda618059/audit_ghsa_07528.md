# [M] OnionShare follows symlinks in shared directories, allowing unintended disclosure of local files

## Summary
Severity: Medium
Advisory: GHSA-22p9-r2f5-22mf
CVE: CVE-2026-54706
CWE: CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-22p9-r2f5-22mf
Type: github-advisory

## Affected
- PyPI: `onionshare-cli` — affected >=0 <2.6.4

## Details
### Summary
OnionShare CLI/Desktop 2.6.3 can follow symbolic links inside a selected Share or Website directory and serve the symlink target rather than limiting access to files physically contained in the selected directory. If a user shares a directory that contains attacker-supplied or otherwise untrusted symlinks, a remote recipient with access to the OnionShare service can read arbitrary local files readable by the OnionShare process that the symlink points to.

This affects the shipped `onionshare-cli` Python package and the desktop application because both call the same `onionshare_cli.web` file-indexing and streaming code.

### Details
Tested repository: `https://github.com/onionshare/onionshare` at commit `8cc75e1d7e88bd31f7276733449d412bf71c8999`.

Affected product evidence:
- `cli/pyproject.toml` declares `onionshare_cli` version `2.6.3`.
- `desktop/pyproject.toml` declares `onionshare` version `2.6.3` and depends on `onionshare_cli` from `../cli`.
- `cli/setup.py` publishes `onionshare-cli` and includes `onionshare_cli.web` plus templates/static resources.
- `desktop/setup.py` publishes `onionshare` and exposes both `onionshare` and `onionshare-cli` console scripts.

Reachable default/common paths:
- CLI share mode is the default mode when no `--receive`, `--website`, or `--chat` flag is provided (`cli/onionshare_cli/__init__.py:234-241`) and accepts filesystem paths from CLI arguments (`cli/onionshare_cli/__init__.py:184-189`).
- CLI website mode is exposed through `--website` (`cli/onionshare_cli/__init__.py:55-59`).
- Desktop Website mode calls `self.web.website_mode.set_file_info(self.filenames)` before starting (`desktop/onionshare/tab/mode/website_mode/__init__.py:281-287`). Desktop Share mode calls `self.mode.web.share_mode.set_file_info(...)` before serving (`desktop/onionshare/tab/mode/share_mode/threads.py:42-49`).
- Documentation describes Website mode as selecting files/folders and serving them over OnionShare (`docs/source/features.rst:109-115`).

Root cause:
- `SendBaseModeWeb.set_file_info()` expands a single selected directory into immediate children and records `os.path.isfile()` entries without rejecting symlinks (`cli/onionshare_cli/web/send_base_mode.py:73-80`, `cli/onionshare_cli/web/send_base_mode.py:100-130`). On POSIX, `os.path.isfile()` follows a symlink to a regular file.
- Website mode serves any mapped file path through `stream_individual_file()` (`cli/onionshare_cli/web/website_mode.py:71-97`). `stream_individual_file()` opens the mapped filesystem path directly (`cli/onionshare_cli/web/send_base_mode.py:199-313`, especially `open(file_to_download, "rb")` at line 237).
- Share mode default `/download` can include a symlink target when a single selected folder is expanded into root entries and `ZipWriter.add_file()` calls `self.z.write(filename, ...)` without rejecting symlinks (`cli/onionshare_cli/web/share_mode.py:473-539`, `cli/onionshare_cli/web/share_mode.py:574-580`).
- Share mode with `--no-autostop-sharing` enables individual file downloads (`cli/onionshare_cli/web/share_mode.py:122-125`) and reaches the same direct streaming sink (`cli/onionshare_cli/web/share_mode.py:430-447`).
- A partial mitigation exists only for recursive ZIP directory traversal: `ZipWriter.add_dir()` skips `os.path.islink(full_filename)` (`cli/onionshare_cli/web/share_mode.py:582-600`). That mitigation does not cover Website mode, Share individual downloads, or Share ZIP generation for root-level symlinks after the single-folder expansion path.

False-positive screening performed:
- URL path traversal without a mapped entry returned 404; the issue is not raw `../` traversal but symlink following after a selected directory has been indexed.
- Jinja/template escaping and CSP do not mitigate this because the sink is file read/streaming.
- Share mode has a symlink skip in recursive ZIP addition, but local PoC confirmed sibling paths still dereference symlinks.
- The default non-public onion service requires the recipient to know the onion address and private key unless the user opts into public mode; this limits exposure but does not prevent disclosure to an authorized recipient or to anyone with the URL/key.

Affected versions / patched versions:
- Affected versions: unknown; confirmed in version `2.6.3` at commit `8cc75e1d7e88bd31f7276733449d412bf71c8999`. Earlier versions were not tested during this audit.
- Patched versions: 2.6.4

Severity:

- Rationale: `AV:N` because the file is exposed over the OnionShare HTTP service; `AC:H` because exploitation requires the victim to share a directory containing an attacker-influenced or untrusted symlink to a sensitive local file; `PR:L` because the attacker generally needs the OnionShare URL/private key unless the user intentionally runs public mode; `UI:R` because the OnionShare user must select/start sharing the affected directory; `S:U` because the same local process reads and serves the file; `C:H` because the symlink can point at high-value readable local secrets; `I:N/A:N` because the confirmed impact is unintended read/disclosure.

### PoC
The following safe local proof uses only temporary files and Flask's local test client. In this audit environment, several runtime dependencies were absent (`waitress`, `flask_compress`, `flask_socketio`, `unidecode`, `stem`, `qrcode`), so the harness stubbed those imports while executing the real `send_base_mode`, `website_mode`, and `share_mode` vulnerable code paths. No external network traffic was sent and no real secrets were read.

Maintainer reproduction from a clean checkout with normal dependencies can omit the import stubs and run the same object/test-client setup, or can start OnionShare locally with a temporary directory containing the symlink.

Positive setup and trigger:
```python
import os, tempfile, shutil
from onionshare_cli.common import Common
from onionshare_cli.settings import Settings
from onionshare_cli.mode_settings import ModeSettings
from onionshare_cli.web import Web

base = tempfile.mkdtemp(prefix='os-symlink-final-poc-')
outside = os.path.join(base, 'outside-secret.txt')
root = os.path.join(base, 'site')
os.mkdir(root)
open(outside, 'w').write('OUTSIDE_SECRET_MARKER')
os.symlink(outside, os.path.join(root, 'link.txt'))

common = Common()
common.settings = Settings(common)

w = Web(common, False, ModeSettings(common), 'website')
w.app.testing = True
w.website_mode.set_file_info([root])
with w.app.test_client() as c:
    print(c.get('/link.txt').status_code)
    print(c.get('/link.txt').get_data(as_text=True))

s = Web(common, False, ModeSettings(common), 'share')
s.app.testing = True
s.share_mode.set_file_info([root])
with s.app.test_client() as c:
    print('OUTSIDE_SECRET_MARKER' in c.get('/download').get_data(as_text=True))

s2 = Web(common, False, ModeSettings(common), 'share')
s2.app.testing = True
s2.settings.set('share', 'autostop_sharing', False)
s2.share_mode.set_file_info([root])
with s2.app.test_client() as c:
    print(c.get('/link.txt').status_code)
    print(c.get('/link.txt').get_data(as_text=True))

shutil.rmtree(base)
```

Observed output from this environment after re-running the proof after drafting:
```text
website_mapped_link_is_symlink: True
website_positive_status: 200
website_positive_body: OUTSIDE_SECRET_MARKER
website_control_status: 404
website_control_contains_secret: False
share_zip_status: 200
share_zip_contains_secret: True
share_individual_status: 200
share_individual_body: OUTSIDE_SECRET_MARKER
cleanup_done: true
```

Negative/control case:
- Requesting `/missing.txt` in Website mode returned HTTP 404 and did not contain `OUTSIDE_SECRET_MARKER`, showing the proof is not a general path traversal or test harness artifact.
- Recursive ZIP traversal has a partial control mitigation in `ZipWriter.add_dir()` (`cli/onionshare_cli/web/share_mode.py:593-596`), but the proven variants bypass that sibling mitigation through root-level single-folder expansion and direct file streaming.

Cleanup:
- The PoC deletes the temporary directory with `shutil.rmtree(base)`; the audit run printed `cleanup_done: true`.

### Impact
A remote recipient of an OnionShare Share or Website service can obtain files outside the selected shared directory if that directory contains a symlink to a readable local file. This can disclose SSH keys, browser profile data, wallet files, documents, or other local secrets readable by the OnionShare process.

The most realistic attack is a malicious archive/project/export supplied to the OnionShare user that contains a symlink to a sensitive path. If the user extracts or otherwise obtains that directory and shares it with OnionShare, the recipient can request the symlink path through Website mode, Share individual-file mode, or receive it inside the default Share ZIP in the single-folder root-symlink case.

The issue is especially surprising because one ZIP code path already tries to skip symlinks recursively, which suggests symlink dereference outside the shared tree is not intended.

### Suggested remediation
Reject symlinks and enforce canonical containment both when building the file map and immediately before opening/streaming/zipping a file:

- In `SendBaseModeWeb.set_file_info()`, do not add paths where `os.path.islink(path)` is true.
- Track selected root directories as canonical `Path.resolve()` values and require every served/zipped file's resolved path to remain under one of those roots.
- Re-check the resolved path immediately before `open()` in `stream_individual_file()` and before `ZipWriter.add_file()` / `ZipWriter.add_dir()` to avoid symlink-swap/TOCTOU surprises.
- Add regression tests for:
  - Website mode serving a root-level symlink.
  - Website mode serving a nested symlink.
  - Share default `/download` ZIP for a single selected folder containing a symlink.
  - Share `--no-autostop-sharing` individual-file symlink download.
  - Existing recursive ZIP symlink skip behavior.

## References
- https://github.com/onionshare/onionshare/security/advisories/GHSA-22p9-r2f5-22mf
- https://github.com/onionshare/onionshare/commit/48f31cfac077fcc9c04c67c2a6dbf87d956f5eec
- https://github.com/onionshare/onionshare
- https://github.com/onionshare/onionshare/releases/tag/v2.6.4
