# [C] RAGFlow: Server-Side Template Injection in Prompt Generator leads to Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-45312
Aliases: GHSA-wpg4-h5g2-jxm6
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-45312
Type: osv

## Details
RAGFlow is an open-source RAG (Retrieval-Augmented Generation) engine. In 0.24.0 and earlier, a Jinja2 template injection in the prompt generator (rag/prompts/generator.py) allows any authenticated user to execute arbitrary OS commands on the server. Any normal user can register, create a Canvas workflow with a DuckDuckGo + LLM component chain, and trigger the SSTI.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45312.json
- https://github.com/infiniflow/ragflow/security/advisories/GHSA-wpg4-h5g2-jxm6
- https://nvd.nist.gov/vuln/detail/CVE-2026-45312
