# [M] httplib2 incorrectly checks SSL certificate

## Summary
Severity: Medium
Advisory: GHSA-q48q-77qv-cf9p
CVE: CVE-2013-2037
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-q48q-77qv-cf9p
Type: github-advisory

## Affected
- PyPI: `httplib2` — affected >=0 <0.10.1

## Details
httplib2 prior to version 0.10.1, after an initial connection is made, does not verify that the server hostname matches a domain name in the subject's Common Name (CN) or subjectAltName field of the X.509 certificate, which allows man-in-the-middle attackers to spoof SSL servers via an arbitrary valid certificate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2037
- https://github.com/httplib2/httplib2/issues/5
- https://github.com/httplib2/httplib2/commit/40cbdcc8586f2292fa0e76a3e8c012f0cc9ed919
- https://bugs.launchpad.net/httplib2/+bug/1175272
- https://github.com/httplib2/httplib2
- https://github.com/pypa/advisory-database/tree/main/vulns/httplib2/PYSEC-2014-81.yaml
- https://web.archive.org/web/20200228052625/http://www.securityfocus.com/bid/52179
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=706602
- http://code.google.com/p/httplib2/issues/detail?id=282
- http://seclists.org/oss-sec/2013/q2/257
- http://www.ubuntu.com/usn/USN-1948-1
