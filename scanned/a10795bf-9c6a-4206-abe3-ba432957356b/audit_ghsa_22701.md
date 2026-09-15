# [H] pyftpdlib vulnerable to allocation of resources without limits

## Summary
Severity: High
Advisory: GHSA-cx59-cp6c-9fr8
CVE: CVE-2007-6740
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-cx59-cp6c-9fr8
Type: github-advisory

## Affected
- PyPI: `pyftpdlib` — affected >=0 <0.2.0

## Details
The ftp_STOU function in FTPServer.py in pyftpdlib before 0.2.0 does not limit the number of attempts to discover a unique filename, which might allow remote authenticated users to cause a denial of service via a STOU command.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-6740
- https://github.com/giampaolo/pyftpdlib/issues/25
- https://github.com/advisories/GHSA-cx59-cp6c-9fr8
- https://github.com/giampaolo/pyftpdlib
- https://github.com/pypa/advisory-database/tree/main/vulns/pyftpdlib/PYSEC-2010-24.yaml
- http://code.google.com/p/pyftpdlib/issues/detail?id=25
- http://code.google.com/p/pyftpdlib/source/browse/trunk/HISTORY
- http://code.google.com/p/pyftpdlib/source/detail?r=37
- http://code.google.com/p/pyftpdlib/source/diff?spec=svn37&r=37&format=side&path=/trunk/pyftpdlib/FTPServer.py
