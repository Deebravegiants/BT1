# [H] Ollama DNS rebinding vulnerability

## Summary
Severity: High
Advisory: GHSA-5jx5-hqx5-2vrj
CVE: CVE-2024-28224
CWE: CWE-290, CWE-346, CWE-350
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-08
Source: https://github.com/advisories/GHSA-5jx5-hqx5-2vrj
Type: github-advisory

## Affected
- Go: `github.com/ollama/ollama` — affected >=0 <0.1.29

## Details
Ollama before 0.1.29 has a DNS rebinding vulnerability that can inadvertently allow remote access to the full API, thereby letting an unauthorized user chat with a large language model, delete a model, or cause a denial of service (resource exhaustion).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28224
- https://github.com/ollama/ollama
- https://github.com/ollama/ollama/releases
- https://pkg.go.dev/vuln/GO-2024-2699
- https://research.nccgroup.com/2024/04/08/technical-advisory-ollama-dns-rebinding-attack-cve-2024-28224
- https://www.nccgroup.trust/us/our-research/?research=Technical+advisories
