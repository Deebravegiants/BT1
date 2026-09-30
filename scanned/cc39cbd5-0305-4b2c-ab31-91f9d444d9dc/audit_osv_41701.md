# [M] NLTK StreamBackedCorpusView Bypasses pathsec.ENFORCE Arbitrary File Read

## Summary
Severity: Medium
Advisory: CVE-2026-63312
Aliases: GHSA-x5ph-mj9p-rfr8, PYSEC-2026-3730
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-63312
Type: osv

## Details
NLTK before 3.10.0 contains an arbitrary local file read vulnerability in StreamBackedCorpusView that bypasses pathsec.ENFORCE by calling builtins.open() directly instead of pathsec.open(). Attackers who control the fileid argument can read arbitrary local files regardless of the ENFORCE setting, including sensitive system files and application credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63312.json
- https://github.com/nltk/nltk/security/advisories/GHSA-x5ph-mj9p-rfr8
- https://nvd.nist.gov/vuln/detail/CVE-2026-63312
- https://www.vulncheck.com/advisories/nltk-streambackedcorpusview-bypasses-pathsec-enforce-arbitrary-file-read
