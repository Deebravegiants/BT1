# [C] Ollama Platform has missing authentication enabling attackers to perform model management operations

## Summary
Severity: Critical
Advisory: GHSA-f6mr-38g8-39rg
CVE: CVE-2025-63389
CWE: CWE-284, CWE-306
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-18
Source: https://github.com/advisories/GHSA-f6mr-38g8-39rg
Type: github-advisory

## Affected
- Go: `github.com/ollama/ollama` — affected >=0

## Details
A critical authentication bypass vulnerability exists in Ollama platform's API endpoints in versions prior to and including v0.12.3. The platform exposes multiple API endpoints without requiring authentication, enabling remote attackers to perform unauthorized model management operations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-63389
- https://gist.github.com/Cristliu/48dae561696374744d9fced07a544ecd
- https://github.com/ollama/ollama
- https://github.com/ollama/ollama/issues
