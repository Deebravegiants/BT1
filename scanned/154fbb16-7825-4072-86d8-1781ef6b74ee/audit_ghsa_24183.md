# [C] Radicale is vulnerable to directory traversal on Windows Filesystem Storage Backend component

## Summary
Severity: Critical
Advisory: GHSA-84cw-mxhv-qvv4
CVE: CVE-2016-1505
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-84cw-mxhv-qvv4
Type: github-advisory

## Affected
- PyPI: `Radicale` — affected >=0 <1.1

## Details
The filesystem storage backend in Radicale before 1.1 on Windows allows remote attackers to read or write to arbitrary files via a crafted path, as demonstrated by /c:/file/ignore.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1505
- https://github.com/Kozea/Radicale/pull/343
- https://github.com/Kozea/Radicale/commit/b4b3d51f33c7623d312f289252dd7bbb8f58bbe6
- https://github.com/Kozea/Radicale
- http://www.openwall.com/lists/oss-security/2016/01/05/7
- http://www.openwall.com/lists/oss-security/2016/01/06/4
- http://www.openwall.com/lists/oss-security/2016/01/06/7
- http://www.openwall.com/lists/oss-security/2016/01/07/7
- http://www.securityfocus.com/bid/80255
