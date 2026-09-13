# [H] authentik: SAML NameID XML Comment Injection Enables Authentication Bypass via Identifier Truncation

## Summary
Severity: High
Advisory: BIT-authentik-2026-40165
Aliases: CVE-2026-40165, GHSA-9wj8-xv4r-qwrp
Ecosystem: Bitnami
Published: 2026-05-25
Source: https://osv.dev/vulnerability/BIT-authentik-2026-40165
Type: osv

## Affected
- Bitnami: `authentik` — affected >=2026.2.0 <2026.2.3

## Details
authentik is an open-source identity provider. Versions 2025.12.4 and prior, and versions 2026.2.0 through 2026.2.2 were vulnerable to Authentication Bypass through SAML NameID XML Comment Injection. Due to how authentik extracted the NameID value from a SAML assertion, it was possible for an attacker to trick authentik into only seeing a part of the NameID value, potentially allowing an attacker to gain access to other accounts. This issue could be exploited on an authentik instance with a SAML Source, where the attacker had an account on the SAML Source and the ability to modify their NameID value (commonly username or E-mail), and XML Signing was enabled. The attacker could modify the SAML assertion given to authentik by injecting a comment within the NameID value, which effectively truncated the NameID value to the snippet before the comment, and gave the attacker access to any user account. This issue has been fixed in versions 2025.12.5 and 2026.2.3.

## References
- https://github.com/goauthentik/authentik/commit/47dec5c6b7fb4a62bfad2ae8bddf002bde7ba774
- https://github.com/goauthentik/authentik/releases/tag/version%2F2025.12.5
- https://github.com/goauthentik/authentik/security/advisories/GHSA-9wj8-xv4r-qwrp
- https://nvd.nist.gov/vuln/detail/CVE-2026-40165
