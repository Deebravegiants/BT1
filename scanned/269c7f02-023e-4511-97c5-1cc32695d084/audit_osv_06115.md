# [H] Keycloak-services: keycloak-services: dcr protocol mapper type-swap policy bypass allows privilege escalation

## Summary
Severity: High
Advisory: BIT-keycloak-2026-15572
Aliases: CVE-2026-15572
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-15572
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=26.6.0 <26.6.5

## Details
A flaw was found in Keycloak's Dynamic Client Registration (DCR) security policy management. The "Allowed Protocol Mapper Types" policy, which restricts which types of data mappers a client can use, fails to re-validate the mapper type during a client update if the mapper's configuration remains unchanged. An attacker with client registration privileges can exploit this by first registering an allowed mapper type with a malicious configuration and then swapping it for a restricted, high-privilege mapper type (such as one that hardcodes administrative roles). This allows the attacker to gain full administrative access to the Keycloak realm.

## References
- https://access.redhat.com/errata/RHSA-2026:50846
- https://access.redhat.com/errata/RHSA-2026:50847
- https://access.redhat.com/errata/RHSA-2026:50848
- https://access.redhat.com/errata/RHSA-2026:50849
- https://access.redhat.com/security/cve/CVE-2026-15572
- https://bugzilla.redhat.com/show_bug.cgi?id=2499592
- https://nvd.nist.gov/vuln/detail/CVE-2026-15572
