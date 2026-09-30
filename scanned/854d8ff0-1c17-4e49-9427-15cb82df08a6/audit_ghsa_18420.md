# [M] Ollama vulnerable to Cross-Domain Token Exposure

## Summary
Severity: Medium
Advisory: GHSA-x9hg-5q6g-q3jr
CVE: CVE-2025-51471
CWE: CWE-345
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2025-07-22
Source: https://github.com/advisories/GHSA-x9hg-5q6g-q3jr
Type: github-advisory

## Affected
- Go: `github.com/ollama/ollama` — affected >=0

## Details
Cross-Domain Token Exposure in server.auth.getAuthorizationToken in Ollama 0.6.7 allows remote attackers to steal authentication tokens and bypass access controls via a malicious realm value in a WWW-Authenticate header returned by the /api/pull endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-51471
- https://github.com/ollama/ollama/pull/10750
- https://github.com/ollama/ollama
- https://github.com/pypa/advisory-database/tree/main/vulns/ollama/PYSEC-2025-147.yaml
- https://huntr.com/bounties/94eea285-fd65-4e01-a035-f533575ebdc2
- https://www.gecko.security/blog/cve-2025-51471
