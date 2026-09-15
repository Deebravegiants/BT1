# [M] Directory Traversal in pyftpdlib

## Summary
Severity: Medium
Advisory: GHSA-f8wg-36r9-7f4q
CVE: CVE-2007-6736
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-f8wg-36r9-7f4q
Type: github-advisory

## Affected
- PyPI: `pyftpdlib` — affected >=0 <0.2.0

## Details
Python FTP server library provides a high-level portable interface to easily write very efficient, scalable and asynchronous FTP servers with Python. Multiple directory traversal vulnerabilities in FTPServer.py in pyftpdlib before 0.2.0 allow remote authenticated users to access arbitrary files and directories via a .. (dot dot) in a (1) LIST, (2) STOR, or (3) RETR command.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-6736
- https://github.com/giampaolo/pyftpdlib/issues/9
- https://github.com/advisories/GHSA-f8wg-36r9-7f4q
- https://github.com/giampaolo/pyftpdlib
- https://github.com/pypa/advisory-database/tree/main/vulns/pyftpdlib/PYSEC-2010-20.yaml
- http://code.google.com/p/pyftpdlib/issues/detail?id=9
- http://code.google.com/p/pyftpdlib/source/browse/trunk/HISTORY
- http://code.google.com/p/pyftpdlib/source/detail?r=16
- http://code.google.com/p/pyftpdlib/source/diff?spec=svn16&r=16&format=side&path=/trunk/pyftpdlib/FTPServer.py
