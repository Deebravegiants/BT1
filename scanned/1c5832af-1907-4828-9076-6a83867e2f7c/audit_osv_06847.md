# [H] ModSecurity: Unsigned integer underflow in @verifySSN / @verifyCPF / @verifySVNR operators

## Summary
Severity: High
Advisory: BIT-modsecurity-2026-42268
Aliases: BIT-modsecurity2-2026-42268, CVE-2026-42268, GHSA-vwr3-7x7g-7p9w
Ecosystem: Bitnami
Published: 2026-05-14
Source: https://osv.dev/vulnerability/BIT-modsecurity-2026-42268
Type: osv

## Affected
- Bitnami: `modsecurity` — affected >=3.0.0 <3.0.15

## Details
ModSecurity is an open source, cross platform web application firewall (WAF) engine for Apache, IIS and Nginx. From 3.0.0 to before 3.0.15, there is an unhandled exception (std::out_of_range) caused by unsigned integer underflow in libmodsecurity3 if the user (administrator) uses a rule any of @verifySSN, @verifyCPF, or @verifySVNR. This vulnerability is fixed in 3.0.15.

## References
- https://github.com/owasp-modsecurity/ModSecurity/security/advisories/GHSA-vwr3-7x7g-7p9w
- https://nvd.nist.gov/vuln/detail/CVE-2026-42268
