# [H] github.com/buger/jsonparser has a denial of service vulnerability

## Summary
Severity: High
Advisory: GHSA-6g7g-w4f8-9c9x
CVE: CVE-2026-32285
CWE: CWE-125, CWE-129
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-6g7g-w4f8-9c9x
Type: github-advisory

## Affected
- Go: `github.com/buger/jsonparser` — affected >=0 <1.1.2

## Details
The Delete function fails to properly validate offsets when processing malformed JSON input. This can lead to a negative slice index and a runtime panic, allowing a denial of service attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-32285
- https://github.com/buger/jsonparser/issues/275
- https://github.com/golang/vulndb/issues/4514
- https://github.com/buger/jsonparser/pull/276
- https://github.com/buger/jsonparser/commit/a69e7e01cd4ad67bdfd3ac2c080b9212af16f4b0
- https://github.com/buger/jsonparser
- https://github.com/buger/jsonparser/releases/tag/v1.1.2
- https://pkg.go.dev/vuln/GO-2026-4514
- https://securityinfinity.com/research/buger-jsonparser-negative-slice-panic-dos-2026
