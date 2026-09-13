# [M] Keycloak does not invalidate offline sessions when the offline_access scope is removed

## Summary
Severity: Medium
Advisory: GHSA-895x-rfqp-jh5c
CVE: CVE-2025-12110
CWE: CWE-613
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-23
Source: https://github.com/advisories/GHSA-895x-rfqp-jh5c
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.2.3

## Details
A flaw was found in Keycloak. An offline session continues to be valid when the offline_access scope is removed from the client. The refresh token is accepted and you can continue to request new tokens for the session. As it can lead to a situation where an administrator removes the scope, and assumes that offline sessions are no longer available, but they are.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-12110
- https://github.com/keycloak/keycloak/pull/43790
- https://github.com/keycloak/keycloak/commit/54e1c8af1e089ad33d32e0f2792610e4b8df421b
- https://github.com/keycloak/keycloak/commit/c830a27928cac4294619af7d147bdff34d4a85e7
- https://access.redhat.com/errata/RHSA-2025:21370
- https://access.redhat.com/errata/RHSA-2025:21371
- https://access.redhat.com/errata/RHSA-2025:22088
- https://access.redhat.com/errata/RHSA-2025:22089
- https://access.redhat.com/security/cve/CVE-2025-12110
- https://bugzilla.redhat.com/show_bug.cgi?id=2406033
- https://github.com/keycloak/keycloak
