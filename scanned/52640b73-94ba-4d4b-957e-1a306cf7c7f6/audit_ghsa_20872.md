# [H] golang.org/x/net/http2 Denial of Service vulnerability

## Summary
Severity: High
Advisory: GHSA-69cg-p879-7622
CVE: CVE-2022-27664
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-07
Source: https://github.com/advisories/GHSA-69cg-p879-7622
Type: github-advisory

## Affected
- Go: `golang.org/x/net` — affected >=0 <0.0.0-20220906165146-f3363e06e74c
- Go: `golang.org/x/net/http2` — affected >=0 <0.0.0-20220906165146-f3363e06e74c

## Details
In net/http in Go before 1.18.6 and 1.19.x before 1.19.1, attackers can cause a denial of service because an HTTP/2 connection can hang during closing if shutdown were preempted by a fatal error.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27664
- https://cs.opensource.google/go/x/net
- https://go.dev/cl/428735
- https://go.dev/issue/54658
- https://groups.google.com/g/golang-announce
- https://groups.google.com/g/golang-announce/c/x49AQzIVX-s
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JXKTHIGE5F576MAPFYCIJXNRGBSPISUF
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TXS2OQ57KZC5XZKK5UW4SYKPVQAHIOJX
- https://pkg.go.dev/vuln/GO-2022-0969
- https://security.gentoo.org/glsa/202209-26
- https://security.netapp.com/advisory/ntap-20220923-0004
