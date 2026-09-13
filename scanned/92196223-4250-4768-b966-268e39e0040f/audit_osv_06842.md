# [H] Libmodsecurity3 has possible bypass of encoded HTML entities

## Summary
Severity: High
Advisory: BIT-modsecurity-2025-27110
Aliases: BIT-modsecurity2-2025-27110, CVE-2025-27110, GHSA-42w7-rmv5-4x2j
Ecosystem: Bitnami
Published: 2025-03-07
Source: https://osv.dev/vulnerability/BIT-modsecurity-2025-27110
Type: osv

## Affected
- Bitnami: `modsecurity` — affected >=3.0.13 <3.0.14

## Details
Libmodsecurity is one component of the ModSecurity v3 project. The library codebase serves as an interface to ModSecurity Connectors taking in web traffic and applying traditional ModSecurity processing. A bug that exists only in Libmodsecurity3 version 3.0.13 means that, in 3.0.13, Libmodsecurity3 can't decode encoded HTML entities if they contains leading zeroes. Version 3.0.14 contains a fix. No known workarounds are available.

## References
- https://github.com/owasp-modsecurity/ModSecurity/issues/3340
- https://github.com/owasp-modsecurity/ModSecurity/security/advisories/GHSA-42w7-rmv5-4x2j
- https://nvd.nist.gov/vuln/detail/CVE-2025-27110
