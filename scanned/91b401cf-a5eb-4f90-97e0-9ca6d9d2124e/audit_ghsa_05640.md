# [M] evershop allows unauthenticated attackers to force server to initiate HTTP request via "GET /images" API

## Summary
Severity: Medium
Advisory: GHSA-vp8w-wj4m-3r7j
CVE: CVE-2025-67427
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-vp8w-wj4m-3r7j
Type: github-advisory

## Affected
- npm: `@evershop/evershop` — affected >=0

## Details
A Blind Server-Side Request Forgery (SSRF) vulnerability in evershop 2.1.0 and prior allows unauthenticated attackers to force the server to initiate an HTTP request via the "GET /images" API. The vulnerability occurs due to insufficient validation of the "src" query parameter, which permits arbitrary HTTP or HTTPS URIs, resulting in unexpected requests against internal and external networks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67427
- https://github.com/dos-m0nk3y/CVE/tree/main/CVE-2025-67427
- https://github.com/evershopcommerce/evershop
- https://pages.dos-m0nk3y.com/blog/EverShop%202.1.0%20-%20Unauthenticated%20DoS/#server-side-request-forgery-ssrf-cve-2025-67427
