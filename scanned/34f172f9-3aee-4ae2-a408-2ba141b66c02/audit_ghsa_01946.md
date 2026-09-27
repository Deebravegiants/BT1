# [H] markdown2 Regular Expression Denial of Service 

## Summary
Severity: High
Advisory: GHSA-jr9p-r423-9m2r
CVE: CVE-2021-26813
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-02
Source: https://github.com/advisories/GHSA-jr9p-r423-9m2r
Type: github-advisory

## Affected
- PyPI: `markdown2` — affected >=1.0.1.18 <2.4.0

## Details
markdown2 >=1.0.1.18, fixed in 2.4.0, is affected by a regular expression denial of service vulnerability. If an attacker provides a malicious string, it can make markdown2 processing difficult or delayed for an extended period of time.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26813
- https://github.com/trentm/python-markdown2/pull/387
- https://github.com/trentm/python-markdown2/commit/7b651260739647de5198323e0445b1618750c374
- https://github.com/advisories/GHSA-jr9p-r423-9m2r
- https://github.com/pypa/advisory-database/tree/main/vulns/markdown2/PYSEC-2021-20.yaml
- https://github.com/trentm/python-markdown2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BRP5RN35JZTSJ3JT4722F447ZDK7LZS5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/J752422YELXLMLZJPVJVKD2KKHHQRVEH
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JTIX5UXRDJZJ57DO4V33ZNJTNKWGBQLY
