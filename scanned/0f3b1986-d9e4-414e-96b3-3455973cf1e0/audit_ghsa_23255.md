# [H] Improper Access Control in pyftpdlib

## Summary
Severity: High
Advisory: GHSA-h4g7-8m7r-87r9
CVE: CVE-2009-5012
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-h4g7-8m7r-87r9
Type: github-advisory

## Affected
- PyPI: `pyftpdlib` — affected >=0 <0.5.2

## Details
ftpserver.py in pyftpdlib before 0.5.2 does not require the l permission for the MLST command, which allows remote authenticated users to bypass intended access restrictions and list the root directory via an FTP session.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-5012
- https://github.com/giampaolo/pyftpdlib
- https://github.com/pypa/advisory-database/tree/main/vulns/pyftpdlib/PYSEC-2010-9.yaml
- http://code.google.com/p/pyftpdlib/issues/detail?id=114
- http://code.google.com/p/pyftpdlib/source/browse/trunk/HISTORY
- http://code.google.com/p/pyftpdlib/source/detail?r=596
- http://code.google.com/p/pyftpdlib/source/diff?spec=svn596&r=596&format=side&path=/trunk/pyftpdlib/ftpserver.py
