# [H] Ollama Denial of Service (DoS) via Null Pointer Dereference

## Summary
Severity: High
Advisory: GHSA-p2wh-w96x-w232
CVE: CVE-2025-0312
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-p2wh-w96x-w232
Type: github-advisory

## Affected
- Go: `github.com/ollama/ollama` — affected >=0

## Details
A vulnerability in ollama/ollama versions <=0.3.14 allows a malicious user to create a customized GGUF model file that, when uploaded and created on the Ollama server, can cause a crash due to an unchecked null pointer dereference. This can lead to a Denial of Service (DoS) attack via remote network.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-0312
- https://github.com/ollama/ollama
- https://huntr.com/bounties/522c87b6-a7ac-41b2-84f3-62fd58921f21
