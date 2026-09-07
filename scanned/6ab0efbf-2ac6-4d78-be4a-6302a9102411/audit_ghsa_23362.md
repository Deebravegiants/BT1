# [M] Python Requests Session Fixation

## Summary
Severity: Medium
Advisory: GHSA-pg2w-x9wp-vw92
CVE: CVE-2015-2296
Ecosystem: PyPI
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-pg2w-x9wp-vw92
Type: github-advisory

## Affected
- PyPI: `requests` — affected >=2.1.0 <2.6.0

## Details
The `resolve_redirects` function in sessions.py in requests 2.1.0 through 2.5.3 allows remote attackers to conduct session fixation attacks via a cookie without a host value in a redirect.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-2296
- https://github.com/kennethreitz/requests/commit/3bd8afbff29e50b38f889b2f688785a669b9aafc
- https://github.com/psf/requests/commit/3bd8afbff29e50b38f889b2f688785a669b9aafc
- https://github.com/psf/requests
- https://github.com/pypa/advisory-database/tree/main/vulns/requests/PYSEC-2015-17.yaml
- https://warehouse.python.org/project/requests/2.6.0
- http://advisories.mageia.org/MGASA-2015-0120.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-March/153594.html
- http://www.mandriva.com/security/advisories?name=MDVSA-2015:133
- http://www.openwall.com/lists/oss-security/2015/03/14/4
- http://www.openwall.com/lists/oss-security/2015/03/15/1
- http://www.ubuntu.com/usn/USN-2531-1
