# [H] csvjson vulnerable to prototype injection

## Summary
Severity: High
Advisory: GHSA-xq4f-3jxp-qv6m
CVE: CVE-2025-57318
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-09-24
Source: https://github.com/advisories/GHSA-xq4f-3jxp-qv6m
Type: github-advisory

## Affected
- npm: `csvjson` — affected >=0

## Details
A Prototype Pollution vulnerability in the toCsv function of csvjson versions thru 5.1.0 allows attackers to inject properties on Object.prototype via supplying a crafted payload, causing denial of service (DoS) as the minimum consequence.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-57318
- https://github.com/VulnSageAgent/PoCs/blob/main/JavaScript/prototype-pollution/csvjson%405.1.0/index.js
- https://github.com/VulnSageAgent/PoCs/tree/main/JavaScript/prototype-pollution/CVE-2025-57318
- https://github.com/pradeep-mishra/csvjson
