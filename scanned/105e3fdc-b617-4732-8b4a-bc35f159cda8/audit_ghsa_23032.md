# [M] Improper Neutralization of Input During Web Page Generation in LXML

## Summary
Severity: Medium
Advisory: GHSA-xp26-p53h-6h2p
CVE: CVE-2018-19787
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-xp26-p53h-6h2p
Type: github-advisory

## Affected
- PyPI: `lxml` — affected >=0 <4.2.5

## Details
An issue was discovered in lxml before 4.2.5. lxml/html/clean.py in the lxml.html.clean module does not remove javascript: URLs that use escaping, allowing a remote attacker to conduct XSS attacks, as demonstrated by "j a v a s c r i p t:" in Internet Explorer. This is a similar issue to CVE-2014-3146.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19787
- https://github.com/lxml/lxml/commit/6be1d081b49c97cfd7b3fbd934a193b668629109
- https://github.com/advisories/GHSA-xp26-p53h-6h2p
- https://github.com/lxml/lxml
- https://github.com/pypa/advisory-database/tree/main/vulns/lxml/PYSEC-2018-12.yaml
- https://lists.debian.org/debian-lts-announce/2018/12/msg00001.html
- https://lists.debian.org/debian-lts-announce/2020/11/msg00044.html
- https://usn.ubuntu.com/3841-1
- https://usn.ubuntu.com/3841-2
