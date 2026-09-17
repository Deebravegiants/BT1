# [M] Invalid HTTP requests in Reactor Netty HTTP Server may reveal access tokens

## Summary
Severity: Medium
Advisory: GHSA-7w4x-4h67-pgmv
CVE: CVE-2022-31684
CWE: CWE-200, CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-10-20
Source: https://github.com/advisories/GHSA-7w4x-4h67-pgmv
Type: github-advisory

## Affected
- Maven: `io.projectreactor.netty:reactor-netty-http` — affected >=1.0.11 <1.0.24

## Details
Reactor Netty HTTP Server, in versions 1.0.11 - 1.0.23, may request log headers in some cases of invalid HTTP requests. The logged headers may reveal valid access tokens to those with access to server logs. This may affect only invalid HTTP requests where logging at WARN level is enabled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-31684
- https://search.maven.org/artifact/io.projectreactor.netty/reactor-netty-http
- https://tanzu.vmware.com/security/cve-2022-31684
