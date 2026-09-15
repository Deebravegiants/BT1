# [H] evershop allows unauthenticated attackers to exhaust application server's resources via "GET /images" API

## Summary
Severity: High
Advisory: GHSA-m2q5-xhqg-92r2
CVE: CVE-2025-67419
CWE: CWE-1050
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-m2q5-xhqg-92r2
Type: github-advisory

## Affected
- npm: `@evershop/evershop` — affected >=0

## Details
A Denial of Service (DoS) vulnerability in evershop 2.1.0 and prior allows unauthenticated attackers to exhaust the application server's resources via the "GET /images" API. The application fails to limit the height of the use-element shadow tree or the dimensions of pattern tiles during the processing of SVG files, resulting in unbounded resource consumption and system-wide denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67419
- https://github.com/dos-m0nk3y/CVE/tree/main/CVE-2025-67419
- https://github.com/evershopcommerce/evershop
- https://pages.dos-m0nk3y.com/blog/EverShop%202.1.0%20-%20Unauthenticated%20DoS/#denial-of-service-dos-cve-2025-67419
