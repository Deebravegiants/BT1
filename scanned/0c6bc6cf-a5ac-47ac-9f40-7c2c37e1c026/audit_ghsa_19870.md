# [H] Ollama Allows Out-of-Bounds Read

## Summary
Severity: High
Advisory: GHSA-89qx-m49c-8crf
CVE: CVE-2024-12055
CWE: CWE-125
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-89qx-m49c-8crf
Type: github-advisory

## Affected
- Go: `github.com/ollama/ollama` — affected >=0

## Details
A vulnerability in Ollama versions <=0.3.14 allows a malicious user to create a customized gguf model file that can be uploaded to the public Ollama server. When the server processes this malicious model, it crashes, leading to a Denial of Service (DoS) attack. The root cause of the issue is an out-of-bounds read in the gguf.go file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-12055
- https://github.com/ollama/ollama
- https://huntr.com/bounties/7b111d55-8215-4727-8807-c5ed4cf1bfbe
