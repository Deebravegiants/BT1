# [M] github.com/pires/go-proxyproto denial of service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fqh4-rh59-xhvf
CVE: CVE-2021-23351
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-fqh4-rh59-xhvf
Type: github-advisory

## Affected
- Go: `github.com/pires/go-proxyproto` — affected >=0 <0.5.0

## Details
The package `github.com/pires/go-proxyproto` before 0.5.0 are vulnerable to Denial of Service (DoS) via the `parseVersion1()` function. The reader in this package is a default `bufio.Reader` wrapping a `net.Conn`. It will read from the connection until it finds a newline. Since no limits are implemented in the code, a deliberately malformed V1 header could be used to exhaust memory in a server process using this code - and create a DoS. This can be exploited by sending a stream starting with PROXY and continuing to send data (which does not contain a newline) until the target stops acknowledging. The risk here is small, because only trusted sources should be allowed to send proxy protocol headers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23351
- https://github.com/pires/go-proxyproto/issues/69
- https://github.com/pires/go-proxyproto/pull/71
- https://github.com/pires/go-proxyproto/commit/7f48261db810703d173f27f3309a808cc2b49b8b
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4BNVGJMVI3ZTZ675EFPUHPGXCKCGSX46
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/C36IBVOZXRTWM7MGTRUTOM56P5RR74VU
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMPIRESGOPROXYPROTO-1081577
