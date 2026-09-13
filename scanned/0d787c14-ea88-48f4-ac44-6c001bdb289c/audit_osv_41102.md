# [C] CVE-2026-5760

## Summary
Severity: Critical
Advisory: CVE-2026-5760
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/CVE-2026-5760
Type: osv

## Details
SGLang's reranking endpoint (/v1/rerank) achieves Remote Code Execution (RCE) when a model file containing a malcious tokenizer.chat_template is loaded, as the Jinja2 chat templates are rendered using an unsandboxed jinja2.Environment().

## References
- https://www.kb.cert.org/vuls/id/915947
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5760.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5760
- https://github.com/sgl-project/sglang/pull/23660
- https://github.com/Stuub/SGLang-0.5.9-RCE
