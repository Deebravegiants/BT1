# [H] golang.org/x/crypto/ssh NULL Pointer Dereference vulnerability

## Summary
Severity: High
Advisory: GHSA-3vm4-22fp-5rfm
CVE: CVE-2020-29652
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3vm4-22fp-5rfm
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.0.0-20201216223049-8b5274cf687f

## Details
A nil pointer dereference in the golang.org/x/crypto/ssh component through v0.0.0-20201203163018-be400aefbc4c for Go allows remote attackers to cause a denial of service against SSH servers. An attacker can craft an authentication request message for the `gssapi-with-mic` method which will cause NewServerConn to panic via a nil pointer dereference if ServerConfig.GSSAPIWithMICConfig is nil.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-29652
- https://go-review.googlesource.com/c/crypto/+/278852
- https://go.dev/cl/278852
- https://go.googlesource.com/crypto/+/8b5274cf687fd9316b4108863654cc57385531e8
- https://groups.google.com/g/golang-announce/c/ouZIlBimOsE?pli=1
- https://lists.apache.org/thread.html/r68032132c0399c29d6cdc7bd44918535da54060a10a12b1591328bff@%3Cnotifications.skywalking.apache.org%3E
- https://pkg.go.dev/vuln/GO-2021-0227
