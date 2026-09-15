# [M] Private Weblate projects vulnerable to observable object existence disclosure via globally scoped object lookups

## Summary
Severity: Medium
Advisory: GHSA-2p9g-x3cv-5hh4
CVE: CVE-2026-55227
CWE: CWE-203
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-2p9g-x3cv-5hh4
Type: github-advisory

## Affected
- PyPI: `weblate` — affected >=0 <2026.7

## Details
### Impact
The several endpoints could leak object existence information to users who had no access to it by HTTP status code 403 instead of 404.

### Patches
* https://github.com/WeblateOrg/weblate/pull/19971

### References
Thanks to Yaohui Wang for reporting this via GitHub.

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-2p9g-x3cv-5hh4
- https://nvd.nist.gov/vuln/detail/CVE-2026-55227
- https://github.com/WeblateOrg/weblate/pull/19971
- https://github.com/WeblateOrg/weblate/commit/836bc082803d49d02f2831ec8339268eb66bcdae
- https://github.com/WeblateOrg/weblate
- https://github.com/WeblateOrg/weblate/releases/tag/weblate-2026.7
