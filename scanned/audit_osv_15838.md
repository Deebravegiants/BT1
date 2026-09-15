# [H] CVE-2019-19999

## Summary
Severity: High
Advisory: CVE-2019-19999
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-26
Source: https://osv.dev/vulnerability/CVE-2019-19999
Type: osv

## Details
Halo before 1.2.0-beta.1 allows Server Side Template Injection (SSTI) because TemplateClassResolver.SAFER_RESOLVER is not used in the FreeMarker configuration.

## References
- https://github.com/halo-dev/halo/compare/v1.1.3-beta.2...v1.2.0-beta.1
- https://github.com/halo-dev/halo/issues/419
- https://github.com/halo-dev/halo/issues/440
