# [M] FastGPT: Cross-team LLM request/response disclosure (IDOR) via /api/core/ai/record/getRecord

## Summary
Severity: Medium
Advisory: CVE-2026-54602
Aliases: GHSA-6vx6-f72r-74cg
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-54602
Type: osv

## Details
FastGPT is a knowledge-based AI application platform. Prior to 4.15.0, GET /api/core/ai/record/getRecord authenticates the caller but loads LLM request and response traces only by requestId without team scoping, allowing any authenticated user to read another team's prompts, retrieved RAG chunks, and completions if the requestId is known. This issue is fixed in version 4.15.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54602.json
- https://github.com/labring/FastGPT/security/advisories/GHSA-6vx6-f72r-74cg
- https://nvd.nist.gov/vuln/detail/CVE-2026-54602
- https://github.com/labring/FastGPT/commit/60c62b7af8269c826885b541bb56e6e5c424c11a
