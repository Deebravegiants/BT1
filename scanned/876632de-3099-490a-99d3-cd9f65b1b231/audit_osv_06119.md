# [M] Keycloak-services: keycloak-services: organization invitation link exposure allows unauthorized member creation

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-16072
Aliases: CVE-2026-16072
Ecosystem: Bitnami
Published: 2026-08-31
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-16072
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=0 <26.7.3

## Details
A flaw was found in the organization management component of Keycloak. A delegated administrator with permission to manage organizations can create an invitation for a non-existent email address and then retrieve the secret registration link directly through the application programming interface. By using this link, the administrator can create new user accounts and add them to the organization without having the required user management permissions or access to the invited email account. This allows an administrator to bypass security boundaries and add unauthorized members to an organization.

## References
- https://access.redhat.com/security/cve/CVE-2026-16072
- https://bugzilla.redhat.com/show_bug.cgi?id=2501721
- https://nvd.nist.gov/vuln/detail/CVE-2026-16072
