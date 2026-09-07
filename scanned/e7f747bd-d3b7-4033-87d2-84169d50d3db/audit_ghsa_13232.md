# [H] Keycloak vulnerable to Plaintext Storage of User Password

## Summary
Severity: High
Advisory: GHSA-5q66-v53q-pm35
CVE: CVE-2023-4918
CWE: CWE-256, CWE-319
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-12
Source: https://github.com/advisories/GHSA-5q66-v53q-pm35
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=22.0.2 <22.0.3

## Details
A flaw was discovered in Keycloak Core package.  When a user registers itself through registration flow, the "password" and "password-confirm" field from the form will occur as regular attributes in the users attributes. The password is also created, but the user attributes must not be there. This way, any entities (all users and clients with proper rights/roles) are able to retrieve the users passwords in clear-text. 

### Impact
Passwords for self-registered users are stored as cleartext attributes associated with the user. 

### Mitigation
Disable self-registration for users in all realms until patched.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-5q66-v53q-pm35
- https://nvd.nist.gov/vuln/detail/CVE-2023-4918
- https://access.redhat.com/security/cve/CVE-2023-4918
- https://bugzilla.redhat.com/show_bug.cgi?id=2238588
- https://github.com/keycloak/keycloak
