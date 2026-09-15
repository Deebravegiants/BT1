# [M] NLTK 3.10.2 Path Traversal via corpus-reader constructors

## Summary
Severity: Medium
Advisory: CVE-2026-79674
Aliases: GHSA-3gq4-3j92-5w49, PYSEC-2026-3736
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-79674
Type: osv

## Details
NLTK versions before 3.10.3 contain a path sandbox bypass vulnerability in corpus-reader constructors that allows attackers to read files outside the intended data root. Attackers can supply arbitrary corpus root paths to LinThesaurusCorpusReader and PanLexLiteCorpusReader constructors to access filesystem content and SQLite databases outside the pathsec sandbox boundary.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79674.json
- https://github.com/nltk/nltk/security/advisories/GHSA-3gq4-3j92-5w49
- https://nvd.nist.gov/vuln/detail/CVE-2026-79674
- https://www.vulncheck.com/advisories/nltk-path-traversal-via-corpus-reader-constructors
