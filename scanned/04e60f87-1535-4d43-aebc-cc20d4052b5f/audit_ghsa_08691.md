# [M] Go Net HTML parser is vulnerable to denial of service

## Summary
Severity: Medium
Advisory: GHSA-5cv4-jp36-h3mw
CVE: CVE-2026-25680
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-5cv4-jp36-h3mw
Type: github-advisory

## Affected
- Go: `golang.org/x/net` — affected >=0 <0.55.0

## Details
In Go Net (`golang.org/x/net`) before verion 0.55.0, parsing arbitrary HTML can consume excessive CPU time, possibly leading to denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-25680
- https://go.dev/cl/781702
- https://go.dev/issue/79573
- https://go.googlesource.com/net/+/08be507abce89191d78cd49da60f4501fc910472
- https://go.googlesource.com/net/+/refs/tags/v0.55.0
- https://groups.google.com/g/golang-announce/c/iI-mYSI0lu8
- https://pkg.go.dev/vuln/GO-2026-5028
- cs.opensource.google/go/x/net
