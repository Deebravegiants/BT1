# [M] Vaadin vulnerable to possible information disclosure in non visible components.

## Summary
Severity: Medium
Advisory: GHSA-5f9v-mv5g-jh5q
CVE: CVE-2023-25499
CWE: CWE-200, CWE-201
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-06-22
Source: https://github.com/advisories/GHSA-5f9v-mv5g-jh5q
Type: github-advisory

## Affected
- Maven: `com.vaadin:vaadin` — affected >=10.0.0 <10.0.23
- Maven: `com.vaadin:vaadin` — affected >=11.0.0 <14.10.1
- Maven: `com.vaadin:vaadin` — affected >=23.0.0 <23.3.13
- Maven: `com.vaadin:vaadin` — affected >=24.0.0 <24.0.6
- Maven: `com.vaadin:vaadin` — affected >=24.1.0.alpha1 <24.1.0
- Maven: `com.vaadin:flow-server` — affected >=1.0.0 <1.0.20
- Maven: `com.vaadin:flow-server` — affected >=1.1.0 <2.8.10
- Maven: `com.vaadin:flow-server` — affected >=3.0.0 <9.1.1
- Maven: `com.vaadin:flow-server` — affected >=23.0.0 <23.3.11
- Maven: `com.vaadin:flow-server` — affected >=24.0.0 <24.0.8
- Maven: `com.vaadin:flow-server` — affected >=24.1.0.alpha1 <24.1.0

## Details
### Description
When adding non-visible components to the UI in server side, content is sent to the browser in Vaadin 10.0.0 through 10.0.22, 11.0.0 through 14.10.0, 15.0.0 through 22.0.28, 23.0.0 through 23.3.12, 24.0.0 through 24.0.5 and 24.1.0.alpha1 to 24.1.0.beta1, resulting in potential information disclosure.

* https://vaadin.com/security/cve-2023-25499

## References
- https://github.com/vaadin/platform/security/advisories/GHSA-5f9v-mv5g-jh5q
- https://nvd.nist.gov/vuln/detail/CVE-2023-25499
- https://github.com/vaadin/flow/pull/15885
- https://github.com/vaadin/platform
- https://vaadin.com/security/CVE-2023-25499
