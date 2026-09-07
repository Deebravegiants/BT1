# [H] depath and cool-path vulnerable to Prototype Pollution via `set()` Method

## Summary
Severity: High
Advisory: GHSA-4h4x-4m75-47j4
CVE: CVE-2024-38985
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:N/E:P (CVSS_V4)
Published: 2025-03-28
Source: https://github.com/advisories/GHSA-4h4x-4m75-47j4
Type: github-advisory

## Affected
- npm: `depath` — affected >=0
- npm: `cool-path` — affected >=0

## Details
janryWang products depath v1.0.6 and cool-path v1.1.2 were discovered to contain a prototype pollution via the set() method at setIn (lib/index.js:90). This vulnerability allows attackers to execute arbitrary code or cause a Denial of Service (DoS) via injecting arbitrary properties.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38985
- https://github.com/janryWang/depath/issues/11
- https://gist.github.com/mestrtee/32c0a48023036e51918f6a098f21953d
- https://github.com/janryWang/depath
