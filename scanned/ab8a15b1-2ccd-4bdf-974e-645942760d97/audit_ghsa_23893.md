# [M] golang.org/x/net/http/httpguts vulnerable to Uncontrolled Recursion

## Summary
Severity: Medium
Advisory: GHSA-h86h-8ppg-mxmh
CVE: CVE-2021-31525
CWE: CWE-674
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h86h-8ppg-mxmh
Type: github-advisory

## Affected
- Go: `golang.org/x/net` — affected >=0 <0.0.0-20210428140749-89ef3d95e781

## Details
golang.org/x/net/http/httpguts in Go before 1.15.12 and 1.16.x before 1.16.4 allows remote attackers to cause a denial of service (panic) via a large header to ReadRequest or ReadResponse. Server, Transport, and Client can each be affected in some configurations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-31525
- https://github.com/golang/go/issues/45710
- https://github.com/golang/go
- https://go.dev/cl/313069
- https://go.dev/issue/45710
- https://go.googlesource.com/net/+/89ef3d95e781148a0951956029c92a211477f7f9
- https://groups.google.com/g/golang-announce/c/cu9SP4eSXMc
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ISRZZ6NY5R2TBYE72KZFOCO25TEUQTBF
- https://pkg.go.dev/vuln/GO-2022-0236
- https://security.gentoo.org/glsa/202208-02
