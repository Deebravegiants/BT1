# [C] Prototype pollution vulnerability in 'patchmerge'

## Summary
Severity: Critical
Advisory: GHSA-84g3-cv89-m9gm
CVE: CVE-2021-25916
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-13
Source: https://github.com/advisories/GHSA-84g3-cv89-m9gm
Type: github-advisory

## Affected
- npm: `patchmerge` — affected >=1.0.0 <1.0.2

## Details
Prototype pollution vulnerability in 'patchmerge' versions 1.0.0 through 1.0.1 allows an attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25916
- https://github.com/pjshumphreys/patchmerge/commit/5b383c537eae7a00ebd26d3f7211dac99ddecb12
- https://github.com/pjshumphreys/patchmerge
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25916
