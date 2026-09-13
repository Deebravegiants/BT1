# [H] Agenta's Server-Side Template Injection (SSTI) via custom evaluator Jinja2 templates allows RCE

## Summary
Severity: High
Advisory: CVE-2026-27961
Aliases: GHSA-cfr2-mp74-3763, PYSEC-2026-7
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-27961
Type: osv

## Details
Agenta is an open-source LLMOps platform. A Server-Side Template Injection (SSTI) vulnerability exists in versions prior to 0.86.8 in Agenta's API server evaluator template rendering. Although the vulnerable code lives in the SDK package, it is executed server-side within the API process when running evaluators. This does not affect standalone SDK usage — it only impacts self-hosted or managed Agenta platform deployments. Version 0.86.8 contains a fix for the issue.

## References
- https://github.com/Agenta-AI/agenta/security/advisories/GHSA-cfr2-mp74-3763
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27961.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-27961
