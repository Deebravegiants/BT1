# [M] Possible route enumeration in production mode via RouteNotFoundError view in Vaadin 10, 11-14, and 15-19

## Summary
Severity: Medium
Advisory: GHSA-qrg9-f472-qwfm
CVE: CVE-2021-31412
CWE: CWE-1295, CWE-20, CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-06-28
Source: https://github.com/advisories/GHSA-qrg9-f472-qwfm
Type: github-advisory

## Affected
- Maven: `com.vaadin:vaadin-bom` — affected >=10.0.0 <10.0.19
- Maven: `com.vaadin:vaadin-bom` — affected >=11.0.0 <14.6.2
- Maven: `com.vaadin:vaadin-bom` — affected >=15.0.0 <19.0.9

## Details
Improper sanitization of path in default `RouteNotFoundError` view in `com.vaadin:flow-server` versions 1.0.0 through 1.0.14 (Vaadin 10.0.0 through 10.0.18), 1.1.0 prior to 2.0.0 (Vaadin 11 prior to 14), 2.0.0 through 2.6.1 (Vaadin 14.0.0 through 14.6.1), and 3.0.0 through 6.0.9 (Vaadin 15.0.0 through 19.0.8) allows network attacker to enumerate all available routes via crafted HTTP request when application is running in production mode and no custom handler for `NotFoundException` is provided.

- https://vaadin.com/security/cve-2021-31412

## References
- https://github.com/vaadin/platform/security/advisories/GHSA-qrg9-f472-qwfm
- https://nvd.nist.gov/vuln/detail/CVE-2021-31412
- https://github.com/vaadin/flow/pull/11107
- https://vaadin.com/security/cve-2021-31412
