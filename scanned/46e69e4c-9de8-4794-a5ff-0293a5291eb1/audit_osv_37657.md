# [H] SQLBot: Remote Code Execution via Terminology Poisoning

## Summary
Severity: High
Advisory: CVE-2026-32622
Aliases: GHSA-m7q7-vhw9-q7m3
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-32622
Type: osv

## Details
SQLBot is an intelligent data query system based on a large language model and RAG. Versions 1.5.0 and below contain a Stored Prompt Injection vulnerability that chains three flaws: a missing permission check on the Excel upload API allowing any authenticated user to upload malicious terminology, unsanitized storage of terminology descriptions containing dangerous payloads, and a lack of semantic fencing when injecting terminology into the LLM's system prompt. Together, these flaws allow an attacker to hijack the LLM's reasoning to generate malicious PostgreSQL commands (e.g., COPY ... TO PROGRAM), ultimately achieving Remote Code Execution on the database or application server with postgres user privileges. The issue is fixed in v1.6.0.

## References
- https://github.com/dataease/SQLBot/releases/tag/v1.6.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32622.json
- https://github.com/dataease/SQLBot/security/advisories/GHSA-m7q7-vhw9-q7m3
- https://nvd.nist.gov/vuln/detail/CVE-2026-32622
