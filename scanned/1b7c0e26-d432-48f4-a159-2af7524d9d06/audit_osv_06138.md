# [M] Keycloak-services: keycloak-services: full-scope-disabled client policy validation bypass via omitted fullscopeallowed

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-18570
Aliases: CVE-2026-18570
Ecosystem: Bitnami
Published: 2026-08-31
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-18570
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=0 <26.7.3

## Details
A flaw was found in the full-scope-disabled client-policy executor within the keycloak-services component. This component is responsible for enforcing security policies during client registration and configuration in Red Hat Build of Keycloak. The issue occurs because the executor only validates the fullScopeAllowed field when it is explicitly provided in a request. By omitting this field, a delegated user can bypass the policy, resulting in a client created with full scope access. This allows the client to obtain tokens with unauthorized role mappings.

## References
- https://access.redhat.com/security/cve/CVE-2026-18570
- https://bugzilla.redhat.com/show_bug.cgi?id=2509756
- https://nvd.nist.gov/vuln/detail/CVE-2026-18570
