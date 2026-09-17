# [M] Ollama allows deletion of arbitrary files

## Summary
Severity: Medium
Advisory: GHSA-93jv-pvg8-hf3v
CVE: CVE-2025-44779
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2025-08-07
Source: https://github.com/advisories/GHSA-93jv-pvg8-hf3v
Type: github-advisory

## Affected
- Go: `github.com/ollama/ollama` — affected >=0 <0.1.34

## Details
An issue in Ollama v0.1.33 allows attackers to delete arbitrary files via sending a crafted packet to the endpoint /api/pull.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-44779
- https://a1batr0ss.top/2025/03/17/Ollama-arbitrary-file-deletion-vulnerability
- https://a1batr0ss.top/2025/08/06/CVE-2025-44779-Ollama-arbitrary-file-deletion
- https://github.com/ollama/ollama
