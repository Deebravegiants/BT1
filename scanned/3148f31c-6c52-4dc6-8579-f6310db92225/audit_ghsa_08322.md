# [C] dash-uploader has a directory traversal vulnerability

## Summary
Severity: Critical
Advisory: GHSA-3rf6-x59v-5jfv
CVE: CVE-2026-38360
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-3rf6-x59v-5jfv
Type: github-advisory

## Affected
- PyPI: `dash-uploader` — affected >=0.1.0

## Details
### Impact

An unauthenticated path traversal vulnerability exists in [dash-uploader](https://pypi.org/project/dash-uploader/) versions 0.1.0 through 0.7.0a2. The library's HTTP request handler at `dash_uploader/httprequesthandler.py` reads three form parameters (`upload_id`, `resumableFilename`, `resumableIdentifier`) from `request.form.get()` and passes them directly to `os.path.join()` and `os.makedirs()` without any sanitization.

A single unauthenticated `POST /API/dash-uploader` request with `upload_id` set to a relative path (e.g. `../../etc/cron.d` or `../venv/lib/python3.13/site-packages`) escapes the application's `uploads/` directory and writes the supplied file content to the chosen target path under the privilege of the gunicorn / WSGI process.

When the chosen target is a Python `site-packages` directory and the dropped file is a `.pth` file containing an `import`-prefixed line, Python's `site` module executes that line on the next interpreter startup, yielding remote code execution. Other escalation paths reachable from the same primitive include overwriting the running WSGI module, dropping `~/.ssh/authorized_keys`, or writing JavaScript into a Dash-served `assets/` directory for stored XSS.

### Affected versions

All 16 published PyPI releases (`0.1.0` through `0.7.0a2`) are affected. The package repository was archived on 2025-07-19; **no patched version exists**.

### Mitigation

Replace `dash-uploader` with an alternative file-upload component (for example, `dash-resumable-upload`, server-rendered `<input type=\"file\">` plus a hardened Flask endpoint, or a maintained Dash community alternative). There is no upstream fix path.

While a replacement is being deployed, mitigations include:

* Block `POST /API/dash-uploader` at an upstream proxy, OR
* Run the application as an unprivileged user with no write access to its own `site-packages`, OR
* Use a read-only filesystem for the application's code directories.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-38360
- https://github.com/fohrloop/dash-uploader/issues/153
- https://github.com/github/advisory-database/pull/7635
- https://github.com/a1ohadance/CVE-2026-38360
- https://github.com/fohrloop/dash-uploader
- https://github.com/fohrloop/dash-uploader/blob/dev/dash_uploader/httprequesthandler.py
- https://github.com/fohrloop/dash-uploader/blob/stable/dash_uploader/httprequesthandler.py
- https://github.com/pypa/advisory-database/tree/main/vulns/dash-uploader/PYSEC-2026-320.yaml
