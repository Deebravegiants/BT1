# [M] Improper privilege management in pyftpdlib

## Summary
Severity: Medium
Advisory: GHSA-8xgx-75qw-6268
CVE: CVE-2007-6741
CWE: CWE-269
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-8xgx-75qw-6268
Type: github-advisory

## Affected
- PyPI: `pyftpdlib` — affected >=0 <0.2.0

## Details
The ftp_PORT function in FTPServer.py in pyftpdlib before 0.2.0 does not prevent TCP connections to privileged ports if the destination IP address matches the source IP address of the connection from the FTP client, which might allow remote authenticated users to conduct FTP bounce attacks via crafted FTP data, as demonstrated by an FTP bounce attack against a NAT server, a related issue to CVE-1999-0017.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-6741
- https://github.com/giampaolo/pyftpdlib/issues/11
- https://github.com/giampaolo/pyftpdlib
- https://github.com/pypa/advisory-database/tree/main/vulns/pyftpdlib/PYSEC-2010-25.yaml
- http://code.google.com/p/pyftpdlib/issues/detail?id=11
- http://code.google.com/p/pyftpdlib/source/browse/trunk/HISTORY
- http://code.google.com/p/pyftpdlib/source/detail?r=32
- http://code.google.com/p/pyftpdlib/source/diff?spec=svn32&r=32&format=side&path=/trunk/pyftpdlib/FTPServer.py
