# [M] Ollama 0.30.0 through 0.33.2 SSRF via Cross-Host Tensor Blob Redirect

## Summary
Severity: Medium
Advisory: CVE-2026-85180
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85180
Type: osv

## Details
Ollama fails to validate redirect destinations when pulling tensor-layer models, allowing unauthenticated attackers to redirect blob downloads to arbitrary hosts. An attacker can control a registry, serve a malicious tensor-layer manifest, and cause the server to issue GET requests to internal hosts including cloud metadata endpoints.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85180.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85180
- https://www.vulncheck.com/advisories/ollama-0.30.0-through-0.33.2-ssrf-via-cross-host-tensor-blob-redirect
- https://github.com/ollama/ollama/issues/17041
- https://github.com/ollama/ollama
- https://github.com/ollama/ollama/blob/v0.33.2/x/transfer/download.go
