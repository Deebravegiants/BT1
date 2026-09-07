# [H] Path Traversal in pip

## Summary
Severity: High
Advisory: GHSA-gpvv-69j7-gwj8
CVE: CVE-2019-20916
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-06-09
Source: https://github.com/advisories/GHSA-gpvv-69j7-gwj8
Type: github-advisory

## Affected
- PyPI: `pip` — affected >=0 <19.2

## Details
The pip package before 19.2 for Python allows Directory Traversal when a URL is given in an install command, because a Content-Disposition header can have ../ in a filename, as demonstrated by overwriting the /root/.ssh/authorized_keys file. This occurs in _download_http_url in _internal/download.py. A fix was committed 6704f2ace.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-20916
- https://github.com/pypa/pip/issues/6413
- https://github.com/gzpan123/pip/commit/a4c735b14a62f9cb864533808ac63936704f2ace
- https://github.com/advisories/GHSA-gpvv-69j7-gwj8
- https://github.com/pypa/advisory-database/tree/main/vulns/pip/PYSEC-2020-173.yaml
- https://github.com/pypa/pip
- https://github.com/pypa/pip/compare/19.1.1...19.2
- https://lists.debian.org/debian-lts-announce/2020/09/msg00010.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00010.html
