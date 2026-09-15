# [M] Reactor Netty HTTP Client Leaks Credentials On Protocol Downgrade Redirect

## Summary
Severity: Medium
Advisory: GHSA-pfc9-2cqg-9wq6
CVE: CVE-2026-41715
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-pfc9-2cqg-9wq6
Type: github-advisory

## Affected
- Maven: `io.projectreactor.netty:reactor-netty` — affected >=1.3.0 <1.3.6
- Maven: `io.projectreactor.netty:reactor-netty` — affected >=1.2.0 <1.2.18
- Maven: `io.projectreactor.netty:reactor-netty` — affected >=1.1.0
- Maven: `io.projectreactor.netty:reactor-netty` — affected >=1.0.0

## Details
In specific scenarios involving HTTP redirects from a secure to an insecure endpoint, the Reactor Netty HTTP client may leak credentials. In order for this to happen, the HTTP client must have been explicitly configured to follow redirects.

Affected versions:
Reactor Netty 1.0.0 through 1.0.51; 1.1.0 through 1.1.35; 1.2.0 through 1.2.17; 1.3.0 through 1.3.5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41715
- https://github.com/reactor/reactor-netty/commit/e7ef551eead84ba465324531683fafa03ab96ee9
- https://github.com/reactor/reactor-netty
- https://github.com/reactor/reactor-netty/releases/tag/v1.2.18
- https://github.com/reactor/reactor-netty/releases/tag/v1.3.6
- https://spring.io/security/cve-2026-41715
