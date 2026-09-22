# [H] Ollama Vulnerable to Denial of Service (DoS) via Crafted GZIP

## Summary
Severity: High
Advisory: GHSA-v464-r2r9-www7
CVE: CVE-2024-12886
CWE: CWE-400, CWE-409
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-v464-r2r9-www7
Type: github-advisory

## Affected
- Go: `github.com/ollama/ollama` — affected >=0

## Details
An Out-Of-Memory (OOM) vulnerability exists in the `ollama` server version 0.3.14. This vulnerability can be triggered when a malicious API server responds with a gzip bomb HTTP response, leading to the `ollama` server crashing. The vulnerability is present in the `makeRequestWithRetry` and `getAuthorizationToken` functions, which use `io.ReadAll` to read the response body. This can result in excessive memory usage and a Denial of Service (DoS) condition.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-12886
- https://github.com/ollama/ollama
- https://huntr.com/bounties/f115fe52-58af-4844-ad29-b1c25f7245df
