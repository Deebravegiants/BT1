# [M] Keycloak has lack of validation of access token on client registrations endpoint

## Summary
Severity: Medium
Advisory: GHSA-v436-q368-hvgg
CVE: CVE-2023-0091
CWE: CWE-284, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-01-12
Source: https://github.com/advisories/GHSA-v436-q368-hvgg
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <20.0.3

## Details
When a service account with the create-client or manage-clients role can use the client-registration endpoints to create/manage clients with an access token.

If the access token is leaked, there is an option to revoke the specific token. However, the check is not performed in client-registration endpoints.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-v436-q368-hvgg
- https://nvd.nist.gov/vuln/detail/CVE-2023-0091
- https://access.redhat.com/security/cve/CVE-2023-0091
- https://github.com/keycloak/keycloak
