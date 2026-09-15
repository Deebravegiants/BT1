# [H] golang.org/x/crypto/ssh Man-in-the-Middle attack

## Summary
Severity: High
Advisory: GHSA-xhjq-w7xm-p8qj
CVE: CVE-2017-3204
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-07
Source: https://github.com/advisories/GHSA-xhjq-w7xm-p8qj
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.0.0-20170330155735-e4e2799dd7aa

## Details
The Go SSH library (golang.org/x/crypto/ssh) by default does not verify host keys, facilitating man-in-the-middle attacks if ClientConfig.HostKeyCallback is not set. Default behavior changed in commit e4e2799 to require explicitly registering a hostkey verification mechanism.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-3204
- https://github.com/golang/go/issues/19767
- https://github.com/golang/crypto/commit/e4e2799dd7aab89f583e1d898300d96367750991
- https://bridge.grumpy-troll.org/2017/04/golang-ssh-security
- https://go.dev/cl/340830
- https://go.dev/cl/38701
- https://go.dev/issue/19767
- https://go.googlesource.com/crypto/+/e4e2799dd7aab89f583e1d898300d96367750991
- https://godoc.org/golang.org/x/crypto/ssh
- https://pkg.go.dev/vuln/GO-2020-0013
- https://web.archive.org/web/20170423080311/https://www.securityfocus.com/bid/97481
- https://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2017-3204
