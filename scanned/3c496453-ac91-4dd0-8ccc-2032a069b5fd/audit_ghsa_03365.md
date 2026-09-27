# [H] Any logged in user could edit any other logged in user.

## Summary
Severity: High
Advisory: GHSA-8hw9-22v6-9jr9
CVE: CVE-2021-29452
CWE: CWE-269, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-04-19
Source: https://github.com/advisories/GHSA-8hw9-22v6-9jr9
Type: github-advisory

## Affected
- npm: `@curveball/a12n-server` — affected >=0.18.0 <0.18.2

## Details
### Impact
Everyone who is running a12n-server. 

A new HAL-Form was added to allow editing users. This feature should only have been accessible to admins. Unfortunately, privileges were incorrectly checked allowing any logged in user to make this change.

### Patches
Patched in v0.18.2

## References
- https://github.com/curveball/a12n-server/security/advisories/GHSA-8hw9-22v6-9jr9
- https://nvd.nist.gov/vuln/detail/CVE-2021-29452
- https://www.npmjs.com/package/@curveball/a12n-server
