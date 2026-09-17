# [H] golang.org/x/crypto/ssh/agent has a potential denial of service

## Summary
Severity: High
Advisory: GHSA-56w8-48fp-6mgv
CVE: CVE-2025-47913
CWE: CWE-617
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-11-14
Source: https://github.com/advisories/GHSA-56w8-48fp-6mgv
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto/ssh/agent` — affected >=0 <0.43.0

## Details
SSH clients receiving SSH_AGENT_SUCCESS when expecting a typed response will panic and cause early termination of the client process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-47913
- https://github.com/golang/crypto
- https://go.dev/cl/700295
- https://go.dev/issue/75178
- https://pkg.go.dev/vuln/GO-2025-4116
