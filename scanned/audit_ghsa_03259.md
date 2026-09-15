# [C] Prototype Pollution in deep-override

## Summary
Severity: Critical
Advisory: GHSA-v659-54cx-g4qr
CVE: CVE-2021-25941
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-17
Source: https://github.com/advisories/GHSA-v659-54cx-g4qr
Type: github-advisory

## Affected
- npm: `deep-override` — affected >=1.0.0 <1.0.2

## Details
Prototype pollution vulnerability in 'deep-override' versions 1.0.0 through 1.0.1 allows an attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25941
- https://github.com/ASaiAnudeep/deep-override/commit/2aced17651fb684959a6e04b1465a8329b3d5268
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25941
