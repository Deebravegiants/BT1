# [M] NLTK before 3.10.3 Path Traversal via Symlink Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-79676
Aliases: GHSA-p4rw-rvv2-7xwr, PYSEC-2026-3737
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-79676
Type: osv

## Details
NLTK versions before 3.10.3 contain a path traversal vulnerability in corpus readers that reopen root-derived paths using built-in open() instead of nltk.pathsec.open(), allowing symlinks to escape trusted roots. Attackers who stage symlinked corpus files under a trusted data root can disclose outside-root content through normal corpus reader methods like channels(), domains(), and synonyms().

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79676.json
- https://github.com/nltk/nltk/security/advisories/GHSA-p4rw-rvv2-7xwr
- https://nvd.nist.gov/vuln/detail/CVE-2026-79676
- https://www.vulncheck.com/advisories/nltk-before-path-traversal-via-symlink-bypass
