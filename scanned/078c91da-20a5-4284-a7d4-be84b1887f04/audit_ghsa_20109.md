# [H] socks Infinite Loop vulnerability

## Summary
Severity: High
Advisory: GHSA-gxgj-xjcw-fv9p
CVE: CVE-2013-10005
CWE: CWE-835
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-gxgj-xjcw-fv9p
Type: github-advisory

## Affected
- Go: `github.com/btcsuite/go-socks` — affected >=0 <0.0.0-20130808000456-233bccbb1abe
- Go: `github.com/btcsuitereleases/go-socks` — affected >=0 <0.0.0-20130808000456-233bccbb1abe

## Details
The `RemoteAddr` and `LocalAddr` methods on the returned `net.Conn` may call themselves, leading to an infinite loop which will crash the program due to a stack overflow.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-10005
- https://github.com/btcsuite/go-socks/commit/233bccbb1abe02f05750f7ace66f5bffdb13defc
- https://github.com/btcsuite/go-socks
- https://pkg.go.dev/vuln/GO-2020-0024
