# [H] authentik has a Signature Verification Bypass via SAML Assertion Wrapping

## Summary
Severity: High
Advisory: BIT-authentik-2026-25922
Aliases: CVE-2026-25922, GHSA-jh35-c4cc-wjm4
Ecosystem: Bitnami
Published: 2026-04-16
Source: https://osv.dev/vulnerability/BIT-authentik-2026-25922
Type: osv

## Affected
- Bitnami: `authentik` — affected >=2025.10.0 <2025.12.4

## Details
authentik is an open-source identity provider. Prior to 2025.8.6, 2025.10.4, and 2025.12.4, when using a SAML Source that has the option Verify Assertion Signature under Verification Certificate enabled and not Verify Response Signature, or does not have the Encryption Certificate setting under Advanced Protocol settings configured, it was possible for an attacker to inject a malicious assertion before the signed assertion that authentik would use instead. authentik 2025.8.6, 2025.10.4, and 2025.12.4 fix this issue.

## References
- https://github.com/goauthentik/authentik/releases/tag/version%2F2025.10.4
- https://github.com/goauthentik/authentik/releases/tag/version%2F2025.12.4
- https://github.com/goauthentik/authentik/releases/tag/version%2F2025.8.6
- https://github.com/goauthentik/authentik/security/advisories/GHSA-jh35-c4cc-wjm4
- https://nvd.nist.gov/vuln/detail/CVE-2026-25922
