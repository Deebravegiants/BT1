# [M] go-ntlmssp NTLM challenges can panic on malformed payloads

## Summary
Severity: Medium
Advisory: GHSA-pjcq-xvwq-hhpj
CVE: CVE-2026-32952
CWE: CWE-190
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-04-23
Source: https://github.com/advisories/GHSA-pjcq-xvwq-hhpj
Type: github-advisory

## Affected
- Go: `github.com/Azure/go-ntlmssp` — affected >=0 <0.1.1

## Details
go-ntlmssp is a Go package that provides NTLM/Negotiate authentication over HTTP. Prior to version 0.1.1, a malicious NTLM challenge message can causes an slice out of bounds panic, which can crash any Go process using `ntlmssp.Negotiator` as an HTTP transport. Version 0.1.1 patches the issue.

## References
- https://github.com/Azure/go-ntlmssp/security/advisories/GHSA-pjcq-xvwq-hhpj
- https://nvd.nist.gov/vuln/detail/CVE-2026-32952
- https://github.com/Azure/go-ntlmssp
- https://github.com/Azure/go-ntlmssp/releases/tag/v0.1.1
