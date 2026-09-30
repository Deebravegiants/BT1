# [C] authentik: Account Takeover via SAML NameID Comment Truncation

## Summary
Severity: Critical
Advisory: BIT-authentik-2026-57580
Aliases: CVE-2026-57580, GHSA-35v6-hv2g-6992
Ecosystem: Bitnami
Published: 2026-08-24
Source: https://osv.dev/vulnerability/BIT-authentik-2026-57580
Type: osv

## Affected
- Bitnami: `authentik` — affected >=2026.5.0 <2026.5.5

## Details
authentik is an open-source identity provider. Prior to 2026.2.6 and 2026.5.5, an inbound SAML Source configured with the non-default USERNAME_LINK or EMAIL_LINK user-matching mode interprets an XML comment in a NameID differently from the identity provider's signed assertion. An attacker with an account on the source identity provider who can set the account's NameID can inject an XML comment that truncates the value used by authentik to the text before the comment while the signed assertion remains valid. A crafted NameID can therefore truncate to a victim's username or email and bind the attacker's external identity to the victim's existing account. This grants full takeover without the victim's password or the identity provider's private key, and the malicious link persists so later logins succeed without the comment. Sources using the default unique-identifier matching mode and authentik's outbound SAML Provider role are not affected. This issue is fixed in versions 2026.2.6 and 2026.5.5.

## References
- https://github.com/goauthentik/authentik/commit/6bd00f09f1f6b5bc5212a10340418fa1b264f02c
- https://github.com/goauthentik/authentik/commit/8704a1b89d7bf46bcef0d3c434c821b937fdecc3
- https://github.com/goauthentik/authentik/pull/24057
- https://github.com/goauthentik/authentik/pull/24062
- https://github.com/goauthentik/authentik/releases/tag/version/2026.2.6
- https://github.com/goauthentik/authentik/releases/tag/version/2026.5.5
- https://github.com/goauthentik/authentik/security/advisories/GHSA-35v6-hv2g-6992
- https://nvd.nist.gov/vuln/detail/CVE-2026-57580
