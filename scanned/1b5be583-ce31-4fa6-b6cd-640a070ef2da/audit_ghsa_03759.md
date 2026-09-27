# [H] NLTK Vulnerable To Path Traversal

## Summary
Severity: High
Advisory: GHSA-mr7p-25v2-35wr
CVE: CVE-2019-14751
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-08-23
Source: https://github.com/advisories/GHSA-mr7p-25v2-35wr
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0 <3.4.5

## Details
NLTK Downloader before 3.4.5 is vulnerable to a directory traversal, allowing attackers to write arbitrary files via a `../` (dot dot slash) in an NLTK package (ZIP archive) that is mishandled during extraction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14751
- https://github.com/nltk/nltk/commit/f59d7ed8df2e0e957f7f247fe218032abdbe9a10
- https://github.com/advisories/GHSA-mr7p-25v2-35wr
- https://github.com/mssalvatore/CVE-2019-14751_PoC
- https://github.com/nltk/nltk
- https://github.com/nltk/nltk/blob/3.4.5/ChangeLog
- https://github.com/pypa/advisory-database/tree/main/vulns/nltk/PYSEC-2019-106.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QI4IJGLZQ5S7C5LNRNROHAO2P526XE3D
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZGZSSEJH7RHH3RBUEVWWYT75QU67J7SE
- https://salvatoresecurity.com/zip-slip-in-nltk-cve-2019-14751
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00001.html
