# [M] mem0 - Unauthenticated Config API Exposure and SSRF via ollama_base_url

## Summary
Severity: Medium
Advisory: CVE-2026-59706
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-59706
Type: osv

## Details
mem0 contains unauthenticated config API endpoints that expose LLM API keys in plaintext and allow server-side request forgery via attacker-controlled ollama_base_url parameter. Unauthenticated attackers can retrieve stored secrets like OpenAI API keys via GET /api/v1/config/ or trigger SSRF attacks by setting ollama_base_url to internal addresses like cloud IMDS via PUT /api/v1/config/mem0/llm endpoint.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59706.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59706
- https://www.vulncheck.com/advisories/mem0-server-side-request-forgery-and-plaintext-api-key-exposure-via-unauthenticated-config-endpoints
- https://github.com/mem0ai/mem0/issues/6081
- https://github.com/mem0ai/mem0/commit/a3154d59e52386d4e1189c1f5f44819868f76514
- https://github.com/mem0ai/mem0
