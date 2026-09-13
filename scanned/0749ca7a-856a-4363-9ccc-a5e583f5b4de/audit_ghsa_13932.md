# [H] rangy vulnerable to Prototype Pollution

## Summary
Severity: High
Advisory: GHSA-65rp-mhqf-8gj3
CVE: CVE-2023-26102
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2023-02-24
Source: https://github.com/advisories/GHSA-65rp-mhqf-8gj3
Type: github-advisory

## Affected
- npm: `rangy` — affected >=0

## Details
All versions of the package rangy are vulnerable to Prototype Pollution when using the `extend()` function in file `rangy-core.js`.The function uses recursive merge which can lead an attacker to modify properties of the Object.prototype.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26102
- https://github.com/timdown/rangy/issues/478
- https://github.com/timdown/rangy
- https://security.snyk.io/vuln/SNYK-JS-RANGY-3175702
