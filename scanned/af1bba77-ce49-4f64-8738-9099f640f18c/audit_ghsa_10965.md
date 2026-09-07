# [M] Craft CMS has a Path Traversal Vulnerability in AssetsController

## Summary
Severity: Medium
Advisory: GHSA-472v-j2g4-g9h2
CVE: CVE-2026-32262
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-472v-j2g4-g9h2
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.17.5
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.11

## Details
The `AssetsController->replaceFile()` method has a `targetFilename` body parameter that is used unsanitized in a `deleteFile()` call before `Assets::prepareAssetName()` is applied on save. This allows an authenticated user with `replaceFiles` permission to delete arbitrary files within the same filesystem root by injecting `../` path traversal sequences into the filename.

This could allow an authenticated user with `replaceFiles` permission on one volume to delete files in other folders/volumes that share the same filesystem root.

This only affects local filesystems.

Users should update to Craft 4.17.5 or 5.9.11 to mitigate the issue.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-472v-j2g4-g9h2
- https://nvd.nist.gov/vuln/detail/CVE-2026-32262
- https://github.com/craftcms/cms/commit/c997efbe4c66c14092714233aeebff15cdbfcf11
- https://github.com/craftcms/cms
