# [M] OPA for Windows has an SMB force-authentication vulnerability

## Summary
Severity: Medium
Advisory: GHSA-c77r-fh37-x2px
CVE: CVE-2024-8260
CWE: CWE-294
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2024-08-30
Source: https://github.com/advisories/GHSA-c77r-fh37-x2px
Type: github-advisory

## Affected
- Go: `github.com/open-policy-agent/opa` — affected >=0 <0.68.0

## Details
A SMB force-authentication vulnerability exists in all versions of OPA for Windows prior to v0.68.0. The vulnerability exists because of improper input validation, allowing a user to pass an arbitrary SMB share instead of a Rego file as an argument to OPA CLI or to one of the OPA Go library’s functions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8260
- https://github.com/open-policy-agent/opa/commit/10f4d553e6bb6ae9c69611ecdd9a77dda857070e
- https://github.com/open-policy-agent/opa
- https://github.com/open-policy-agent/opa/releases/tag/v0.68.0
- https://pkg.go.dev/vuln/GO-2024-3141
- https://www.tenable.com/security/research/tra-2024-36
