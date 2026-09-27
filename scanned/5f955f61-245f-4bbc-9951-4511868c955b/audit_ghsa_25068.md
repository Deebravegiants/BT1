# [M] priority vulnerable to denial of service

## Summary
Severity: Medium
Advisory: GHSA-h3q4-6j7f-r24c
CVE: CVE-2016-6580
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-h3q4-6j7f-r24c
Type: github-advisory

## Affected
- PyPI: `priority` — affected >=0 <1.2.0

## Details
A HTTP/2 implementation built using any version of the Python priority library prior to version 1.2.0 could be targeted by a malicious peer by having that peer assign priority information for every possible HTTP/2 stream ID. The priority tree would happily continue to store the priority information for each stream, and would therefore allocate unbounded amounts of memory. Attempting to actually use a tree like this would also cause extremely high CPU usage to maintain the tree.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6580
- https://github.com/python-hyper/priority/commit/7d01a7dc4db83bce50f20d47caf4f37b403a3ecd
- https://github.com/pypa/advisory-database/tree/main/vulns/priority/PYSEC-2017-93.yaml
- https://github.com/python-hyper/priority
- https://python-hyper.org/priority/en/latest/security/CVE-2016-6580.html
- https://web.archive.org/web/20160806004329/http://www.securityfocus.com/bid/92311
