# [M] Exposure of Sensitive Information to an Unauthorized Actor in Requests

## Summary
Severity: Medium
Advisory: GHSA-cfj3-7x9c-4p3h
CVE: CVE-2014-1829
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-cfj3-7x9c-4p3h
Type: github-advisory

## Affected
- PyPI: `requests` — affected >=0 <2.3.0

## Details
Requests (aka python-requests) before 2.3.0 allows remote servers to obtain a netrc password by reading the Authorization header in a redirected request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-1829
- https://github.com/kennethreitz/requests/issues/1885
- https://github.com/psf/requests/issues/1885
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=733108
- https://github.com/advisories/GHSA-cfj3-7x9c-4p3h
- https://github.com/psf/requests
- https://github.com/pypa/advisory-database/tree/main/vulns/requests/PYSEC-2014-13.yaml
- https://web.archive.org/web/20150523055216/http://www.mandriva.com/en/support/security/advisories/advisory/MDVSA-2015:133/?name=MDVSA-2015:133
- http://advisories.mageia.org/MGASA-2014-0409.html
- http://www.debian.org/security/2015/dsa-3146
- http://www.mandriva.com/security/advisories?name=MDVSA-2015:133
- http://www.ubuntu.com/usn/USN-2382-1
