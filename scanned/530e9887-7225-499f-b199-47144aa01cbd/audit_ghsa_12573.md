# [M] Keycloak Untrusted Certificate Validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5cc8-pgp5-7mpm
CVE: CVE-2023-1664
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-06-30
Source: https://github.com/advisories/GHSA-5cc8-pgp5-7mpm
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <21.1.2

## Details
A flaw was found in keycloak-core. This flaw considers the scenario when using X509 Client Certificate Authenticatior with the option "Revalidate Client Certificate". A user may be able to choose, if directly connect to keycloak (not passing via reverse proxy) a specific certificate. If there's a configuration error in KC_SPI_TRUSTSTORE_FILE_FILE the authenticator allows even with the "Cannot validate client certificate trust: Truststore not available" message as there's no certificate to trust against.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-5cc8-pgp5-7mpm
- https://nvd.nist.gov/vuln/detail/CVE-2023-1664
- https://access.redhat.com/security/cve/CVE-2023-1664
- https://bugzilla.redhat.com/show_bug.cgi?id=2182196&comment#0
- https://github.com/keycloak/keycloak
