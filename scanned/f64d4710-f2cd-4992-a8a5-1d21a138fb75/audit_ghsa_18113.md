# [H] apidoc-core is vulnerable to prototype pollution

## Summary
Severity: High
Advisory: GHSA-5q53-78f2-6gf8
CVE: CVE-2025-57317
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-09-25
Source: https://github.com/advisories/GHSA-5q53-78f2-6gf8
Type: github-advisory

## Affected
- npm: `apidoc-core` — affected >=0

## Details
apidoc-core is the core parser library to generate apidoc result following the apidoc-spec. A Prototype Pollution vulnerability in the preProcess function of apidoc-core versions thru 0.15.0 allows attackers to inject properties on Object.prototype via supplying a crafted payload, causing denial of service (DoS) as the minimum consequence.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-57317
- https://github.com/OrangeShieldInfos/PoCs/tree/main/JavaScript/prototype-pollution/CVE-2025-57317
- https://github.com/VulnSageAgent/PoCs/blob/main/JavaScript/prototype-pollution/apidoc-core%400.15.0/index.js
- https://github.com/apidoc/apidoc-core
