# [H] Cross-Site Request Forgery (CSRF) in Luigi

## Summary
Severity: High
Advisory: GHSA-p69g-f978-xxv9
CVE: CVE-2018-1000843
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-12-20
Source: https://github.com/advisories/GHSA-p69g-f978-xxv9
Type: github-advisory

## Affected
- PyPI: `luigi` — affected >=0 <2.8.0

## Details
Luigi version prior to version 2.8.0; after commit 53b52e12745075a8acc016d33945d9d6a7a6aaeb; after GitHub PR spotify/luigi/pull/1870 contains a Cross ite Request Forgery (CSRF) vulnerability in API endpoint: /api/<method> that can result in Task metadata such as task name, id, parameter, etc. will be leaked to unauthorized users. This attack appear to be exploitable via The victim must visit a specially crafted webpage from the network where their Luigi server is accessible.. This vulnerability appears to have been fixed in 2.8.0 and later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000843
- https://github.com/spotify/luigi/pull/1870
- https://github.com/advisories/GHSA-p69g-f978-xxv9
- https://github.com/pypa/advisory-database/tree/main/vulns/luigi/PYSEC-2018-11.yaml
- https://github.com/spotify/luigi
- https://github.com/spotify/luigi/blob/2.7.9/luigi/server.py#L67
- https://groups.google.com/forum/#!topic/luigi-user/ZgfRTpBsVUY
