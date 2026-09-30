# [C] Bleach URI Scheme Restriction Bypass

## Summary
Severity: Critical
Advisory: GHSA-m9mq-p2f9-cfqv
CVE: CVE-2018-7753
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-01-04
Source: https://github.com/advisories/GHSA-m9mq-p2f9-cfqv
Type: github-advisory

## Affected
- PyPI: `bleach` — affected >=2.1.0 <2.1.3

## Details
An issue was discovered in Bleach 2.1.x before 2.1.3. Attributes that have URI values weren't properly sanitized if the values contained character entities. Using character entities, it was possible to construct a URI value with a scheme that was not allowed that would slide through unsanitized.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7753
- https://github.com/mozilla/bleach/commit/c5df5789ec3471a31311f42c2d19fc2cf21b35ef
- https://bugs.debian.org/892252
- https://github.com/mozilla/bleach
- https://github.com/mozilla/bleach/releases/tag/v2.1.3
- https://github.com/pypa/advisory-database/tree/main/vulns/bleach/PYSEC-2018-51.yaml
