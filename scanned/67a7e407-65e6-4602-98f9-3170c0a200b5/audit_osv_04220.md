# [C] Insufficient user check in FlowTokens by Email stage

## Summary
Severity: Critical
Advisory: BIT-authentik-2023-26481
Aliases: CVE-2023-26481, GHSA-3xf5-pqvf-rqq3
Ecosystem: Bitnami
Published: 2026-04-16
Source: https://osv.dev/vulnerability/BIT-authentik-2023-26481
Type: osv

## Affected
- Bitnami: `authentik` — affected >=0 <2022.12.3, >=2023.2.0

## Details
authentik is an open-source Identity Provider. Due to an insufficient access check, a recovery flow link that is created by an admin (or sent via email by an admin) can be used to set the password for any arbitrary user. This attack is only possible if a recovery flow exists, which has both an Identification and an Email stage bound to it. If the flow has policies on the identification stage to skip it when the flow is restored (by checking `request.context['is_restored']`), the flow is not affected by this. With this flow in place, an administrator must create a recovery Link or send a recovery URL to the attacker, who can, due to the improper validation of the token create, set the password for any account. Regardless, for custom recovery flows it is recommended to add a policy that checks if the flow is restored, and skips the identification stage. This issue has been fixed in versions 2023.2.3, 2023.1.3 and 2022.12.2.

## References
- https://github.com/goauthentik/authentik/security/advisories/GHSA-3xf5-pqvf-rqq3
- https://goauthentik.io/docs/releases/2023.2#fixed-in-202323
- https://nvd.nist.gov/vuln/detail/CVE-2023-26481
