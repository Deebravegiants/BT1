# [C] Critical severity vulnerability in Ignition

## Summary
Severity: Critical
Advisory: GHSA-m5v7-pr32-mjx2
CVE: CVE-2020-13909
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-m5v7-pr32-mjx2
Type: github-advisory

## Affected
- Packagist: `facade/ignition` — affected >=2.0.0 <2.0.5
- Packagist: `facade/ignition` — affected >=0 <1.16.15

## Details
The Ignition page before version 2.0.5 for Laravel mishandles globals, _get, _post, _cookie, and _env.

NOTE: in the 1.x series, versions 1.16.15 and later are unaffected as a consequence of the CVE-2021-43996 fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13909
- https://github.com/github/advisory-database/issues/2316
- https://github.com/facade/ignition
- https://github.com/facade/ignition/compare/2.0.4...2.0.5
- https://github.com/facade/ignition/releases/tag/2.0.5
- https://www.cve.org/CVERecord?id=CVE-2020-13909
