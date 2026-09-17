# [H] libModSecurity3 denial of service via segfault when using t:hexDecode on single-character query strings

## Summary
Severity: High
Advisory: BIT-modsecurity-2026-30923
Aliases: CVE-2026-30923, GHSA-qrjc-3jpc-3h2g
Ecosystem: Bitnami
Published: 2026-05-07
Source: https://osv.dev/vulnerability/BIT-modsecurity-2026-30923
Type: osv

## Affected
- Bitnami: `modsecurity` — affected >=3.0.0 <3.0.15

## Details
ModSecurity is an open source, cross platform web application firewall (WAF) engine for Apache, IIS and Nginx. Libmodsecurity is one component of the ModSecurity v3 project. A segmentation fault occurs when a rule using the t:hexDecode transformation inspects a query string parameter containing a single character. An attacker can exploit this to crash worker processes, causing a denial of service. Service resumes once the attack stops as worker processes recover from the segfault. All versions before 3.0.15 of libModSecurity3 are affected. This has been patched in version 3.0.15.

## References
- https://github.com/owasp-modsecurity/ModSecurity/releases/tag/v3.0.15
- https://github.com/owasp-modsecurity/ModSecurity/security/advisories/GHSA-qrjc-3jpc-3h2g
- https://nvd.nist.gov/vuln/detail/CVE-2026-30923
