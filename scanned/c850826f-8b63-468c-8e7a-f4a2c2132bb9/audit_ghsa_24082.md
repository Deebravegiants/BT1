# [M] Possible information disclosure inside TreeGrid component with default data provider

## Summary
Severity: Medium
Advisory: GHSA-qfr3-323w-qv27
CVE: CVE-2022-29567
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-25
Source: https://github.com/advisories/GHSA-qfr3-323w-qv27
Type: github-advisory

## Affected
- Maven: `com.vaadin:vaadin` — affected >=14.8.5 <14.8.10
- Maven: `com.vaadin:vaadin` — affected >=22.0.6 <22.0.15
- Maven: `com.vaadin:vaadin` — affected >=23.0.0 <23.0.9
- Maven: `com.vaadin:vaadin-grid-flow` — affected >=14.8.5 <14.8.10
- Maven: `com.vaadin:vaadin-grid-flow` — affected >=22.0.6 <22.0.15
- Maven: `com.vaadin:vaadin-grid-flow` — affected >=23.0.0.beta2 <23.0.9

## Details
### Description

The default configuration of a TreeGrid component uses Object::toString as a key on the client-side and server communication in Vaadin 14.8.5 through 14.8.9, 22.0.6 through 22.0.14, 23.0.0.beta2 through 23.0.8 and 23.1.0.alpha1 through 23.1.0.alpha4, resulting in potential information disclosure of values that should not be available on the client-side.

## References
- https://github.com/vaadin/platform/security/advisories/GHSA-qfr3-323w-qv27
- https://nvd.nist.gov/vuln/detail/CVE-2022-29567
- https://github.com/vaadin/flow-components/pull/3046
- https://github.com/vaadin/platform
- https://vaadin.com/security/cve-2022-29567
