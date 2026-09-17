# [M] NLTK FramenetCorpusReader Symlink Sandbox Bypass before 3.10.2

## Summary
Severity: Medium
Advisory: CVE-2026-62384
Aliases: GHSA-f833-7jw8-xwrv, PYSEC-2026-3789
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-62384
Type: osv

## Details
NLTK versions before 3.10.2 contain a symlink-based sandbox bypass in FramenetCorpusReader that allows attackers to read arbitrary XML files outside the corpus root. Attackers can place symlinks with names containing no path separators inside the corpus subdirectory, which pass the path validation guard and are resolved to files outside the intended corpus root when accessed via frame_by_name(), _lu_file(), or doc() methods.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62384.json
- https://github.com/nltk/nltk/security/advisories/GHSA-f833-7jw8-xwrv
- https://nvd.nist.gov/vuln/detail/CVE-2026-62384
- https://www.vulncheck.com/advisories/nltk-framenetcorpusreader-symlink-sandbox-bypass-before
