# [H] mechanize Regular Expression Denial of Service vulnerability

## Summary
Severity: High
Advisory: GHSA-g3pv-pj5f-3hfq
CVE: CVE-2021-32837
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-01-18
Source: https://github.com/advisories/GHSA-g3pv-pj5f-3hfq
Type: github-advisory

## Affected
- PyPI: `mechanize` — affected >=0 <0.4.6

## Details
mechanize, a library for automatically interacting with HTTP web servers, contains a regular expression that is vulnerable to regular expression denial of service (ReDoS) prior to version 0.4.6. If a web server responds in a malicious way, then mechanize could crash. Version 0.4.6 has a patch for the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32837
- https://github.com/python-mechanize/mechanize/commit/dd05334448e9f39814bab044d2eaa5ef69b410d6
- https://github.com/pypa/advisory-database/tree/main/vulns/mechanize/PYSEC-2023-25.yaml
- https://github.com/python-mechanize/mechanize
- https://github.com/python-mechanize/mechanize/blob/3acb1836f3fd8edc5a758a417dd46b53832ae3b5/mechanize/_urllib2_fork.py#L878-L879
- https://github.com/python-mechanize/mechanize/releases/tag/v0.4.6
- https://lists.debian.org/debian-lts-announce/2023/06/msg00022.html
- https://lists.debian.org/debian-lts-announce/2025/12/msg00028.html
- https://securitylab.github.com/advisories/GHSL-2021-108-python-mechanize-mechanize
