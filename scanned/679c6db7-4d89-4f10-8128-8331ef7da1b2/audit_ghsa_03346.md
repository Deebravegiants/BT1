# [M] Server session is not invalidated when logout() helper method of Authentication module is used in Vaadin 18-19

## Summary
Severity: Medium
Advisory: GHSA-6hgr-2g6q-3rmc
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-04-22
Source: https://github.com/advisories/GHSA-6hgr-2g6q-3rmc
Type: github-advisory

## Affected
- Maven: `com.vaadin:flow-client` — affected >=5.0.0 <6.0.5

## Details
`Authentication.logout()` helper in `com.vaadin:flow-client` versions 5.0.0 prior to 6.0.0 (Vaadin 18), and 6.0.0 through 6.0.4 (Vaadin 19.0.0 through 19.0.3) uses incorrect HTTP method, which, in combination with Spring Security CSRF protection, allows local attackers to access Fusion endpoints after the user attempted to log out.

- https://vaadin.com/security/cve-2021-31408

## References
- https://github.com/vaadin/flow/security/advisories/GHSA-6hgr-2g6q-3rmc
- https://github.com/vaadin/flow/pull/10577
- https://github.com/vaadin/flow/commit/815b967fc84fefa8d3a4d72b9a036f48b0d96326
- https://github.com/vaadin/flow
- https://vaadin.com/security/cve-2021-31408
