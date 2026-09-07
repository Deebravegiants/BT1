# [M] Craft CMS: Unauthorized Deletion of Source Assets During File Replacement

## Summary
Severity: Medium
Advisory: GHSA-qh45-9g5p-m2v4
CVE: CVE-2026-50283
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-qh45-9g5p-m2v4
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.21
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.17.14

## Details
We have identified an authorization issue in Craft CMS `AssetsController::actionReplaceFile` that can delete a source asset without source delete permission by supplying both `assetId` and `sourceAssetId`.

### Description

Craft CMS’s `craft\\controllers\\AssetsController::actionReplaceFile()` supports replacing a target asset file using another existing asset as the source. The action loads:

- `$assetToReplace` from `assetId`  
- `$sourceAsset` from `sourceAssetId`

It then enforces replace permissions using `($assetToReplace ?: $sourceAsset)`. When both IDs are provided, this expression resolves to the target asset so no permission check is performed against the source asset volume.

```php
$this->requireVolumePermissionByAsset('replaceFiles', $assetToReplace ?: $sourceAsset);
$this->requirePeerVolumePermissionByAsset('replacePeerFiles', $assetToReplace ?: $sourceAsset);
```

[*src/controllers/AssetsController.php:L433-L434*](https://github.com/craftcms/cms/blob/5.x/src/controllers/AssetsController.php#L433-L434)

In the branch where both assets are present, Craft copies the source file into the target and then deletes the source asset. There is no check for `deleteAssets:<sourceVolumeUid>` or `deletePeerAssets:<sourceVolumeUid>` for the source asset before deletion.

```php
$assets->replaceAssetFile($assetToReplace, $tempPath, $assetToReplace->getFilename(), $sourceAsset->getMimeType());
Craft::$app->getElements()->deleteElement($sourceAsset);
```

[*src/controllers/AssetsController.php:L462-L463*](https://github.com/craftcms/cms/blob/5.x/src/controllers/AssetsController.php#L462-L463)

### Impact

An authenticated user who can replace files in one volume can delete assets in another volume where they do not have delete permission, as long as they can obtain a `sourceAssetId`. This can lead to unauthorized asset deletion, broken content references, and data loss.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-qh45-9g5p-m2v4
- https://nvd.nist.gov/vuln/detail/CVE-2026-50283
- https://github.com/craftcms/cms/commit/2c2579c7f1030872423f268d0c8b48377101961d
- https://github.com/craftcms/cms
