# [H] Regular expression Denial of Service (ReDoS) in EmailValidator class in V7 compatibility module in Vaadin 8

## Summary
Severity: High
Advisory: GHSA-jfmf-w293-8xr8
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-10-13
Source: https://github.com/advisories/GHSA-jfmf-w293-8xr8
Type: github-advisory

## Affected
- Maven: `com.vaadin:vaadin-bom` — affected >=8.0.0 <8.13.0

## Details
Unsafe validation RegEx in `EmailValidator` component in `com.vaadin:vaadin-compatibility-server` versions 8.0.0 through 8.12.4 (Vaadin versions 8.0.0 through 8.12.4) allows attackers to cause uncontrolled resource consumption by submitting malicious email addresses.

## References
- https://github.com/vaadin/framework/security/advisories/GHSA-jfmf-w293-8xr8
- https://github.com/vaadin/framework
- https://vaadin.com/security/cve-2021-31409
