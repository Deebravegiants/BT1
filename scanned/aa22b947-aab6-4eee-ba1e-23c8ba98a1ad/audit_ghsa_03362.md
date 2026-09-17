# [H] Regular expression denial of service (ReDoS) in EmailField component in Vaadin 14 and 15-17

## Summary
Severity: High
Advisory: GHSA-2wqp-jmcc-mc77
CVE: CVE-2021-31405
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-04-19
Source: https://github.com/advisories/GHSA-2wqp-jmcc-mc77
Type: github-advisory

## Affected
- Maven: `com.vaadin:vaadin-bom` — affected >=14.0.6 <14.4.4
- Maven: `com.vaadin:vaadin-bom` — affected >=15.0.0 <17.0.11

## Details
Unsafe validation RegEx in `EmailField` component in `com.vaadin:vaadin-text-field-flow` versions 2.0.4 through 2.3.2 (Vaadin 14.0.6 through 14.4.3), and 3.0.0 through 4.0.2 (Vaadin 15.0.0 through 17.0.10) allows attackers to cause uncontrolled resource consumption by submitting malicious email addresses.

- https://vaadin.com/security/cve-2021-31405

## References
- https://github.com/vaadin/platform/security/advisories/GHSA-2wqp-jmcc-mc77
- https://nvd.nist.gov/vuln/detail/CVE-2021-31405
- https://github.com/vaadin/flow-components/pull/442
- https://vaadin.com/security/cve-2021-31405
