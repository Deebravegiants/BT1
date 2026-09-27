# [H] Keycloak exposes sensitive information in Pushed Authorization Requests (PAR)

## Summary
Severity: High
Advisory: GHSA-69fp-7c8p-crjr
CVE: CVE-2024-4540
CWE: CWE-200, CWE-922
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-10
Source: https://github.com/advisories/GHSA-69fp-7c8p-crjr
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <24.0.5

## Details
A flaw was found in Keycloak in the OAuth 2.0 Pushed Authorization Requests (PAR). Client provided parameters were found to be included in plain text in the KC_RESTART cookie returned by the authorization server's HTTP response to a request_uri authorization request. This could lead to an information disclosure vulnerability.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-69fp-7c8p-crjr
- https://nvd.nist.gov/vuln/detail/CVE-2024-4540
- https://github.com/keycloak/keycloak/commit/2191cc26ae6deb52eeaf74046027b65804d16fd0
- https://access.redhat.com/errata/RHSA-2024:3566
- https://access.redhat.com/errata/RHSA-2024:3567
- https://access.redhat.com/errata/RHSA-2024:3568
- https://access.redhat.com/errata/RHSA-2024:3570
- https://access.redhat.com/errata/RHSA-2024:3572
- https://access.redhat.com/errata/RHSA-2024:3573
- https://access.redhat.com/errata/RHSA-2024:3574
- https://access.redhat.com/errata/RHSA-2024:3575
- https://access.redhat.com/errata/RHSA-2024:3576
- https://access.redhat.com/security/cve/CVE-2024-4540
- https://bugzilla.redhat.com/show_bug.cgi?id=2279303
- https://github.com/keycloak/keycloak
