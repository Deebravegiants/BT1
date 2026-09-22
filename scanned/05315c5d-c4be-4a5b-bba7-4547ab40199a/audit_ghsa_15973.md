# [H] Plenti arbitrary file deletion vulnerability

## Summary
Severity: High
Advisory: GHSA-6h8w-hrfp-pffx
CVE: CVE-2024-49381
CWE: CWE-74
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2024-10-31
Source: https://github.com/advisories/GHSA-6h8w-hrfp-pffx
Type: github-advisory

## Affected
- Go: `github.com/plentico/plenti` — affected >=0 <0.7.2

## Details
Plenti, a static site generator, has an arbitrary file deletion vulnerability in versions prior to 0.7.2. The `/postLocal` endpoint is vulnerable to an arbitrary file write deletion when a plenti user serves their website. This issue may lead to information loss. Version 0.7.2 fixes the vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-49381
- https://github.com/plentico/plenti
- https://github.com/plentico/plenti/blob/01825e0dcd3505fac57adc2edf29f772d585c008/cmd/serve.go#L205
- https://github.com/plentico/plenti/releases/tag/v0.7.2
- https://securitylab.github.com/advisories/GHSL-2024-297_GHSL-2024-298_plenti
