# [C] authentik vulnerable to unauthorized user creation and potential account takeover

## Summary
Severity: Critical
Advisory: BIT-authentik-2022-46145
Aliases: CVE-2022-46145, GHSA-mjfw-54m5-fvjf
Ecosystem: Bitnami
Published: 2026-04-16
Source: https://osv.dev/vulnerability/BIT-authentik-2022-46145
Type: osv

## Affected
- Bitnami: `authentik` — affected >=2022.11.0 <2022.11.2

## Details
authentik is an open-source identity provider. Versions prior to 2022.11.2 and 2022.10.2 are vulnerable to unauthorized user creation and potential account takeover. With the default flows, unauthenticated users can create new accounts in authentik. If a flow exists that allows for email-verified password recovery, this can be used to overwrite the email address of admin accounts and take over their accounts. authentik 2022.11.2 and 2022.10.2 fix this issue. As a workaround, a policy can be created and bound to the `default-user-settings-flow flow` with the contents `return request.user.is_authenticated`.

## References
- https://github.com/goauthentik/authentik/security/advisories/GHSA-mjfw-54m5-fvjf
- https://goauthentik.io/docs/releases/2022.10#fixed-in-2022102
- https://goauthentik.io/docs/releases/2022.11#fixed-in-2022112
- https://nvd.nist.gov/vuln/detail/CVE-2022-46145
