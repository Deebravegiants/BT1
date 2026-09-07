# [H] ThinkCMF Cross Site Request Forgery (CSRF) vulnerability

## Summary
Severity: High
Advisory: GHSA-6xw3-cpqj-8mxr
CVE: CVE-2022-40489
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-01
Source: https://github.com/advisories/GHSA-6xw3-cpqj-8mxr
Type: github-advisory

## Affected
- Packagist: `thinkcmf/thinkcmf` — affected >=0 <6.0.8

## Details
ThinkCMF version 6.0.7 is affected by a Cross Site Request Forgery (CSRF) vulnerability that allows a Super Administrator user to be injected into administrative users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40489
- https://github.com/thinkcmf/thinkcmf/issues/736
- https://github.com/thinkcmf/thinkcmf/commit/321faa20865e74540e5f0a63e4c3f4ea75093d59
- https://github.com/thinkcmf/thinkcmf/commit/b61636134aa57d4693967f35772200c779099740
- https://github.com/thinkcmf/thinkcmf
