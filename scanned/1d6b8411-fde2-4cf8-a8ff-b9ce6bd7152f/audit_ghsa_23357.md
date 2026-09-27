# [H] golang.org/x/net/html NULL Pointer Dereference vulnerability

## Summary
Severity: High
Advisory: GHSA-5p4h-3377-7w67
CVE: CVE-2018-17075
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-5p4h-3377-7w67
Type: github-advisory

## Affected
- Go: `golang.org/x/net` — affected >=0 <0.0.0-20180816102801-aaf60122140d

## Details
The html package (aka x/net/html) before 2018-07-13 in Go mishandles "in frameset" insertion mode, leading to a "panic: runtime error" for html.Parse of <template><object>, <template><applet>, or <template><marquee>. This is related to HTMLTreeBuilder.cpp in WebKit.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17075
- https://github.com/golang/go/issues/27016
- https://github.com/golang/net/commit/aaf60122140d3fcf75376d319f0554393160eb50
- https://bugs.chromium.org/p/chromium/issues/detail?id=829668
- https://github.com/golang/go
- https://go-review.googlesource.com/c/net/+/94838/9/html/parse.go#1906
- https://go.dev/cl/123776
- https://go.dev/issue/27016
- https://go.googlesource.com/net/+/aaf60122140d3fcf75376d319f0554393160eb50
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LREEWY6KNLHRWFZ7OT4HVLMVVCGGUHON
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UKRCI7WIOCOCD3H7NXWRGIRABTQOZOBK
- https://pkg.go.dev/vuln/GO-2021-0078
