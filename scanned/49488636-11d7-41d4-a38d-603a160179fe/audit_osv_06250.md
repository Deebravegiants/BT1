# [H] PHP CGI Parameter Injection Vulnerability (CVE-2024-4577 bypass)

## Summary
Severity: High
Advisory: BIT-libphp-2024-8926
Aliases: BIT-php-2024-8926, BIT-php-min-2024-8926, CVE-2024-8926, GHSA-p99j-rfp4-xqvq
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2024-8926
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.3.0 <8.3.12

## Details
In PHP versions 8.1.* before 8.1.30, 8.2.* before 8.2.24, 8.3.* before 8.3.12, when using a certain non-standard configurations of Windows codepages, the fixes for  CVE-2024-4577 https://github.com/advisories/GHSA-vxpp-6299-mxw3  may still be bypassed and the same command injection related to Windows "Best Fit" codepage behavior can be achieved. This may allow a malicious user to pass options to PHP binary being run, and thus reveal the source code of scripts, run arbitrary PHP code on the server, etc.

## References
- https://github.com/php/php-src/security/advisories/GHSA-p99j-rfp4-xqvq
- https://nvd.nist.gov/vuln/detail/CVE-2024-8926
- https://security.netapp.com/advisory/ntap-20241101-0003/
