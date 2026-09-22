# [H] Mem0 0.2.8 Missing Authorization via POST /configure Endpoint

## Summary
Severity: High
Advisory: CVE-2026-49948
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-49948
Type: osv

## Details
Mem0 versions through 0.2.8, fixed in commit ae7f406, contain a missing authorization vulnerability in the self-hosted server component where the POST /configure endpoint modifies global LLM provider and embedder configuration but only verifies authentication via JWT or X-API-Key without validating the caller's role. Any authenticated user holding a distributed API key can redirect all LLM and embedder traffic to an attacker-controlled server, with the malicious configuration persisted to PostgreSQL and surviving server restarts to affect all users and API keys on the instance.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49948.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-49948
- https://www.vulncheck.com/advisories/mem0-missing-authorization-via-post-configure-endpoint
- https://github.com/mem0ai/mem0/issues/5127
- https://github.com/mem0ai/mem0/issues/5384
- https://github.com/mem0ai/mem0/pull/5360
- https://github.com/mem0ai/mem0/commit/ae7f4062652df1376990221101d1adbb0819c973
- https://github.com/mem0ai/mem0
