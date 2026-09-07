# [C] Snipe-IT has insecure permissions in file uploads

## Summary
Severity: Critical
Advisory: GHSA-xg82-2hrv-hf64
CVE: CVE-2026-37709
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-xg82-2hrv-hf64
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.4.1

## Details
Insecure Permissions vulnerability in grokability snipe-it versions through 8.4.0, fixed after 2026-03-10 commit 676a9958, allow a remote attacker to execute arbitrary code via the `app/Http/Controllers/Api/UploadedFilesController.php` component

### Impact
Users who can view assets, consumables, etc were able to send a POST request to `/api/v1/{object_type}/{id}/files`. The API authorized with "view" instead of write permission and persists the file and audit log entry.

### Patches
Fixed after 2026-03-10 commit 676a9958, fix released to 8.4.1.

### Workarounds
None.

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-xg82-2hrv-hf64
- https://nvd.nist.gov/vuln/detail/CVE-2026-37709
- https://github.com/grokability/snipe-it/commit/676a9958895a77de340565e7a0b17ae744664904
- https://github.com/grokability/snipe-it
