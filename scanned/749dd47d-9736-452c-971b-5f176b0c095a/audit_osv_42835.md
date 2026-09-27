# [M] Flowise 2.2.4 - 3.1.4 Missing Authorization via openai-assistants-file/download

## Summary
Severity: Medium
Advisory: CVE-2026-71962
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-71962
Type: osv

## Details
Flowise versions 2.2.4 through 3.1.4 contain a missing authorization vulnerability in the POST /api/v1/openai-assistants-file/download endpoint that allows unauthenticated attackers to access private files by exploiting the endpoint's inclusion in the global authentication whitelist, which bypasses all session and API key verification. Attackers can supply valid chatflowId, chatId, and fileName identifiers to retrieve files from any chatflow on the instance, including private chatflows belonging to other workspaces or organizations.

## References
- https://flowiseai.com/sunset
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71962.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-71962
- https://www.vulncheck.com/advisories/flowise-missing-authorization-via-openai-assistants-file-download
- https://github.com/FlowiseAI/Flowise
- https://gist.github.com/haidang-infosec/402db84bee7aca2f57bb109b31574649?utm_source=chatgpt.com
