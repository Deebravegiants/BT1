# [H] OliveTin OS Command Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-p3qf-84rg-jxfc
CVE: CVE-2025-50946
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-08-13
Source: https://github.com/advisories/GHSA-p3qf-84rg-jxfc
Type: github-advisory

## Affected
- Go: `github.com/OliveTin/OliveTin` — affected >=0

## Details
OS Command Injection in Olivetin 2025.4.22 Custom Themes via the ParseRequestURI function in service/internal/executor/arguments.go.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-50946
- https://github.com/OliveTin/OliveTin
- https://github.com/OliveTin/OliveTin/blob/8c073bf45fca6c6eda4e8a9feb182433277343ee/service/internal/executor/arguments.go#L211
- https://github.com/chrisWalker11/Cves/blob/main/CVE-2025-50946/CVE-2025-50946.md
