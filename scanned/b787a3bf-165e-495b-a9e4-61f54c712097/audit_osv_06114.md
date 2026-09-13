# [H] Flaw in the legacy client-initiated account-linking endpoint of Keycloak

## Summary
Severity: High
Advisory: BIT-keycloak-2026-15571
Aliases: CVE-2026-15571
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-15571
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=0 <26.7.2

## Details
A flaw was found in the legacy client-initiated account-linking endpoint of Keycloak, a widely used open-source identity and access management solution. The mechanism used to protect the account-linking process from unauthorized requests relies on a hash that can be predicted by a malicious OIDC client. By tricking a user into authenticating, an attacker-controlled client can forge a valid linking URL to connect the victim's account to an attacker's external identity. This results in a full account takeover, allowing the attacker to log in as the victim.

## References
- https://access.redhat.com/errata/RHSA-2026:56523
- https://access.redhat.com/errata/RHSA-2026:56524
- https://nvd.nist.gov/vuln/detail/CVE-2026-15571
- https://access.redhat.com/security/cve/CVE-2026-15571
- https://bugzilla.redhat.com/show_bug.cgi?id=2499591
