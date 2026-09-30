# [H] Ollama Divide By Zero vulnerability

## Summary
Severity: High
Advisory: GHSA-9gcr-28rp-cc24
CVE: CVE-2025-0317
CWE: CWE-369
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-9gcr-28rp-cc24
Type: github-advisory

## Affected
- Go: `github.com/ollama/ollama` — affected >=0

## Details
A vulnerability in ollama/ollama versions <=0.3.14 allows a malicious user to upload and create a customized GGUF model file on the Ollama server. This can lead to a division by zero error in the ggufPadding function, causing the server to crash and resulting in a Denial of Service (DoS) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-0317
- https://github.com/ollama/ollama
- https://huntr.com/bounties/a9951bca-9bd8-49b2-b143-4cd4219f9fa0
