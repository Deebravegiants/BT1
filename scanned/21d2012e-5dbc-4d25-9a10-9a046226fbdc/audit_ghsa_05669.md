# [H] Unauthenticated Craft CMS users can trigger a database backup

## Summary
Severity: High
Advisory: GHSA-v64r-7wg9-23pr
CVE: CVE-2025-68456
CWE: CWE-202, CWE-770
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-v64r-7wg9-23pr
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.8.21
- Packagist: `craftcms/cms` — affected >=3.0.0 <4.16.17

## Details
Unauthenticated users can trigger database backup operations the `updater/backup` action, potentially leading to resource exhaustion or information disclosure.

Users should update to the patched versions (5.8.21 and 4.16.17) to mitigate the issue.

Craft 3 users should update to the latest Craft 4 and 5 releases, which include the fixes.

References:

https://github.com/craftcms/cms/commit/f83d4e0c6b906743206b4747db4abf8164b8da39

https://github.com/craftcms/cms/blob/5.x/CHANGELOG.md#5821---2025-12-04

## Affected Endpoints

- `POST /admin/actions/updater/backup` (unauthenticated)

## Vulnerability Details

### Root Cause
All `updater/*` actions are explicitly configured with anonymous access:

```php
// BaseUpdaterController.php  
protected array|bool|int $allowAnonymous = self::ALLOW_ANONYMOUS_LIVE | self::ALLOW_ANONYMOUS_OFFLINE;
```

### Attack Vector
1. Send unauthenticated POST request to `/admin/actions/updater/backup`
2. Database backup executes with configured `backupCommand`

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-v64r-7wg9-23pr
- https://nvd.nist.gov/vuln/detail/CVE-2025-68456
- https://github.com/craftcms/cms/commit/f83d4e0c6b906743206b4747db4abf8164b8da39
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/blob/5.x/CHANGELOG.md#5821---2025-12-04
