# [M] [20240201] - Core - Insufficient session expiration in MFA management views

## Summary
Severity: Medium
Advisory: BIT-joomla-2024-21722
Aliases: CVE-2024-21722
Ecosystem: Bitnami
Published: 2025-06-03
Source: https://osv.dev/vulnerability/BIT-joomla-2024-21722
Type: osv

## Affected
- Bitnami: `joomla` — affected >=3.2.0 <5.0.3

## Details
The MFA management features did not properly terminate existing user sessions when a user's MFA methods have been modified.

## References
- https://developer.joomla.org/security-centre/925-20240201-core-insufficient-session-expiration-in-mfa-management-views.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-21722
