# [H] Allocation of Resources Without Limits or Throttling in ollama/ollama

## Summary
Severity: High
Advisory: CVE-2025-0315
Aliases: GHSA-fccc-8m69-8r78, GO-2025-3557
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2025-0315
Type: osv

## Details
A vulnerability in ollama/ollama <=0.3.14 allows a malicious user to create a customized GGUF model file, upload it to the Ollama server, and create it. This can cause the server to allocate unlimited memory, leading to a Denial of Service (DoS) attack.

## References
- https://huntr.com/bounties/da414d29-b55a-496f-b135-17e0fcec67bc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/0xxx/CVE-2025-0315.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-0315
