# [H] Formio improperly authorized permission elevation through specially crafted request path

## Summary
Severity: High
Advisory: GHSA-m654-769v-qjv7
CVE: CVE-2025-67718
CWE: CWE-178
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-m654-769v-qjv7
Type: github-advisory

## Affected
- npm: `formio` — affected >=0 <3.5.7
- npm: `formio` — affected >=4.0.0-rc.1 <4.4.3

## Details
# Security Advisory: Unauthorized permission elevation through specially crafted request path

**Summary:** A flaw in path handling could allow an attacker to access protected API endpoints by sending a crafted request path. This issue could result in unauthorized data disclosure under certain configurations.

**Impact:** In affected configurations, an unauthenticated or unauthorized request could retrieve data from endpoints that should be protected.

**Affected versions:** 
<= 3.5.6
<= 4.4.2

**Fixed in:** 
3.5.7
4.4.3

**Mitigation / Workarounds:** 
Upgrade to 3.5.7  or later. 

**Disclosure timeline:** 
Discovered 2025-05-22; fixed 2025-05-30; publicly disclosed 2025-12.

## References
- https://github.com/formio/formio/security/advisories/GHSA-m654-769v-qjv7
- https://nvd.nist.gov/vuln/detail/CVE-2025-67718
- https://github.com/formio/formio/commit/1665b7c99e3cf3246db7ff0b4ff732231dc6903b
- https://github.com/formio/formio/commit/1836bdd9f55f5888ff397c257b2108c09d3de478
- https://github.com/formio/formio
