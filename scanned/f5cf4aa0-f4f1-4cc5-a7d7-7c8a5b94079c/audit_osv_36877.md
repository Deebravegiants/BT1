# [C] LightLLM <= 1.1.0 PD Mode Unsafe Deserialization RCE

## Summary
Severity: Critical
Advisory: CVE-2026-26220
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-17
Source: https://osv.dev/vulnerability/CVE-2026-26220
Type: osv

## Details
LightLLM version 1.1.0 and prior contain an unauthenticated remote code execution vulnerability in PD (prefill-decode) disaggregation mode. The PD master node exposes WebSocket endpoints that receive binary frames and pass the data directly to pickle.loads() without authentication or validation. A remote attacker who can reach the PD master can send a crafted payload to achieve arbitrary code execution.

## References
- https://github.com/ModelTC/lightllm/blob/a27dfc88c2144ed51a6e160b6fbe20aad66c8fe0/lightllm/server/api_http.py#L310
- https://github.com/ModelTC/lightllm/blob/a27dfc88c2144ed51a6e160b6fbe20aad66c8fe0/lightllm/server/api_http.py#L331
- https://lightllm-en.readthedocs.io/en/latest/index.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26220.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-26220
- https://www.vulncheck.com/advisories/lightllm-pd-mode-unsafe-deserialization-rce
- https://github.com/ModelTC/LightLLM/issues/1213
- https://github.com/ModelTC/lightllm
- https://chocapikk.com/posts/2026/lightllm-pickle-rce/
