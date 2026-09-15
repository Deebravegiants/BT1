# [M] LLaMA-Factory SSRF Guard Bypass via Redirect and DNS Rebinding

## Summary
Severity: Medium
Advisory: CVE-2026-85673
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85673
Type: osv

## Details
LLaMA-Factory contains a server-side request forgery vulnerability in the OpenAI-compatible API multimodal media URL handler that allows unauthenticated attackers to bypass SSRF validation. The check_ssrf_url guard validates URLs once but requests.get follows redirects and re-resolves DNS without re-validation, enabling attackers to use HTTP redirects or DNS rebinding to access internal addresses and cloud metadata endpoints.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85673.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85673
- https://www.vulncheck.com/advisories/llama-factory-ssrf-guard-bypass-via-redirect-and-dns-rebinding
- https://github.com/hiyouga/LlamaFactory/issues/10646
- https://github.com/hiyouga/LlamaFactory
- https://github.com/hiyouga/LlamaFactory/blob/v0.9.5/src/llamafactory/api/chat.py
- https://github.com/hiyouga/LlamaFactory/blob/v0.9.5/src/llamafactory/api/common.py
