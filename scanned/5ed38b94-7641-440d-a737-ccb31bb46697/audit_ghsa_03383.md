# [M] Reflected cross-site scripting in default RouteNotFoundError view in Vaadin 10 and 11-13

## Summary
Severity: Medium
Advisory: GHSA-jqj4-r483-4gvr
CWE: CWE-81
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-04-19
Source: https://github.com/advisories/GHSA-jqj4-r483-4gvr
Type: github-advisory

## Affected
- Maven: `com.vaadin:vaadin-bom` — affected >=10.0.0 <10.0.14
- Maven: `com.vaadin:vaadin-bom` — affected >=11.0.0 <13.0.6

## Details
Missing output sanitization in default `RouteNotFoundError` view in `com.vaadin:flow-server` versions 1.0.0 through 1.0.10 (Vaadin 10.0.0 through 10.0.13), and 1.1.0 through 1.4.2 (Vaadin 11.0.0 through 13.0.5) allows attacker to execute malicious JavaScript via crafted URL.

- https://vaadin.com/security/cve-2019-25027

## References
- https://github.com/vaadin/platform/security/advisories/GHSA-jqj4-r483-4gvr
- https://github.com/vaadin/platform
- https://vaadin.com/security/cve-2019-25027
