# [M] Keycloak-services: keycloak-services: ldap entry-dn user search bypasses configured users dn boundary

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-16071
Aliases: CVE-2026-16071
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-16071
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=26.6.0 <26.6.5

## Details
A flaw was found in the LDAP storage provider of Keycloak, which is used to federate user identities from external directories. The issue occurs when a delegated administrator performs a search using a specific LDAP entry Distinguished Name (DN). Due to missing validation, the system allows lookups for users located outside the configured search boundary, leading to the disclosure of account information from unauthorized parts of the directory and unintended importing of those users into local storage.

## References
- https://access.redhat.com/errata/RHSA-2026:50846
- https://access.redhat.com/errata/RHSA-2026:50847
- https://access.redhat.com/errata/RHSA-2026:50848
- https://access.redhat.com/errata/RHSA-2026:50849
- https://access.redhat.com/security/cve/CVE-2026-16071
- https://bugzilla.redhat.com/show_bug.cgi?id=2501720
- https://nvd.nist.gov/vuln/detail/CVE-2026-16071
