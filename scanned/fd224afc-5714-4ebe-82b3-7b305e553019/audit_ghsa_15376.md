# [H] Ollama can extract members of a ZIP archive outside of the parent directory

## Summary
Severity: High
Advisory: GHSA-846m-99qv-67mg
CVE: CVE-2024-45436
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-08-29
Source: https://github.com/advisories/GHSA-846m-99qv-67mg
Type: github-advisory

## Affected
- Go: `github.com/ollama/ollama` — affected >=0 <0.1.47

## Details
`extractFromZipFile` in `model.go` in Ollama before 0.1.47 can extract members of a ZIP archive outside of the parent directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45436
- https://github.com/ollama/ollama/pull/5314
- https://github.com/ollama/ollama/commit/123a722a6f541e300bc8e34297ac378ebe23f527
- https://github.com/ollama/ollama
- https://github.com/ollama/ollama/compare/v0.1.46...v0.1.47
