# [H] Improper Restriction of XML External Entity Reference in python-docx

## Summary
Severity: High
Advisory: GHSA-34wj-p5jm-2p96
CVE: CVE-2016-5851
CWE: CWE-611
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-34wj-p5jm-2p96
Type: github-advisory

## Affected
- PyPI: `python-docx` — affected >=0 <0.8.6

## Details
python-docx before 0.8.6 allows context-dependent attackers to conduct XML External Entity (XXE) attacks via a crafted document.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5851
- https://github.com/python-openxml/python-docx/commit/61b40b161b64173ab8e362aec1fd197948431beb
- https://github.com/advisories/GHSA-34wj-p5jm-2p96
- https://github.com/pypa/advisory-database/tree/main/vulns/python-docx/PYSEC-2016-21.yaml
- https://github.com/python-openxml/python-docx
- https://github.com/python-openxml/python-docx/blob/v0.8.6/HISTORY.rst
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6FFMOH7ZPOPQWNJGUZOS5LXX4MGNRXXT
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XU2WSYRNB7CLBBFCGSX34XHACTA2SWDZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6FFMOH7ZPOPQWNJGUZOS5LXX4MGNRXXT
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XU2WSYRNB7CLBBFCGSX34XHACTA2SWDZ
- https://web.archive.org/web/20170214030949/http://www.securityfocus.com/bid/91485
- http://www.openwall.com/lists/oss-security/2016/06/28/7
- http://www.openwall.com/lists/oss-security/2016/06/28/8
- http://www.securityfocus.com/bid/91485
