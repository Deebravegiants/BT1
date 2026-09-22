# [M] AVideo: IDOR - Any Admin Can Set Another User's Channel Password via setPassword.json.php

## Summary
Severity: Medium
Advisory: GHSA-6547-8hrg-c55m
CVE: CVE-2026-33297
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-6547-8hrg-c55m
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
### Summary

The `setPassword.json.php` endpoint in the CustomizeUser plugin allows administrators to set a channel password for any user. Due to a logic error in how the submitted password value is processed, any password containing non-numeric characters is silently coerced to the integer zero before being stored. This means that regardless of the intended password, the stored channel password becomes 0, which any visitor can trivially guess to bypass channel-level access control.

### Details

The endpoint correctly restricts access to administrators only, but the password value submitted via the ProfilePassword request parameter is processed with `intval()` before being passed to `User::setProfilePassword()`. The relevant code is:

```php
$obj->ProfilePassword = intval(@$_REQUEST['ProfilePassword']);
$obj->users_id = $users_id;
$obj->response = User::setProfilePassword($users_id, $obj->ProfilePassword);
```

The call to `intval()` on an alphanumeric string such as secretabc123 returns 0. This silently discards the intended password value and stores 0 as the channel password instead. Because the coercion is silent, the administrator receives no error or warning and has no indication that the password they set was not stored correctly. Any visitor to the channel who enters 0 as the password will be granted access, completely defeating the channel password protection feature.

This is not a case where a malicious admin deliberately sets a weak password. The vulnerability causes well-intentioned admins to unknowingly install a trivially guessable password on any channel for which they attempt to configure a non-numeric password.

### PoC

```bash
curl -s -X POST "https://target.example.com/plugin/CustomizeUser/setPassword.json.php" \
  -b "PHPSESSID=<admin_session_cookie>" \
  -d "users_id=42&ProfilePassword=secretPassword123"
```

```bash
curl -s -X POST "https://target.example.com/channel_password_check_endpoint" \
  -d "users_id=42&password=0"
```

```python
import requests

base_url = "https://target.example.com"
session = requests.Session()

session.post(f"{base_url}/login", data={"user": "admin", "pass": "adminpass"})

session.post(
    f"{base_url}/plugin/CustomizeUser/setPassword.json.php",
    data={"users_id": "42", "ProfilePassword": "mySuperSecretPassword"}
)

resp = session.post(
    f"{base_url}/plugin/CustomizeUser/setPassword.json.php",
    data={"users_id": "42", "ProfilePassword": "0"}
)

print(resp.text)
```

### Impact

Any administrator who sets a channel password using a non-numeric string unknowingly reduces that password to 0. Any unauthenticated or unprivileged user who simply enters 0 as the channel password can access the content that was intended to be protected. This breaks the confidentiality guarantees of the channel password protection feature across all channels managed by administrators who use alphanumeric passwords. The impact is scoped to channel-level access control and does not enable account takeover or privilege escalation, but it renders the password protection feature entirely ineffective for the common case of non-numeric passwords.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-6547-8hrg-c55m
- https://nvd.nist.gov/vuln/detail/CVE-2026-33297
- https://github.com/WWBN/AVideo/commit/7a6a94631a0a18c313894395e6eb6703cca4abd0
- https://github.com/WWBN/AVideo
