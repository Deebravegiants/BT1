# [H] Craft CMS Vulnerable to Unauthorized Deletion of Destination Folders During Forced Moves

## Summary
Severity: High
Advisory: GHSA-3w32-23wj-rxg3
CVE: CVE-2026-50282
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-3w32-23wj-rxg3
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.21
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.17.14

## Details
We have identified an authorization issue in Craft CMS where a forced folder move can delete a conflicting destination folder without destination delete permission.

### Description

Craft CMS’s `craft\\controllers\\AssetsController::actionMoveFolder()` supports moving an asset folder into a destination parent folder. If a folder with the same name already exists at the destination, the action can be called with `force=true` to overwrite the destination.

The permission checks for this action allow:

- `deleteAssets:<sourceVolumeUid>` for the folder being moved  
- `createFolders:<destVolumeUid>` for the destination parent folder  
- `saveAssets:<destVolumeUid>` for the destination parent folder

The action does not require `deleteAssets` on the destination volume or destination conflict folder. When `force=true` and a name conflict exists, the code deletes the destination folder to resolve the conflict.

```php
$this->requireVolumePermissionByFolder('deleteAssets', $folderToMove);
$this->requireVolumePermissionByFolder('createFolders', $destinationFolder);
$this->requireVolumePermissionByFolder('saveAssets', $destinationFolder);
```

[*src/controllers/AssetsController.php:L751-L753*](https://github.com/craftcms/cms/blob/5.x/src/controllers/AssetsController.php#L751-L753)

Indexed destination conflicts are deleted via the Assets service:

```php
$assets->deleteFoldersByIds($existingFolder->id);
```

[*src/controllers/AssetsController.php:L798-L798*](https://github.com/craftcms/cms/blob/5.x/src/controllers/AssetsController.php#L798-L798)

Unindexed destination conflicts are deleted directly in the volume filesystem:

```php
$targetVolume->deleteDirectory(rtrim($destinationFolder->path, '/') . '/' . $folderToMove->name);
```

[*src/controllers/AssetsController.php:L815*](https://github.com/craftcms/cms/blob/5.x/src/controllers/AssetsController.php#L815)

### Impact

A user who cannot delete assets in a destination volume can still delete a destination folder and its contents by triggering a forced move into a conflicting name. This can cause asset loss, broken references in entries and fields that point to deleted assets, and operational disruption.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-3w32-23wj-rxg3
- https://nvd.nist.gov/vuln/detail/CVE-2026-50282
- https://github.com/craftcms/cms/commit/2c2579c7f1030872423f268d0c8b48377101961d
- https://github.com/craftcms/cms
