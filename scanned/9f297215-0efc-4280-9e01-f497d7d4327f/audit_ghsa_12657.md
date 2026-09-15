# [H] Keycloak vulnerable to Improper Client Certificate Validation for OAuth/OpenID clients

## Summary
Severity: High
Advisory: GHSA-3qh5-qqj2-c78f
CVE: CVE-2023-2422
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-06-30
Source: https://github.com/advisories/GHSA-3qh5-qqj2-c78f
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <21.1.2

## Details
When a Keycloak server is configured to support mTLS authentication for OAuth/OpenID clients, it does not properly verify the client certificate chain. A client that possesses a proper certificate can authorize itself as any other client and therefore access data that belongs to other clients.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-3qh5-qqj2-c78f
- https://nvd.nist.gov/vuln/detail/CVE-2023-2422
- https://github.com/keycloak/keycloak/commit/5c6c55945a384bfd82e51283096204dcb6f63d91
- https://access.redhat.com/errata/RHSA-2023:3883
- https://access.redhat.com/errata/RHSA-2023:3884
- https://access.redhat.com/errata/RHSA-2023:3885
- https://access.redhat.com/errata/RHSA-2023:3888
- https://access.redhat.com/errata/RHSA-2023:3892
- https://access.redhat.com/security/cve/CVE-2023-2422
- https://bugzilla.redhat.com/show_bug.cgi?id=2191668
- https://github.com/keycloak/keycloak
