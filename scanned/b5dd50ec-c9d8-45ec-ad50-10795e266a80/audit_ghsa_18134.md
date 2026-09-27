# [M] Llama Stack could potentially allow for remote code execution

## Summary
Severity: Medium
Advisory: GHSA-x75h-m6jj-6cj2
CVE: CVE-2025-55178
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-09-24
Source: https://github.com/advisories/GHSA-x75h-m6jj-6cj2
Type: github-advisory

## Affected
- PyPI: `llama-stack` — affected >=0 <0.2.20

## Details
Llama Stack prior to version v0.2.20 accepted unverified parameters in the resolve_ast_by_type function which could potentially allow for remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-55178
- https://github.com/llamastack/llama-stack/pull/3281
- https://github.com/llamastack/llama-stack/commit/efdb5558b8dcab4d141678bfed0a405e2f312b6f
- https://github.com/llamastack/llama-stack
- https://github.com/llamastack/llama-stack/releases/tag/v0.2.20
- https://www.facebook.com/security/advisories/cve-2025-55178
