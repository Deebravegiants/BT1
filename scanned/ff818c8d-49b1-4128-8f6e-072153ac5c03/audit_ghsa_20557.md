# [H] golang.org/x/net/http2 allows uncontrolled memory consumption

## Summary
Severity: High
Advisory: GHSA-vc3p-29h2-gpcp
CVE: CVE-2021-44716
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-02
Source: https://github.com/advisories/GHSA-vc3p-29h2-gpcp
Type: github-advisory

## Affected
- Go: `golang.org/x/net/http2` — affected >=0 <0.0.0-20211209124913-491a49abca63

## Details
net/http in Go before 1.16.12 and 1.17.x before 1.17.5 allows uncontrolled memory consumption in the header canonicalization cache via HTTP/2 requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44716
- https://go.dev/cl/369794
- https://go.dev/issue/50058
- https://groups.google.com/g/golang-announce/c/hcmEScgc00k
- https://lists.debian.org/debian-lts-announce/2022/01/msg00016.html
- https://lists.debian.org/debian-lts-announce/2022/01/msg00017.html
- https://pkg.go.dev/vuln/GO-2022-0288
- https://security.gentoo.org/glsa/202208-02
- https://security.netapp.com/advisory/ntap-20220121-0002
