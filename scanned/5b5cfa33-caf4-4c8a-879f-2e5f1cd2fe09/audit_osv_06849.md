# [M] ModSecurity: Transformation utf8toUnicode produces wrong output on i386 architecture

## Summary
Severity: Medium
Advisory: BIT-modsecurity-2026-52761
Aliases: BIT-modsecurity2-2026-52761, CVE-2026-52761, GHSA-qjgm-7gp4-f8qq
Ecosystem: Bitnami
Published: 2026-07-15
Source: https://osv.dev/vulnerability/BIT-modsecurity-2026-52761
Type: osv

## Affected
- Bitnami: `modsecurity` — affected >=3.0.0 <3.0.16

## Details
ModSecurity is an open source, cross platform web application firewall (WAF) engine for Apache, IIS and Nginx. From 3.0.0 through 3.0.15, the t:utf8toUnicode transformation in src/actions/transformations/utf8_to_unicode.cc produces wrong output on i386 architecture because snprintf uses sizeof on a char pointer rather than the length of the unicode buffer, allowing rules that use this transformation to be bypassed on i386 architecture. This issue is fixed in version 3.0.16.

## References
- https://github.com/owasp-modsecurity/ModSecurity/commit/edcd010814e234d46e2ec55a0f1078ff9d3032e4
- https://github.com/owasp-modsecurity/ModSecurity/releases/tag/v3.0.16
- https://github.com/owasp-modsecurity/ModSecurity/security/advisories/GHSA-qjgm-7gp4-f8qq
- https://nvd.nist.gov/vuln/detail/CVE-2026-52761
