# [H] mpregular vulnerable to prototype pollution

## Summary
Severity: High
Advisory: GHSA-xx4g-r65p-3qf2
CVE: CVE-2025-57323
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-09-24
Source: https://github.com/advisories/GHSA-xx4g-r65p-3qf2
Type: github-advisory

## Affected
- npm: `mpregular` — affected >=0

## Details
mpregular is a package that provides a small program development framework based on RegularJS. A Prototype Pollution vulnerability in the mp.addEventHandler function of mpregular version 0.2.0 and before allows attackers to inject properties on Object.prototype via supplying a crafted payload, causing denial of service (DoS) as the minimum consequence.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-57323
- https://github.com/VulnSageAgent/PoCs/blob/main/JavaScript/prototype-pollution/mpregular%400.2.0/index.js
- https://github.com/VulnSageAgent/PoCs/tree/main/JavaScript/prototype-pollution/CVE-2025-57323
- https://github.com/regularjs/regular
