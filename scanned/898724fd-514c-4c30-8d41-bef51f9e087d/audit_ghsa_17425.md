# [C] apidoc-core has a prototype pollution vulnerability

## Summary
Severity: Critical
Advisory: GHSA-6vj3-p34w-xxjp
CVE: CVE-2025-13158
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-26
Source: https://github.com/advisories/GHSA-6vj3-p34w-xxjp
Type: github-advisory

## Affected
- npm: `apidoc-core` — affected >=0.2.0

## Details
Prototype pollution vulnerability in apidoc-core versions 0.2.0 and all subsequent versions allows remote attackers to modify JavaScript object prototypes via malformed data structures, including the “define” property processed by the application, potentially leading to denial of service or unintended behavior in applications relying on the integrity of prototype chains. This affects the preProcess() function in api_group.js, api_param_title.js, api_use.js, and api_permission.js worker modules.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-13158
- https://github.com/apidoc/apidoc-core
- https://www.sonatype.com/security-advisories/cve-2025-13158
