# [M] Keycloak: keycloak: information disclosure through arbitrary filesystem path probing

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-9083
Aliases: CVE-2026-9083
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-9083
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=26.6.0 <26.6.4

## Details
A flaw was found in Keycloak. A realm administrator with the "manage-realm" role can exploit this vulnerability by submitting an arbitrary filesystem path as a keystore parameter when creating a key provider component. This allows the administrator to probe arbitrary filesystem paths, determining which files exist and are readable by the Keycloak process. This information disclosure could be used to identify high-value targets for follow-on attacks.

## References
- https://access.redhat.com/errata/RHSA-2026:30049
- https://access.redhat.com/errata/RHSA-2026:30050
- https://access.redhat.com/errata/RHSA-2026:30083
- https://access.redhat.com/errata/RHSA-2026:30084
- https://access.redhat.com/security/cve/CVE-2026-9083
- https://bugzilla.redhat.com/show_bug.cgi?id=2480168
- https://nvd.nist.gov/vuln/detail/CVE-2026-9083
