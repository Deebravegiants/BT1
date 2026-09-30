# [H] Pylons Colander Denial of Service vulnerability

## Summary
Severity: High
Advisory: GHSA-rv95-4wxj-6fqq
CVE: CVE-2017-18361
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-02-07
Source: https://github.com/advisories/GHSA-rv95-4wxj-6fqq
Type: github-advisory

## Affected
- PyPI: `colander` — affected >=0 <1.7.0

## Details
In Pylons Colander through 1.6, the URL validator allows an attacker to potentially cause an infinite loop thereby causing a denial of service via an unclosed parenthesis.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18361
- https://github.com/Pylons/colander/issues/290
- https://github.com/Pylons/colander/pull/323
- https://github.com/Pylons/colander/commit/98805557c10ab5ff3016ed09aa2d48c49b9df40b
- https://github.com/Pylons/colander
- https://github.com/advisories/GHSA-rv95-4wxj-6fqq
- https://github.com/pypa/advisory-database/tree/main/vulns/colander/PYSEC-2019-167.yaml
