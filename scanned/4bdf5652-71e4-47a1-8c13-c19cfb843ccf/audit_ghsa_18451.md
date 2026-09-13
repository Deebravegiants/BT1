# [M] Reactor Netty HTTP is vulnerable to credential leaks during chained redirects

## Summary
Severity: Medium
Advisory: GHSA-4q2v-9p7v-3v22
CVE: CVE-2025-22227
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-07-16
Source: https://github.com/advisories/GHSA-4q2v-9p7v-3v22
Type: github-advisory

## Affected
- Maven: `io.projectreactor.netty:reactor-netty-http` — affected >=1.3.0-M1 <1.3.0-M5
- Maven: `io.projectreactor.netty:reactor-netty-http` — affected >=0 <1.2.8

## Details
In some specific scenarios with chained redirects, Reactor Netty HTTP client leaks credentials. In order for this to happen, the HTTP client must have been explicitly configured to follow redirects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-22227
- https://github.com/reactor/reactor-netty/commit/522892307ea89bf24fe634e8bfea35728c9bf411
- https://github.com/reactor/reactor-netty
- https://spring.io/security/cve-2025-22227
