# [M] Vaadin Vulnerable to Authentication Bypass When Accessing the /VAADIN Endpoint Without a Trailing Slash

## Summary
Severity: Medium
Advisory: GHSA-rjgh-wgc7-m37j
CVE: CVE-2026-2742
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:L/S:N/AU:Y/R:A/V:D/RE:L/U:Amber (CVSS_V4)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-rjgh-wgc7-m37j
Type: github-advisory

## Affected
- Maven: `com.vaadin:flow-server` — affected >=0 <14.14.1
- Maven: `com.vaadin:flow-server` — affected >=23.0.0 <23.6.7
- Maven: `com.vaadin:flow-server` — affected >=24.0.0 <24.9.8
- Maven: `com.vaadin:flow-server` — affected >=25.0.0 <25.0.2
- Maven: `com.vaadin:vaadin` — affected >=25.0.0 <25.0.2
- Maven: `com.vaadin:vaadin` — affected >=24.0.0 <24.9.8
- Maven: `com.vaadin:vaadin` — affected >=23.0.0 <23.6.7
- Maven: `com.vaadin:vaadin` — affected >=0 <14.14.1

## Details
An authentication bypass vulnerability exists in Vaadin 14.0.0 through 14.14.0, 23.0.0 through 23.6.6, 24.0.0 through 24.9.7 and 25.0.0 through 25.0.1, applications using Spring Security due to inconsistent path pattern matching of reserved framework paths.

Accessing the /VAADIN endpoint without a trailing slash bypasses security filters, and allowing unauthenticated users to trigger framework initialization and create sessions without proper authorization.

Users of affected versions using Spring Security should upgrade as follows: 14.0.0-14.14.0 upgrade to 14.14.1, 23.0.0-23.6.6 to 23.6.7, 24.0.0 - 24.9.7 to 24.9.8, and 25.0.0-25.0.1 upgrade to 25.0.2 or newer.

Please note that Vaadin versions 10-13 and 15-22 are no longer supported and users should update either to the latest 14, 23, 24, 25 version.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2742
- https://github.com/vaadin/flow/pull/22998
- https://github.com/vaadin/flow/pull/23033
- https://github.com/vaadin/flow/pull/23034
- https://github.com/vaadin/flow/pull/23037
- https://github.com/vaadin/flow/pull/23052
- https://github.com/vaadin/flow/pull/23057
- https://github.com/vaadin/flow
- https://vaadin.com/security/cve-2026-2742
