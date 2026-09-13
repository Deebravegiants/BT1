# [M] OnionShare Receive mode writes uploaded files even when file uploads are disabled

## Summary
Severity: Medium
Advisory: GHSA-v833-3823-cmhp
CVE: CVE-2026-54707
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-v833-3823-cmhp
Type: github-advisory

## Affected
- PyPI: `onionshare-cli` — affected >=0 <2.6.4

## Details
### Summary
OnionShare CLI/Desktop 2.6.3 does not enforce the Receive mode `disable_files` setting at the file upload sink. When a Receive service is configured as a text-message-only endpoint (`--disable-files` / "Disable uploading files"), a remote sender who can reach the OnionShare service can still send a crafted multipart request containing `file[]`; OnionShare writes the uploaded bytes to disk before the route handler skips file accounting.

This affects the shipped `onionshare-cli` Python package and the desktop application because both use the same `onionshare_cli.web.receive_mode` request-streaming implementation.

### Details
Tested repository: `https://github.com/onionshare/onionshare` at commit `8cc75e1d7e88bd31f7276733449d412bf71c8999`.

Affected product evidence:
- `cli/pyproject.toml` declares `onionshare_cli` version `2.6.3`.
- `desktop/pyproject.toml` declares `onionshare` version `2.6.3` and depends on `onionshare_cli` from `../cli`.
- `cli/setup.py` publishes `onionshare-cli` and includes `onionshare_cli.web` plus templates/static resources.
- `desktop/setup.py` publishes `onionshare` and exposes both `onionshare` and `onionshare-cli` console scripts.

Reachable default/common paths:
- CLI Receive mode is exposed through `--receive` (`cli/onionshare_cli/__init__.py:55-57`).
- The `--disable-files` option is documented and stored in mode settings (`cli/onionshare_cli/__init__.py:156-160`, `cli/onionshare_cli/__init__.py:254-261`).
- Desktop Receive mode exposes the same setting via the "Disable uploading files" checkbox and stores it as `receive.disable_files` (`desktop/onionshare/tab/mode/receive_mode/__init__.py:89-99`, `desktop/onionshare/tab/mode/receive_mode/__init__.py:246-254`).
- User documentation says "Disable uploading files" should "only allow submitting text messages, like for an anonymous contact form" (`docs/source/features.rst:64`).
- Advanced documentation lists `--disable-files` and `disable_files` as the option to disable receiving files (`docs/source/advanced.rst:162-163`, `docs/source/advanced.rst:455`).

Root cause:
- The Receive template hides the file input when `disable_files` is set (`cli/onionshare_cli/resources/templates/receive.html:51-56`), but this is only UI-side.
- The `/upload` route skips `request.files.getlist("file[]")` and file accounting when `disable_files` is enabled (`cli/onionshare_cli/web/receive_mode.py:96-135`). However, by this point Werkzeug has already parsed the multipart body and invoked the custom stream factory.
- `ReceiveModeRequest.__init__()` treats every `POST /upload` or `POST /upload-ajax` as an upload request and creates a receive directory regardless of `disable_files` (`cli/onionshare_cli/web/receive_mode.py:369-391`).
- `ReceiveModeRequest._get_file_stream()` creates a writable `ReceiveModeFile` for each uploaded part without checking `self.web.settings.get("receive", "disable_files")` (`cli/onionshare_cli/web/receive_mode.py:517-540`).
- `ReceiveModeFile` opens `<receive_mode_dir>/<secure_filename>.part`, writes attacker-controlled bytes, then renames the `.part` file to the final filename (`cli/onionshare_cli/web/receive_mode.py:272-285`, `cli/onionshare_cli/web/receive_mode.py:320-346`).

False-positive screening performed:
- `secure_filename()` is used at `cli/onionshare_cli/web/receive_mode.py:111-113` and `cli/onionshare_cli/web/receive_mode.py:527-528`, so the confirmed issue is not path traversal; the file is written under the configured receive data directory.
- The UI hiding the file input is bypassable by direct multipart POST.
- Route-level `if not disable_files` only affects later accounting/status/webhook behavior; it does not prevent the stream sink from creating and writing the file.
- Default non-public onion services require the sender to know the onion address and private key unless the user opts into public mode. This limits exposure but does not enforce the user-selected "text only" security policy for authorized senders or public contact-form deployments.
- A control case with `disable_text=True` showed submitted text was not written as a message file, demonstrating the harness was exercising the settings boundary.

Affected versions / patched versions:
- Affected versions: unknown; confirmed in version `2.6.3` at commit `8cc75e1d7e88bd31f7276733449d412bf71c8999`. Earlier versions were not tested during this audit.
- Patched versions: 2.6.4

Severity:

 Rationale: `AV:N` because the Receive endpoint is reached over the OnionShare HTTP service; `AC:L` because a crafted multipart POST is straightforward once the service is reachable; `PR:L` because the sender generally needs the OnionShare URL/private key unless the receiver intentionally runs public mode; `UI:N` because no further receiver interaction is required after service startup; `S:U` because the same local application writes the file; `C:N` because this PoC does not read data; `I:L` because the attacker writes unwanted files in a mode configured to reject files; `A:L` because the bypass can consume disk/storage despite the files-disabled policy, bounded by available disk and operator controls.

### PoC
The following safe local proof uses only temporary directories and Flask's local test client. In this audit environment, several runtime dependencies were absent (`waitress`, `flask_compress`, `flask_socketio`, `unidecode`, `stem`, `qrcode`), so the harness stubbed those imports while executing the real `receive_mode` request parsing and file writing code. No external network traffic was sent and no real files outside temporary directories were modified.

Maintainer reproduction from a clean checkout with normal dependencies can omit the import stubs and run the same test-client setup, or can start a local Receive service with `--disable-files` and submit a multipart request to `/upload-ajax`.

Positive setup and trigger:
```python
import os, tempfile, shutil
from io import BytesIO
from onionshare_cli.common import Common
from onionshare_cli.settings import Settings
from onionshare_cli.mode_settings import ModeSettings
from onionshare_cli.web import Web

base = tempfile.mkdtemp(prefix='os-disable-files-poc-')
data_dir = os.path.join(base, 'receive-data')
os.mkdir(data_dir)

common = Common()
common.settings = Settings(common)
mode_settings = ModeSettings(common)
web = Web(common, False, mode_settings, 'receive')
web.app.testing = True
web.proxies = None
web.settings.set('receive', 'data_dir', data_dir)
web.settings.set('receive', 'disable_files', True)

with web.app.test_client() as c:
    res = c.post(
        '/upload-ajax',
        buffered=True,
        content_type='multipart/form-data',
        data={'file[]': (BytesIO(b'DISABLE_FILES_BYPASS_MARKER'), 'audit.txt')},
    )
    print(res.status_code)
    print(res.get_data(as_text=True))
    for root, dirs, files in os.walk(data_dir):
        for name in files:
            path = os.path.join(root, name)
            print(os.path.relpath(path, data_dir), open(path, 'rb').read().decode())

shutil.rmtree(base)
```

Observed output from this environment after re-running the proof after drafting:
```text
May 29, 06:13PM: Upload of total size 274.0 B is starting
=> 27.0 B audit.txt          positive_status: 200
positive_response: {"info_flashes": ["Nothing submitted or message was too long (> 524288 characters)"]}
positive_written: [('2026-05-29/181347904165/audit.txt', 'DISABLE_FILES_BYPASS_MARKER')]
```

The response says nothing/fileless was submitted, but the `audit.txt` file was created under the Receive data directory.

Negative/control case:
```python
web2.settings.set('receive', 'disable_text', True)
# POST only a text field to /upload-ajax
```

Observed control output:
```text
control_status: 200
control_response: {"info_flashes": ["Nothing submitted"]}
control_written_files: []
cleanup_done: true
```

Cleanup:
- The PoC deletes all temporary directories with `shutil.rmtree(...)`; the audit run printed `cleanup_done: true`.

### Impact
A Receive service operator can configure OnionShare as a text-only submission endpoint (for example, an anonymous contact form) and still receive attacker-controlled files on disk. This bypasses the explicit user-selected restriction and can lead to unwanted file placement and disk consumption in a deployment where file uploads were intentionally disabled.

The response and GUI/history accounting can be misleading because the route skips file processing while the lower-level request stream has already written the file. This may delay detection by the operator.

The confirmed issue does not provide arbitrary path traversal because filenames are sanitized and writes occur under the configured Receive data directory.

### Suggested remediation
Enforce `disable_files` before any multipart file stream is written, not only in the route handler or template:

- In `ReceiveModeRequest._get_file_stream()`, if `self.web.settings.get("receive", "disable_files")` is true, reject the file part before creating `ReceiveModeFile`, or route it to a discard stream and mark the request as rejected.
- Ensure `/upload` and `/upload-ajax` return an explicit error when files are submitted while files are disabled.
- Avoid creating a receive subdirectory for a file-only request that is rejected by policy.
- Add regression tests for both `/upload` and `/upload-ajax` proving no file appears under `receive.data_dir` when `receive.disable_files` is true.
- Add a control regression test proving `disable_text` still prevents message-file creation.

## References
- https://github.com/onionshare/onionshare/security/advisories/GHSA-v833-3823-cmhp
- https://github.com/onionshare/onionshare/commit/a090e97193efc91fbeac9dace7793ea568b83cf5
- https://github.com/onionshare/onionshare
- https://github.com/onionshare/onionshare/releases/tag/v2.6.4
