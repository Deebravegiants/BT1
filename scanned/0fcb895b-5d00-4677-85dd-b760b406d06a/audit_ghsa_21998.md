# [H] Denial of Service in Bytom

## Summary
Severity: High
Advisory: GHSA-vc3x-gx6c-g99f
CVE: CVE-2018-18206
CWE: CWE-190
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-vc3x-gx6c-g99f
Type: github-advisory

## Affected
- Go: `github.com/bytom/bytom` — affected >=0 <1.0.6

## Details
In the client in Bytom before 1.0.6, checkTopicRegister in p2p/discover/net.go does not prevent negative idx values, leading to a crash.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18206
- https://github.com/Bytom/bytom/pull/1307
- https://github.com/Bytom/bytom/commit/1ac3c8ac4f2b1e1df9675228290bda6b9586ba42
- https://github.com/Bytom/bytom
- https://pkg.go.dev/vuln/GO-2021-0079
