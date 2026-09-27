# [M] Craft CMS: Missing authorization check allows non-admin control panel users access to user registration metrics

## Summary
Severity: Medium
Advisory: GHSA-rvmm-v933-jgxq
CVE: CVE-2026-14794
CWE: CWE-266, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-rvmm-v933-jgxq
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.18.1
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.10.3

## Details
`ChartsController::actionGetNewUsersData()` at `/actions/charts/get-new-users-data` is missing a `requirePermission('viewUsers')` authorization check. Any authenticated control panel user, regardless of permissions beyond `accessCp`, can POST to this endpoint to receive time-series user registration counts for the entire site or for an arbitrary user group ID.

The `viewUsers` permission is consistently required throughout the control panel before exposing user-related data, but this action enforces only the base `accessCp` check inherited from the framework.

Each call returns the total count of users who joined the specified group in the requested period.

## Impact

Any control panel user with only `accessCp` permission can obtain the total number of registered users and their registration date distribution across any time window.

In installations with multiple editor roles, this allows a low-privilege control panel user to infer user group sizes and registration trends that would normally require the `viewUsers` permission to access.

No user PII (name, email, password) is disclosed; only aggregate counts and timestamps are returned. Confidentiality impact is low. No integrity or availability impact.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-rvmm-v933-jgxq
- https://nvd.nist.gov/vuln/detail/CVE-2026-14794
- https://github.com/craftcms/cms/commit/9ee53efc1314e6aba32771c66a13e072a246f4ce
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/4.18.1
- https://github.com/craftcms/cms/releases/tag/5.10.3
- https://vuldb.com/cve/CVE-2026-14794
- https://vuldb.com/submit/850793
- https://vuldb.com/vuln/376388
