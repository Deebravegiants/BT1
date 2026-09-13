# [M] parse is vulnerable to prototype pollution

## Summary
Severity: Medium
Advisory: GHSA-9g8m-v378-pcg3
CVE: CVE-2025-57324
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-09-24
Source: https://github.com/advisories/GHSA-9g8m-v378-pcg3
Type: github-advisory

## Affected
- npm: `parse` — affected >=0 <7.0.0-alpha.1

## Details
parse is a package designed to parse JavaScript SDK. A Prototype Pollution vulnerability in the SingleInstanceStateController.initializeState function of parse allows attackers to inject properties on Object.prototype via supplying a crafted payload, causing denial of service (DoS) as the minimum consequence.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-57324
- https://github.com/parse-community/Parse-SDK-JS/commit/9e7c1bad472b1ed2463cbac567b8ec752ae5b4c9
- https://github.com/VulnSageAgent/PoCs/blob/main/JavaScript/prototype-pollution/parse%405.3.0/index.js
- https://github.com/VulnSageAgent/PoCs/tree/main/JavaScript/prototype-pollution/CVE-2025-57324
- https://github.com/parse-community/Parse-SDK-JS
