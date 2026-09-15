# [H] ChromaDB's SimpleRBACAuthorizationProvider doesn't check which tenant, database, or collection a permission applies to

## Summary
Severity: High
Advisory: GHSA-xph7-9rjv-w5fr
CVE: CVE-2026-45831
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-xph7-9rjv-w5fr
Type: github-advisory

## Affected
- PyPI: `chromadb` — affected >=0.5.0

## Details
The SimpleRBACAuthorizationProvider authorization provider in versions 0.5.0 or later of the ChromaDB Python project evaluates whether a user holds a given permission but never checks which tenant, database, or collection that permission applies to allowing users to perform cross tenant actions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-45831
- https://github.com/chroma-core/chroma/issues/7588
- https://github.com/chroma-core/chroma/pull/7602
- https://github.com/chroma-core/chroma
- https://www.hiddenlayer.com/sai-security-advisory/2026-06-chromadb-3
