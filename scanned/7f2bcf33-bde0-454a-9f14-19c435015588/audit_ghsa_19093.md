# [H] module-from-string prototype pollution

## Summary
Severity: High
Advisory: GHSA-q5j8-9m9g-x2jh
CVE: CVE-2024-57072
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-02-06
Source: https://github.com/advisories/GHSA-q5j8-9m9g-x2jh
Type: github-advisory

## Affected
- npm: `module-from-string` — affected >=0

## Details
A prototype pollution in the lib.requireFromString function of module-from-string v3.3.1 allows attackers to cause a Denial of Service (DoS) via supplying a crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-57072
- https://gist.github.com/tariqhawis/8b1fe301dd1ea52952cef347daddee67
- https://github.com/exuanbo/module-from-string
