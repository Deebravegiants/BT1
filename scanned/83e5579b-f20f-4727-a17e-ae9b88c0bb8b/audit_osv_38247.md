# [H] text-generation-webui has a SSRF in superbooga/superboogav2 extensions — no URL validation

## Summary
Severity: High
Advisory: CVE-2026-35486
Aliases: GHSA-jvrj-w5hq-6cp2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-35486
Type: osv

## Details
text-generation-webui is an open-source web interface for running Large Language Models. Prior to 4.3, he superbooga and superboogav2 RAG extensions fetch user-supplied URLs via requests.get() with zero validation — no scheme check, no IP filtering, no hostname allowlist. An attacker can access cloud metadata endpoints, steal IAM credentials, and probe internal services. The fetched content is exfiltrated through the RAG pipeline. This vulnerability is fixed in 4.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35486.json
- https://github.com/oobabooga/text-generation-webui/security/advisories/GHSA-jvrj-w5hq-6cp2
- https://nvd.nist.gov/vuln/detail/CVE-2026-35486
