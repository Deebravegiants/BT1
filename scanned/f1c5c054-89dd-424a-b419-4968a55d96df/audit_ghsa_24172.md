# [M] MODX Revolution allows XSS via document resources

## Summary
Severity: Medium
Advisory: GHSA-fpxg-5x79-43rm
CVE: CVE-2018-20756
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-fpxg-5x79-43rm
Type: github-advisory

## Affected
- Packagist: `modx/revolution` — affected >=0 <2.7.1-pl

## Details
MODX Revolution through v2.7.0-pl allows XSS via a document resource (such as pagetitle), which is mishandled during an Update action, a Quick Edit action, or the viewing of manager logs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20756
- https://github.com/modxcms/revolution/issues/14105
- https://github.com/modxcms/revolution/pull/14335
- https://github.com/modxcms/revolution/commit/71f894ee55dc4eed10538979761d6c94e8cd1078
- https://github.com/modxcms/revolution
