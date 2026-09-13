# [M] nltk IPIPANCorpusReader Symlink Arbitrary File Read

## Summary
Severity: Medium
Advisory: CVE-2026-62383
Aliases: GHSA-3hhw-38pf-pxj6, PYSEC-2026-3726
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-62383
Type: osv

## Details
nltk versions before 3.10.2 contain a symlink-based arbitrary file read vulnerability in IPIPANCorpusReader methods that bypass nltk.pathsec validation entirely. Attackers can place a symlink in the corpus root directory and read arbitrary files accessible to the process by calling channels(), domains(), categories(), or fileids() methods with the symlink filename.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62383.json
- https://github.com/nltk/nltk/security/advisories/GHSA-3hhw-38pf-pxj6
- https://nvd.nist.gov/vuln/detail/CVE-2026-62383
- https://www.vulncheck.com/advisories/nltk-ipipancorpusreader-symlink-arbitrary-file-read
