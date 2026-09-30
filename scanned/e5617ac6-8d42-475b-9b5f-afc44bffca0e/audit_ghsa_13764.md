# [H] In Reactor Netty HTTP Server a malicious user can send a request using a specially crafted URL that can lead to a directory traversal attack

## Summary
Severity: High
Advisory: GHSA-xjhv-p3fv-x24r
CVE: CVE-2023-34062
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-11-15
Source: https://github.com/advisories/GHSA-xjhv-p3fv-x24r
Type: github-advisory

## Affected
- Maven: `io.projectreactor.netty:reactor-netty-http` — affected >=1.1.0 <1.1.13
- Maven: `io.projectreactor.netty:reactor-netty-http` — affected >=1.0.0 <1.0.39

## Details
In Reactor Netty HTTP Server, versions 1.1.x prior to 1.1.13 and versions 1.0.x prior to 1.0.39, a malicious user can send a request using a specially crafted URL that can lead to a directory traversal attack.

Specifically, an application is vulnerable if Reactor Netty HTTP Server is configured to serve static resources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34062
- https://github.com/reactor/reactor-netty/commit/b1dd46b9a424ca27f7f770be6561faa84d812e5b
- https://github.com/reactor/reactor-netty
- https://spring.io/security/cve-2023-34062
