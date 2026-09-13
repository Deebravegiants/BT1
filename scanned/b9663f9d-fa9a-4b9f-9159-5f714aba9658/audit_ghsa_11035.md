# [H] Denial of service in github.com/shamaton/msgpack

## Summary
Severity: High
Advisory: GHSA-h9q6-hc68-35rp
CVE: CVE-2026-32284
CWE: CWE-125
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-h9q6-hc68-35rp
Type: github-advisory

## Affected
- Go: `github.com/shamaton/msgpack/v2` — affected >=0
- Go: `github.com/shamaton/msgpack/v3` — affected >=0

## Details
The msgpack decoder fails to properly validate the input buffer length when processing truncated fixext data (format codes 0xd4-0xd8). This can lead to an out-of-bounds read and a runtime panic, allowing a denial of service attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-32284
- https://github.com/golang/vulndb/issues/4513
- https://github.com/shamaton/msgpack/issues/59
- https://github.com/shamaton/msgpack
- https://pkg.go.dev/vuln/GO-2026-4513
- https://securityinfinity.com/research/shamaton-msgpack-oob-panic-fixext-dos-2026
