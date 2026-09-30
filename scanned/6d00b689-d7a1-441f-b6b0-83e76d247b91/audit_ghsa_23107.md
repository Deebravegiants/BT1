# [M] Improper input validation in pyftpdlib

## Summary
Severity: Medium
Advisory: GHSA-8p2c-fghc-9hj4
CVE: CVE-2008-7264
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-8p2c-fghc-9hj4
Type: github-advisory

## Affected
- PyPI: `pyftpdlib` — affected >=0 <0.5.0

## Details
The ftp_QUIT function in ftpserver.py in pyftpdlib before 0.5.0 allows remote authenticated users to cause a denial of service (file descriptor exhaustion and daemon outage) by sending a QUIT command during a disallowed data-transfer attempt.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-7264
- https://github.com/giampaolo/pyftpdlib/issues/71
- https://github.com/advisories/GHSA-8p2c-fghc-9hj4
- https://github.com/giampaolo/pyftpdlib
- https://github.com/pypa/advisory-database/tree/main/vulns/pyftpdlib/PYSEC-2010-6.yaml
- http://code.google.com/p/pyftpdlib/issues/detail?id=71
- http://code.google.com/p/pyftpdlib/source/browse/trunk/HISTORY
- http://code.google.com/p/pyftpdlib/source/detail?r=344
- http://code.google.com/p/pyftpdlib/source/diff?spec=svn344&r=344&format=side&path=/trunk/pyftpdlib/ftpserver.py
