# [H] Craft CMS: Missing peer-permission check in `AssetsController::actionDeleteFolder` allows deletion of other users' assets

## Summary
Severity: High
Advisory: GHSA-7h62-6v23-v8fm
CVE: CVE-2026-50284
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-7h62-6v23-v8fm
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.22
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.17.15

## Details
## Summary

`AssetsController::actionDeleteFolder()` only requires the `deleteAssets:<volume-uid>` permission for the target folder. It never enforces `deletePeerAssets:<volume-uid>`, even though `Assets::deleteFoldersByIds()` cascades deletion to every descendant folder and every asset inside, regardless of who uploaded them. A low-privilege user who has been granted folder-management rights on a shared volume can therefore destroy assets uploaded by other users (peer assets), bypassing the per-asset peer-permission check that the sibling `actionDeleteAsset` endpoint correctly applies.

This is the same bug class that was just fixed in `actionMoveFolder` as **GHSA-3w32-23wj-rxg3** (commit `05c2042`, Apr 23 2026); the fix added `requireVolumePermissionByFolder('deletePeerAssets', …)` and `savePeerAssets` checks to the move endpoint but did not propagate to the delete-folder endpoint.

## Details

`src/controllers/AssetsController.php:552-569`:

```php
public function actionDeleteFolder(): Response
{
    $this->requireAcceptsJson();
    $folderId = $this->request->getRequiredBodyParam('folderId');

    $assets = Craft::$app->getAssets();
    $folder = $assets->getFolderById($folderId);

    if (!$folder) {
        throw new BadRequestHttpException('The folder cannot be found');
    }

    // Check if it's possible to delete objects in the target volume.
    $this->requireVolumePermissionByFolder('deleteAssets', $folder); // <-- only checks deleteAssets
    $assets->deleteFoldersByIds($folderId);

    return $this->asSuccess();
}
```

`requireVolumePermissionByFolder()` (`src/controllers/AssetsControllerTrait.php:75-88`) only resolves to a single `requirePermission('deleteAssets:<vol-uid>')` call. The peer-equivalent helper (`requirePeerVolumePermissionByAsset`) is never invoked because there is no folder-level peer helper that iterates the folder's contents.

`Assets::deleteFoldersByIds()` (`src/services/Assets.php:311-349`) then enumerates the folder + every descendant folder, queries every asset under those IDs, and calls `Craft::$app->getElements()->deleteElement($asset, true)` directly:

```php
$assetQuery = Asset::find()->folderId($allFolderIds);
$elementService = Craft::$app->getElements();

foreach (Db::each($assetQuery) as $asset) {
    $asset->keepFileOnDelete = !$deleteDir;
    $elementService->deleteElement($asset, true);
}
```

This bypasses `Asset::canDelete()` (`src/elements/Asset.php:1515-1536`):

```php
public function canDelete(User $user): bool
{
    if ($this->isFolder) { return false; }
    if (parent::canDelete($user)) { return true; }
    $volume = $this->getVolume();
    if (Assets::isTempUploadFs($volume->getFs())) { return true; }

    if ($this->uploaderId !== $user->id) {
        return $user->can("deletePeerAssets:$volume->uid"); // <-- never reached on cascade delete
    }
    return $user->can("deleteAssets:$volume->uid");
}
```

Compare to `actionDeleteAsset` (`src/controllers/AssetsController.php:579-613`), which correctly does:

```php
$this->requireVolumePermissionByAsset('deleteAssets', $asset);
$this->requirePeerVolumePermissionByAsset('deletePeerAssets', $asset);
```

The fix that landed in `05c2042` for `actionMoveFolder` (`src/controllers/AssetsController.php:733-765`) added both `savePeerAssets` and `deletePeerAssets` `requireVolumePermissionByFolder` checks to mirror the per-asset pattern, but the same hardening was not applied to `actionDeleteFolder` or `actionRenameFolder` (which also calls `deleteFoldersByIds` indirectly through later logic).

The asymmetry between the two endpoints demonstrates the missing check.

## Impact

- Integrity / availability of other users' assets on any volume where the attacker has `deleteAssets` but not `deletePeerAssets`: the attacker can permanently delete peer-owned files (and their parent folder structure) on the underlying filesystem, with no recovery via Craft's UI.
- The Craft permission model explicitly distinguishes "delete your own assets" (`deleteAssets`) from "delete other users' assets" (`deletePeerAssets`) precisely so administrators can grant the former without the latter on shared volumes — this finding renders that distinction unenforceable for any user given folder-delete rights.
- No information disclosure or remote code execution; impact is bounded to the affected volume's contents.
- Does not require any non-default configuration: the affected endpoint is enabled by default and only requires that an administrator has split `deleteAssets` from `deletePeerAssets` (the documented, supported permission model).

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-7h62-6v23-v8fm
- https://nvd.nist.gov/vuln/detail/CVE-2026-50284
- https://github.com/craftcms/cms/commit/b4e08977f0c9bdf002a77f9f6d1346cd55ac0598
- https://github.com/craftcms/cms
