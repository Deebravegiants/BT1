# [M] Improper Authentication in pyftpdlib

## Summary
Severity: Medium
Advisory: GHSA-9x66-ghqx-8g5r
CVE: CVE-2007-6737
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-9x66-ghqx-8g5r
Type: github-advisory

## Affected
- PyPI: `pyftpdlib` — affected >=0 <0.2.0

## Details
FTPServer.py in pyftpdlib before 0.2.0 does not increment the attempted_logins count for a USER command that specifies an invalid username, which makes it easier for remote attackers to obtain access via a brute-force attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-6737
- https://github.com/giampaolo/pyftpdlib/issues/20
- https://github.com/advisories/GHSA-9x66-ghqx-8g5r
- https://github.com/giampaolo/pyftpdlib
- https://github.com/pypa/advisory-database/tree/main/vulns/pyftpdlib/PYSEC-2010-21.yaml
- http://code.google.com/p/pyftpdlib/issues/detail?id=20
- http://code.google.com/p/pyftpdlib/source/browse/trunk/HISTORY
- http://code.google.com/p/pyftpdlib/source/detail?r=23
- http://code.google.com/p/pyftpdlib/source/diff?spec=svn23&r=23&format=side&path=/trunk/pyftpdlib/FTPServer.py
