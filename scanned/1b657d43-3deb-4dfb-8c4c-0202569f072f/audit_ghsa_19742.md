# [H] Spacy-LLM Server-Side Template Injection (SSTI) vulnerability

## Summary
Severity: High
Advisory: GHSA-793v-gxfp-9q9h
CVE: CVE-2025-25362
CWE: CWE-1336, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-05
Source: https://github.com/advisories/GHSA-793v-gxfp-9q9h
Type: github-advisory

## Affected
- PyPI: `spacy-llm` — affected >=0 <0.7.3

## Details
A Server-Side Template Injection (SSTI) vulnerability in Spacy-LLM v0.7.2 allows attackers to execute arbitrary code via injecting a crafted payload into the template field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-25362
- https://github.com/explosion/spacy-llm/issues/492
- https://github.com/explosion/spacy-llm/pull/491
- https://github.com/explosion/spacy-llm/commit/8bde0490cc1e9de9dd2e84480b7b5cd18a94d739
- https://github.com/explosion/spacy-llm
- https://www.hacktivesecurity.com/blog/2025/04/01/cve-2025-25362-old-vulnerabilities-new-victims-breaking-llm-prompts-with-ssti
