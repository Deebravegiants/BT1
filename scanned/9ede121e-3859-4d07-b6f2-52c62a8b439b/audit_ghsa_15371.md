# [C] Gitea Cross-site Scripting Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-4h4p-553m-46qh
CVE: CVE-2024-6886
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-06
Source: https://github.com/advisories/GHSA-4h4p-553m-46qh
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.22.1

## Details
Improper Neutralization of Input During Web Page Generation (XSS or 'Cross-site Scripting') vulnerability in Gitea Gitea Open Source Git Server allows Stored XSS.This issue affects Gitea Open Source Git Server: 1.22.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6886
- https://github.com/go-gitea/gitea/pull/31200
- https://github.com/go-gitea/gitea/commit/b6280f4d21309cfae7cc07f74173354c664d5e10
- https://blog.gitea.com/release-of-1.22.1
- https://github.com/go-gitea/gitea
- https://pkg.go.dev/vuln/GO-2024-3056
