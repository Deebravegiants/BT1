# [M] Reflected cross-site scripting in vaadin-menu-bar webjar resources in Vaadin 14

## Summary
Severity: Medium
Advisory: GHSA-93c4-vf86-3rj7
CVE: CVE-2021-33611
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-11-03
Source: https://github.com/advisories/GHSA-93c4-vf86-3rj7
Type: github-advisory

## Affected
- Maven: `com.vaadin:vaadin-bom` — affected >=14.0.0 <14.4.5
- Maven: `org.webjars.bowergithub.vaadin:vaadin-menu-bar` — affected >=1.0.0 <1.2.1

## Details
Missing output sanitization in test sources in `org.webjars.bowergithub.vaadin:vaadin-menu-bar` versions 1.0.0 through 1.2.0 (Vaadin 14.0.0 through 14.4.4) allows remote attackers to execute malicious JavaScript in browser by opening crafted URL.

## References
- https://github.com/vaadin/platform/security/advisories/GHSA-93c4-vf86-3rj7
- https://nvd.nist.gov/vuln/detail/CVE-2021-33611
- https://github.com/vaadin/vaadin-menu-bar/pull/126
- https://github.com/vaadin/platform
- https://vaadin.com/security/cve-2021-33611
