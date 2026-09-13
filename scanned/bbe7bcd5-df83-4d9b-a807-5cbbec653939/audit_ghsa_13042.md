# [M] @adobe/css-tools Regular Expression Denial of Service (ReDOS) while Parsing CSS

## Summary
Severity: Medium
Advisory: GHSA-hpx4-r86g-5jrg
CVE: CVE-2023-26364
CWE: CWE-1333, CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2023-08-29
Source: https://github.com/advisories/GHSA-hpx4-r86g-5jrg
Type: github-advisory

## Affected
- npm: `@adobe/css-tools` — affected >=0 <4.3.1

## Details
### Impact
@adobe/css-tools version 4.3.0 and earlier are affected by an Improper Input Validation vulnerability that could result in a denial of service while attempting to parse CSS.

### Patches
The issue has been resolved in 4.3.1.

### Workarounds
None

### References
N/A

## References
- https://github.com/adobe/css-tools/security/advisories/GHSA-hpx4-r86g-5jrg
- https://nvd.nist.gov/vuln/detail/CVE-2023-26364
- https://github.com/adobe/css-tools/commit/2b09a25d1dbdbb16fe80065e4c9beb5623ee5793
- https://github.com/adobe/css-tools
