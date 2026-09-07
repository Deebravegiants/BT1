# [M] Improper Authentication in pyftpdlib

## Summary
Severity: Medium
Advisory: GHSA-q6w2-jxcm-2crj
CVE: CVE-2008-7263
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-q6w2-jxcm-2crj
Type: github-advisory

## Affected
- PyPI: `pyftpdlib` — affected >=0 <0.5.0

## Details
ftpserver.py in pyftpdlib before 0.5.0 does not delay its response after receiving an invalid login attempt, which makes it easier for remote attackers to obtain access via a brute-force attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-7263
- https://github.com/giampaolo/pyftpdlib/issues/73
- https://github.com/advisories/GHSA-q6w2-jxcm-2crj
- https://github.com/giampaolo/pyftpdlib
- https://github.com/pypa/advisory-database/tree/main/vulns/pyftpdlib/PYSEC-2010-5.yaml
- http://code.google.com/p/pyftpdlib/issues/detail?id=73
- http://code.google.com/p/pyftpdlib/source/browse/trunk/HISTORY
- http://code.google.com/p/pyftpdlib/source/detail?r=348
- http://code.google.com/p/pyftpdlib/source/diff?spec=svn348&r=348&format=side&path=/trunk/pyftpdlib/ftpserver.py
