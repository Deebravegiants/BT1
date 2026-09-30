# [M] Directory traversal in development mode handler in Vaadin 14 and 15-17

## Summary
Severity: Medium
Advisory: GHSA-82mf-mmh7-hxp5
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-04-19
Source: https://github.com/advisories/GHSA-82mf-mmh7-hxp5
Type: github-advisory

## Affected
- Maven: `com.vaadin:vaadin-bom` — affected >=14.0.0 <14.4.3
- Maven: `com.vaadin:vaadin-bom` — affected >=15.0.0 <18.0.0

## Details
Improper URL validation in development mode handler in `com.vaadin:flow-server` versions 2.0.0 through 2.4.1 (Vaadin 14.0.0 through 14.4.2), and 3.0 prior to 5.0 (Vaadin 15 prior to 18) allows attacker to request arbitrary files stored outside of intended frontend resources folder.

- https://vaadin.com/security/cve-2020-36321

## References
- https://github.com/vaadin/platform/security/advisories/GHSA-82mf-mmh7-hxp5
- https://github.com/vaadin/platform
- https://vaadin.com/security/cve-2020-36321
