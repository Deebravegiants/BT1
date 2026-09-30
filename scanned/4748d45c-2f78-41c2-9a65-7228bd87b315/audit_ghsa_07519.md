# [M] changedetection.io is vulnerable to unauthenticated static path traversal

## Summary
Severity: Medium
Advisory: GHSA-9jj8-v89v-xjvw
CVE: CVE-2026-25527
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-9jj8-v89v-xjvw
Type: github-advisory

## Affected
- PyPI: `changedetection.io` — affected >=0 <0.53.2

## Details
## Summary
The `/static/<group>/<filename>` route accepts `group=".."`, which causes `send_from_directory("static/..", filename)` to execute. This moves the base directory up to `/app/changedetectionio`, enabling **unauthenticated local file read** of application source files (e.g., `flask_app.py`). Severity is **low information disclosure (C:L)**.

### Details
The vulnerable code is in `changedetectionio/flask_app.py` inside `static_content()`:

```
group = re.sub(r'[^\w.-]+', '', group.lower())
filename = re.sub(r'[^\w.-]+', '', filename.lower())
...
return send_from_directory(f"static/{group}", path=filename)
```

The `group` sanitization allows dots, so `group=".."` passes validation.  
This results in `send_from_directory("static/..", filename)`, effectively shifting the base directory to `/app/changedetectionio` and allowing reads of files in that directory.  
The route is unauthenticated, so **any user can retrieve source files** without logging in.

> Limitation: the route only matches `/static/<group>/<filename>` and rejects slashes inside `filename`, so it cannot traverse further to arbitrary system paths like `/etc/passwd`. It is limited to files inside the application package directory.

### PoC
1) Start an instance (example: Docker on port 5050)
```
docker run -d --name cdio -p 127.0.0.1:5050:5000 -v cdio-data:/datastore cdio-local
```

2) Reproduce  
**(URL-encoded traversal)**
```
curl -i http://127.0.0.1:5050/static/%2e%2e/flask_app.py
```

**(curl path passthrough)**
```
curl --path-as-is -i http://127.0.0.1:5050/static/../flask_app.py
```

3) Observe that the response body contains Python source code from `flask_app.py`.

### Impact
- **Vulnerability type:** Directory Traversal / Local File Read
- **Affected users:** Anyone with network access (no authentication required)
- **Scope:** Source files under `/app/changedetectionio`
- **Security impact:** Internal logic exposure can aid further exploitation (Confidentiality: Low)

## References
- https://github.com/dgtlmoon/changedetection.io/security/advisories/GHSA-9jj8-v89v-xjvw
- https://nvd.nist.gov/vuln/detail/CVE-2026-25527
- https://github.com/dgtlmoon/changedetection.io/commit/9d38b4517364831889b5b0d7b3465fd060403fd4
- https://github.com/dgtlmoon/changedetection.io
- https://github.com/pypa/advisory-database/tree/main/vulns/changedetection-io/PYSEC-2026-2124.yaml
