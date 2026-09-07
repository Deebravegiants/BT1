# [M] XSS in python-markdown2

## Summary
Severity: Medium
Advisory: GHSA-fv3h-8x5j-pvgq
CVE: CVE-2020-11888
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-04-22
Source: https://github.com/advisories/GHSA-fv3h-8x5j-pvgq
Type: github-advisory

## Affected
- PyPI: `markdown2` — affected >=0 <2.3.9

## Details
python-markdown2 through 2.3.8 allows XSS because element names are mishandled unless a \w+ match succeeds. For example, an attack might use elementname@ or elementname- with an onclick attribute.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-11888
- https://github.com/trentm/python-markdown2/issues/348
- https://github.com/pypa/advisory-database/tree/main/vulns/markdown2/PYSEC-2020-65.yaml
- https://github.com/trentm/python-markdown2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6XOAIRJJCZNJUALXDHSIGH5PS2H63A3J
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AQLRBGRVRRZK7P5SFL2MNGXFX37YHJAV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PN6QSHRFZXRQAYZJQ4MOW5MKIXBYOMED
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00031.html
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00035.html
