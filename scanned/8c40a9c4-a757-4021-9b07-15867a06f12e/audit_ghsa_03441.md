# [M] Stored cross-site scripting in Grid component in Vaadin 7 and 8

## Summary
Severity: Medium
Advisory: GHSA-q74r-4xw3-ppx9
CVE: CVE-2019-25028
CWE: CWE-79, CWE-80
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-04-19
Source: https://github.com/advisories/GHSA-q74r-4xw3-ppx9
Type: github-advisory

## Affected
- Maven: `com.vaadin:vaadin-bom` — affected >=7.4.0 <7.7.20
- Maven: `com.vaadin:vaadin-bom` — affected >=8.0.0 <8.8.5
- Maven: `com.vaadin:vaadin-server` — affected >=7.4.0 <7.7.20
- Maven: `com.vaadin:vaadin-server` — affected >=8.0.0 <8.8.5

## Details
Missing variable sanitization in `Grid` component in `com.vaadin:vaadin-server` versions 7.4.0 through 7.7.19 (Vaadin 7.4.0 through 7.7.19), and 8.0.0 through 8.8.4 (Vaadin 8.0.0 through 8.8.4) allows attacker to inject malicious JavaScript via unspecified vector.

- https://vaadin.com/security/cve-2019-25028

## References
- https://github.com/vaadin/framework/security/advisories/GHSA-q74r-4xw3-ppx9
- https://nvd.nist.gov/vuln/detail/CVE-2019-25028
- https://github.com/vaadin/framework/pull/11644
- https://github.com/vaadin/framework/pull/11645
- https://vaadin.com/security/cve-2019-25028
