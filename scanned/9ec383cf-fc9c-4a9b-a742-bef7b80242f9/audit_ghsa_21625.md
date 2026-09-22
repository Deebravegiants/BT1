# [H] Improper Handling of Exceptional Conditions and Improper Input Validation in Reactor Netty

## Summary
Severity: High
Advisory: GHSA-hp5x-rqf7-43vf
CVE: CVE-2020-5403
CWE: CWE-20, CWE-755
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-hp5x-rqf7-43vf
Type: github-advisory

## Affected
- Maven: `io.projectreactor.netty:reactor-netty-http` — affected >=0.9.3 <0.9.5

## Details
Reactor Netty HttpServer, versions 0.9.3 and 0.9.4, is exposed to a URISyntaxException that causes the connection to be closed prematurely instead of producing a 400 response.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-5403
- https://pivotal.io/security/cve-2020-5403
