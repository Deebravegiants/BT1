# [M] Keycloak Vulnerable to Improper Handling of Insufficient Permissions or Privilege

## Summary
Severity: Medium
Advisory: GHSA-33j3-g875-37rp
CVE: CVE-2026-9792
CWE: CWE-280
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-33j3-g875-37rp
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=26.5.0 <26.6.3
- Maven: `org.keycloak:keycloak-services` — affected >=0

## Details
A flaw was found in Keycloak's Client Policies, specifically within the `org.keycloak.protocol.oidc` component. When certain condition providers (client-type, client-roles, client-attributes, client-scopes) are used to enforce security restrictions, the `reject-ropc-grant` executor is silently bypassed. This allows an unauthenticated remote attacker to obtain tokens via a Resource Owner Password Credentials (ROPC) grant, even when a policy is explicitly configured to block it. This bypass can lead to unauthorized access and information disclosure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9792
- https://github.com/keycloak/keycloak/issues/49436
- https://github.com/keycloak/keycloak/pull/49636
- https://github.com/keycloak/keycloak/pull/49637
- https://github.com/keycloak/keycloak/commit/13622ee0ffed91fd07ef444be2c858a7f356766d
- https://github.com/keycloak/keycloak/commit/2af73c16a4e49333779bb34bce65461d9af036a4
- https://github.com/keycloak/keycloak/commit/af5e3e8c60842bc1f3a78e6be414fe303f93163d
- https://access.redhat.com/errata/RHSA-2026:25097
- https://access.redhat.com/errata/RHSA-2026:25098
- https://access.redhat.com/errata/RHSA-2026:30049
- https://access.redhat.com/errata/RHSA-2026:30050
- https://access.redhat.com/security/cve/CVE-2026-9792
- https://bugzilla.redhat.com/show_bug.cgi?id=2482459
- https://github.com/keycloak/keycloak
