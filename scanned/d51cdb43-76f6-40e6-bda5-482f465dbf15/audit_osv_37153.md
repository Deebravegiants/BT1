# [C] RAGFlow: Server-Side Template Injection (SSTI) leading to Remote Code Execution (RCE) in Agent "Text Processing" Component

## Summary
Severity: Critical
Advisory: CVE-2026-28797
Aliases: GHSA-vvwj-fvwh-4whx
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-28797
Type: osv

## Details
RAGFlow is an open-source RAG (Retrieval-Augmented Generation) engine. In versions 0.24.0 and prior, a Server-Side Template Injection (SSTI) vulnerability exists in RAGFlow's Agent workflow Text Processing (StringTransform) and Message components. These components use Python's jinja2.Template (unsandboxed) to render user-supplied templates, allowing any authenticated user to execute arbitrary operating system commands on the server. At time of publication, there are no publicly available patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28797.json
- https://github.com/infiniflow/ragflow/security/advisories/GHSA-vvwj-fvwh-4whx
- https://nvd.nist.gov/vuln/detail/CVE-2026-28797
