# [H] CraftCMS's `ElementSearchController` Affected by Blind SQL Injection

## Summary
Severity: High
Advisory: GHSA-g7j6-fmwx-7vp8
CVE: CVE-2026-31858
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-g7j6-fmwx-7vp8
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.9

## Details
The `ElementSearchController::actionSearch()` endpoint is missing the `unset()` protection that
was added to ElementIndexesController in [GHSA-2453-mppf-46cj](https://github.com/craftcms/cms/security/advisories/GHSA-2453-mppf-46cj).

The exact same SQL injection vulnerability (including `criteria[orderBy]`, the original advisory vector) works on this controller because the fix was never applied to it.

Any authenticated control panel user (no admin required) can inject arbitrary SQL via `criteria[where]`,
`criteria[orderBy]`, or other query properties, and extract the full database contents via boolean-based blind injection.

Users should update to the patched 5.9.9 release to mitigate the issue.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-2453-mppf-46cj
- https://github.com/craftcms/cms/security/advisories/GHSA-g7j6-fmwx-7vp8
- https://nvd.nist.gov/vuln/detail/CVE-2026-31858
- https://github.com/craftcms/cms/commit/e1a3dd669ae31491b86ad996e88a1d30d33d9a42
- https://github.com/craftcms/cms
