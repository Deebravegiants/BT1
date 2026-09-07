# [H] OSGi applications using Vaadin 12-14 and 19 vulnerable to server classes and resources exposure

## Summary
Severity: High
Advisory: GHSA-25xc-jwfq-39jw
CVE: CVE-2021-31407
CWE: CWE-402, CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2021-04-19
Source: https://github.com/advisories/GHSA-25xc-jwfq-39jw
Type: github-advisory

## Affected
- Maven: `com.vaadin:flow-server` — affected >=1.2.0 <2.4.8
- Maven: `com.vaadin:flow-server` — affected >=6.0.0 <6.0.1

## Details
Vulnerability in OSGi integration in `com.vaadin:flow-server` versions 1.2.0 through 2.4.7 (Vaadin 12.0.0 through 14.4.9), and 6.0.0 through 6.0.1 (Vaadin 19.0.0) allows attacker to access application classes and resources on the server via crafted HTTP request.

- https://vaadin.com/security/cve-2021-31407

## References
- https://github.com/vaadin/flow/security/advisories/GHSA-25xc-jwfq-39jw
- https://nvd.nist.gov/vuln/detail/CVE-2021-31407
- https://github.com/vaadin/osgi/issues/50
- https://github.com/vaadin/flow/pull/10229
- https://github.com/vaadin/flow/pull/10269
- https://github.com/vaadin/flow
- https://vaadin.com/security/cve-2021-31407
