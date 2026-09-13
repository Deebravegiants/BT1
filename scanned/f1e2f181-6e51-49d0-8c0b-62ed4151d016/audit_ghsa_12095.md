# [M] Amazon S3 for Craft CMS has an Information Disclosure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hwj7-4vgc-j3v9
CVE: CVE-2026-32265
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-hwj7-4vgc-j3v9
Type: github-advisory

## Affected
- Packagist: `craftcms/aws-s3` — affected >=2.0.2 <2.2.5

## Details
Unauthenticated users can view a list of buckets the plugin has access to.

The `BucketsController->actionLoadBucketData()` endpoint allows unauthenticated users with a valid CSRF token to view a list of buckets that the plugin is allowed to see.

Users should update to version 2.2.5 of the plugin to mitigate the issue.

## References
- https://github.com/craftcms/aws-s3/security/advisories/GHSA-hwj7-4vgc-j3v9
- https://nvd.nist.gov/vuln/detail/CVE-2026-32265
- https://github.com/craftcms/aws-s3/commit/ef8904d8b6856e4a52893a9e1e52988ae110aa3f
- https://github.com/craftcms/aws-s3
