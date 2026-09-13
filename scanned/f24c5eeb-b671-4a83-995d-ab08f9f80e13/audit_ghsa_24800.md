# [M] Directory traversal in pyftpdlib

## Summary
Severity: Medium
Advisory: GHSA-jw88-wxv5-7c4f
CVE: CVE-2008-7262
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-jw88-wxv5-7c4f
Type: github-advisory

## Affected
- PyPI: `pyftpdlib` — affected >=0 <0.3.0

## Details
Multiple directory traversal vulnerabilities in FTPServer.py in pyftpdlib before 0.3.0 allow remote authenticated users to access arbitrary files and directories via vectors involving a symlink in a pathname to a (1) CWD, (2) DELE, (3) STOR, or (4) RETR command.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-7262
- https://github.com/giampaolo/pyftpdlib/issues/55
- https://github.com/giampaolo/pyftpdlib
- https://github.com/pypa/advisory-database/tree/main/vulns/pyftpdlib/PYSEC-2010-4.yaml
- http://code.google.com/p/pyftpdlib/issues/detail?id=55
- http://code.google.com/p/pyftpdlib/source/browse/trunk/HISTORY
