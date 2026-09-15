# [H] Laravel Backpack CRUD: Arbitrary file deletion via attacker-controlled clear_<attr>[] in HasUploadFields::uploadMultipleFilesToDisk

## Summary
Severity: High
Advisory: GHSA-8xjm-wqrp-2f25
CVE: CVE-2026-54178
CWE: CWE-22, CWE-285, CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-8xjm-wqrp-2f25
Type: github-advisory

## Affected
- Packagist: `backpack/crud` — affected >=5.0.0
- Packagist: `backpack/crud` — affected >=6.0.0 <6.8.12
- Packagist: `backpack/crud` — affected >=7.0.0 <7.0.35

## Details
## Summary

`HasUploadFields::uploadMultipleFilesToDisk` (in `src/app/Models/Traits/HasUploadFields.php`) reads file paths from the `clear_<attribute>[]` request input and deletes them from the configured storage disk **without verifying that the paths belong to the current model record**.

An authenticated user with Update access on any CRUD that wires `uploadMultipleFilesToDisk` as a model mutator (the pattern documented in the v5.x `upload_multiple` field guide) can supply arbitrary disk-relative paths in `clear_<attr>[]` to delete files that were never associated with the record they are editing.

The safe pattern already exists in the codebase: `src/app/Library/Uploaders/MultipleFiles.php` intersects the requested deletions against the files currently stored in the database column before calling `Storage::disk()->delete()`. The trait method lacks that intersection.

## Affected code

- `src/app/Models/Traits/HasUploadFields.php` — `uploadMultipleFilesToDisk` (primary sink)
- `src/app/Models/Traits/CrudTrait.php` — mixes `HasUploadFields` into all Backpack-managed models

The vulnerability is present in all 5.x, 6.x < 6.8.12, and 7.x < 7.0.35 releases.

## Impact

An attacker with low-privilege Backpack admin access (e.g. a content editor) can delete any file under the configured disk root: other records' attachments, shared assets, or files placed on the same disk for operational purposes. No confidentiality impact (files cannot be read, only deleted).

**CWE-285** (Authorization Bypass) / **CWE-639** (IDOR on file deletion)  
CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H = **8.1 High**

## Fix

Intersect `$files_to_clear` against the filenames currently persisted on the model before calling `delete()`, mirroring the logic already present in `MultipleFiles::uploadFiles`. Fixed in **6.8.12** and **7.0.35**.

Deployments still using the `uploadMultipleFilesToDisk` mutator pattern from the v5.x docs should migrate to the Uploader API (`MultipleFiles::class` via `config/backpack/crud.php`), which applies the safe intersection automatically.

## Credits

Reported by Vishal Shukla ([@shukla304](https://github.com/shukla304)).

## References
- https://github.com/Laravel-Backpack/CRUD/security/advisories/GHSA-8xjm-wqrp-2f25
- https://github.com/Laravel-Backpack/CRUD
- https://github.com/Laravel-Backpack/CRUD/releases/tag/6.8.12
- https://github.com/Laravel-Backpack/CRUD/releases/tag/7.0.35
