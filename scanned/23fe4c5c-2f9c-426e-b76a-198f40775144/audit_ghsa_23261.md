# [M] Uncontrolled Resource Consumption in pyftpdlib

## Summary
Severity: Medium
Advisory: GHSA-8gv6-x88p-3f6h
CVE: CVE-2009-5013
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-8gv6-x88p-3f6h
Type: github-advisory

## Affected
- PyPI: `pyftpdlib` — affected >=0 <0.5.2

## Details
Memory leak in the on_dtp_close function in ftpserver.py in pyftpdlib before 0.5.2 allows remote authenticated users to cause a denial of service (memory consumption) by sending a QUIT command during a data transfer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-5013
- https://github.com/giampaolo/pyftpdlib
- https://github.com/pypa/advisory-database/tree/main/vulns/pyftpdlib/PYSEC-2010-10.yaml
- http://code.google.com/p/pyftpdlib/issues/detail?id=119
- http://code.google.com/p/pyftpdlib/source/browse/trunk/HISTORY
- http://code.google.com/p/pyftpdlib/source/detail?r=615
- http://code.google.com/p/pyftpdlib/source/diff?spec=svn615&r=615&format=side&path=/trunk/pyftpdlib/ftpserver.py
