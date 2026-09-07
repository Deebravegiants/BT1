# [H] Keycloak allows anyone to register new security device or key for any user by using WebAuthn password-less login flow

## Summary
Severity: High
Advisory: GHSA-qpq9-jpv4-6gwr
CVE: CVE-2021-3632
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-27
Source: https://github.com/advisories/GHSA-qpq9-jpv4-6gwr
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <15.1.0

## Details
A flaw was found in Keycloak. This vulnerability allows anyone to register a new security device or key when there is not a device already registered for any user by using the WebAuthn password-less login flow.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3632
- https://github.com/keycloak/keycloak/pull/8203
- https://github.com/keycloak/keycloak/commit/65480cb5a11630909c086f79d396004499fbd1e4
- https://access.redhat.com/security/cve/CVE-2021-3632
- https://bugzilla.redhat.com/show_bug.cgi?id=1978196
- https://github.com/keycloak/keycloak
- https://issues.redhat.com/browse/KEYCLOAK-18500
