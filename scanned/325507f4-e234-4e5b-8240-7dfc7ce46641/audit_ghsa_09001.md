# [M] Keycloak has an Authentication Bypass by Primary Weakness

## Summary
Severity: Medium
Advisory: GHSA-q6h7-xxp7-7429
CVE: CVE-2026-9798
CWE: CWE-305
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-q6h7-xxp7-7429
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0
- Maven: `org.keycloak:keycloak-services` — affected >=26.5.0

## Details
A flaw was found in Keycloak, an open-source identity and access management solution. When a user account is temporarily locked due to repeated failed login attempts, an attacker with valid client credentials can exploit the Client-Initiated Backchannel Authentication (CIBA) flow to bypass this brute-force protection. This allows continued authentication attempts and token issuance even when the account should be locked, potentially enabling further unauthorized access attempts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9798
- https://github.com/keycloak/keycloak/issues/49432
- https://github.com/keycloak/keycloak/pull/49791
- https://github.com/keycloak/keycloak/pull/49903
- https://github.com/keycloak/keycloak/pull/49905
- https://github.com/keycloak/keycloak/commit/11c2695064cd93da1d333df3f69d4a4141e86c29
- https://github.com/keycloak/keycloak/commit/2edc6b112e2dedce63062b89ab3c7ae542e0d9ac
- https://github.com/keycloak/keycloak/commit/a11e3254efc16ae72ce5092b93b9f557a4ba43ae
- https://access.redhat.com/errata/RHSA-2026:50846
- https://access.redhat.com/errata/RHSA-2026:50847
- https://access.redhat.com/errata/RHSA-2026:50848
- https://access.redhat.com/errata/RHSA-2026:50849
- https://access.redhat.com/security/cve/CVE-2026-9798
- https://bugzilla.redhat.com/show_bug.cgi?id=2482470
- https://github.com/keycloak/keycloak
