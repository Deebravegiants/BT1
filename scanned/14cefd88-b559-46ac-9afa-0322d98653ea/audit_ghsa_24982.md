# [H] Undertow vulnerable to Uncontrolled Resource Consumption

## Summary
Severity: High
Advisory: GHSA-vjxc-frw4-jmh5
CVE: CVE-2019-14888
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vjxc-frw4-jmh5
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=0 <2.0.29.Final

## Details
A vulnerability was found in the Undertow HTTP server in versions before 2.0.29 when listening on HTTPS. An attacker can target the HTTPS port to carry out a Denial Of Service (DOS) to make the service unavailable on SSL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14888
- https://access.redhat.com/errata/RHSA-2020:0729
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14888
- https://security.netapp.com/advisory/ntap-20220211-0001
