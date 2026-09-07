# [H] golang.org/x/net/html has Improper Restriction of Operations within the Bounds of a Memory Buffer

## Summary
Severity: High
Advisory: GHSA-fcf9-6fv2-fc5v
CVE: CVE-2018-17143
CWE: CWE-119
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-fcf9-6fv2-fc5v
Type: github-advisory

## Affected
- Go: `golang.org/x/net` — affected >=0 <0.0.0-20180921000356-2f5d2388922f

## Details
The html package (aka x/net/html) through 2018-09-17 in Go mishandles <template><tBody><isindex/action=0>, leading to a "panic: runtime error" in inBodyIM in parse.go during an html.Parse call

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17143
- https://github.com/golang/go/issues/27704
- https://github.com/golang/go
- https://go-review.googlesource.com/c/net/+/136575
- https://go.dev/issue/27704
- https://go.googlesource.com/net/+/2f5d2388922f370f4355f327fcf4cfe9f5583908
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LREEWY6KNLHRWFZ7OT4HVLMVVCGGUHON
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UKRCI7WIOCOCD3H7NXWRGIRABTQOZOBK
- https://pkg.go.dev/vuln/GO-2022-0193
