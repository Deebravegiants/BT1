# [M]  Keycloak’s OpenID Connect Dynamic Client Registration feature affected by Server-Side Request Forgery (SSRF)

## Summary
Severity: Medium
Advisory: GHSA-7vw6-5q2f-7w5r
CVE: CVE-2026-1180
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-01-20
Source: https://github.com/advisories/GHSA-7vw6-5q2f-7w5r
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-adapter-core` — affected >=0

## Details
A flaw was identified in Keycloak’s OpenID Connect Dynamic Client Registration feature when clients authenticate using private_key_jwt. The issue allows a client to specify an arbitrary jwks_uri, which Keycloak then retrieves without validating the destination. This enables attackers to coerce the Keycloak server into making HTTP requests to internal or restricted network resources. As a result, attackers can probe internal services and cloud metadata endpoints, creating an information disclosure and reconnaissance risk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1180
- https://github.com/keycloak/keycloak/issues/45645
- https://access.redhat.com/errata/RHSA-2026:6477
- https://access.redhat.com/errata/RHSA-2026:6478
- https://access.redhat.com/security/cve/CVE-2026-1180
- https://bugzilla.redhat.com/show_bug.cgi?id=2430781
- https://github.com/keycloak/keycloak
