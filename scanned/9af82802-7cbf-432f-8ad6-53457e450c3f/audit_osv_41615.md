# [M] NLTK 3.9.4 Path Traversal via FrameNet and NKJP Readers

## Summary
Severity: Medium
Advisory: CVE-2026-62385
Aliases: GHSA-568f-pv23-39p4, PYSEC-2026-3728
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-62385
Type: osv

## Details
NLTK versions before 3.10.0 contain a path traversal vulnerability in FramenetCorpusReader and NKJPCorpusReader that allows attackers to parse XML files outside the corpus root by supplying unsafe selectors or poisoned index state. Attackers can exploit frame_by_name, doc, lu, and header methods with crafted parameters to read arbitrary XML files accessible to the application.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62385.json
- https://github.com/nltk/nltk/security/advisories/GHSA-568f-pv23-39p4
- https://nvd.nist.gov/vuln/detail/CVE-2026-62385
- https://www.vulncheck.com/advisories/nltk-path-traversal-via-framenet-and-nkjp-readers
