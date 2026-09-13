# [M] casdoor's use of`ssh.InsecureIgnoreHostKey()` disables host key verification

## Summary
Severity: Medium
Advisory: GHSA-67fw-w8f2-88wp
CVE: CVE-2024-41264
CWE: CWE-200, CWE-295, CWE-297
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-08-01
Source: https://github.com/advisories/GHSA-67fw-w8f2-88wp
Type: github-advisory

## Affected
- Go: `github.com/casdoor/casdoor` — affected >=1.541.0

## Details
An issue discovered in casdoor v1.636.0 allows attackers to obtain sensitive information via the `ssh.InsecureIgnoreHostKey()` method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41264
- https://gist.github.com/nyxfqq/33ceaccbc9b05d439a944c2b55fa1c0f
- https://github.com/casdoor/casdoor
- https://github.com/casdoor/casdoor/blob/v1.636.0/object/viaSSHDialer.go
- https://pkg.go.dev/vuln/GO-2024-3026
