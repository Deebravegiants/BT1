# [H] CVE-2024-39720

## Summary
Severity: High
Advisory: CVE-2024-39720
Aliases: GHSA-95j2-w8x7-hm88, GO-2024-3245
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2024-10-31
Source: https://osv.dev/vulnerability/CVE-2024-39720
Type: osv

## Details
An issue was discovered in Ollama before 0.1.46. An attacker can use two HTTP requests to upload a malformed GGUF file containing just 4 bytes starting with the GGUF custom magic header. By leveraging a custom Modelfile that includes a FROM statement pointing to the attacker-controlled blob file, the attacker can crash the application through the CreateModel route, leading to a segmentation fault (signal SIGSEGV: segmentation violation).

## References
- https://github.com/ollama/ollama/compare/v0.1.45...v0.1.46#diff-782c2737eecfa83b7cb46a77c8bdaf40023e7067baccd4f806ac5517b4563131L417
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39720.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39720
- https://oligo.security/blog/more-models-more-probllms
