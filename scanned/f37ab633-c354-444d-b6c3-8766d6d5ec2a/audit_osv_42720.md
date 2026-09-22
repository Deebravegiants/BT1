# [C] NLTK before 3.9.4 Symlink Escape via CorpusReader

## Summary
Severity: Critical
Advisory: CVE-2026-70626
Aliases: GHSA-r6gq-whwq-mvg9, PYSEC-2026-3732
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-70626
Type: osv

## Details
NLTK versions before 3.9.4 contain a symlink escape vulnerability in CorpusReader.open() that allows local attackers to read arbitrary files outside the corpus root. The vulnerability exists because path validation is lexical and does not account for symlink resolution, enabling attackers to place symlinks inside the corpus root to access files outside the intended boundary.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70626.json
- https://github.com/nltk/nltk/security/advisories/GHSA-r6gq-whwq-mvg9
- https://nvd.nist.gov/vuln/detail/CVE-2026-70626
- https://www.vulncheck.com/advisories/nltk-before-symlink-escape-via-corpusreader
