# [C] Prototype Pollution in merge-options

## Summary
Severity: Critical
Advisory: GHSA-qw93-45r3-p66p
CVE: CVE-2018-3752
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-09
Source: https://github.com/advisories/GHSA-qw93-45r3-p66p
Type: github-advisory

## Affected
- npm: `merge-options` — affected >=0 <1.0.1

## Details
All versions of `merge-options` are vulnerable to Prototype Pollution


## Recommendation

Update to version 1.0.1 or greater.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3752
- https://github.com/schnittstabil/merge-options/commit/d4a93bc2890455e0931ac0779667023e6cb101d4
- https://hackerone.com/reports/311336
- https://github.com/advisories/GHSA-qw93-45r3-p66p
- https://github.com/schnittstabil/merge-options
- https://www.npmjs.com/advisories/717
