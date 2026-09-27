# [C] tree-kit Prototype Pollution vulnerability

## Summary
Severity: Critical
Advisory: GHSA-5p42-m6f3-hpmj
CVE: CVE-2023-38894
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-17
Source: https://github.com/advisories/GHSA-5p42-m6f3-hpmj
Type: github-advisory

## Affected
- npm: `tree-kit` — affected >=0 <0.7.5

## Details
A Prototype Pollution issue in Cronvel Tree-kit v.0.7.4 and before allows a remote attacker to execute arbitrary code via the extend function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-38894
- https://github.com/cronvel/tree-kit/commit/61bf10cf0dbddaeea3f198cfe7cb469f360d82bc
- https://github.com/cronvel/tree-kit
- https://www.code-intelligence.com/blog/treekit-prototype-pollution-cve-2023-38894
- http://tree-kit.com
