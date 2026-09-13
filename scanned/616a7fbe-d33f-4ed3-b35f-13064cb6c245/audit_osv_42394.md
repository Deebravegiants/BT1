# [M] Flowise 3.1.4 IDOR in OpenAI Assistants Integration

## Summary
Severity: Medium
Advisory: CVE-2026-67622
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:H/SA:L)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-67622
Type: osv

## Details
Flowise through 3.1.4 contains an insecure direct object reference vulnerability in the OpenAI Assistants integration that allows authenticated attackers to access credentials belonging to other workspaces by supplying an arbitrary credential UUID to Assistants endpoints without workspace ownership verification. Attackers can enumerate cross-workspace assistant metadata, retrieve file and vector store listings, and upload files into victim workspaces by exploiting the missing workspace-scoped authorization check in the credential lookup logic.

## References
- https://flowiseai.com/sunset
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67622.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67622
- https://www.vulncheck.com/advisories/flowise-idor-in-openai-assistants-integration
- https://github.com/FlowiseAI/Flowise
- https://github.com/Caycon/cve-advisories/blob/main/2026/Flowise/CVE-2026-67622.md
