# [C] Keycloak: Unauthenticated account takeover via reset-credentials flow bypass

## Summary
Severity: Critical
Advisory: GHSA-4gv3-mc9p-5wqc
CVE: CVE-2026-18963
CWE: CWE-640
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-4gv3-mc9p-5wqc
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=26.0.0 <26.4.15
- Maven: `org.keycloak:keycloak-services` — affected >=26.5.0 <26.6.6
- Maven: `org.keycloak:keycloak-services` — affected >=26.7.0 <26.7.2

## Details
A flaw was found in the reset-credentials flow of the keycloak-services component, which is the core engine for identity and access management in Red Hat Build of Keycloak. The issue allows an unauthenticated attacker to force the password reset process for any user without needing to click the required email verification link. This can result in the attacker gaining full control over target user accounts by directly setting new credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-18963
- https://github.com/keycloak/keycloak/issues/51833
- https://github.com/keycloak/keycloak/pull/51844
- https://github.com/keycloak/keycloak/commit/dc2d4e524b4dae85aedc87ca28b9e4fa567d56c1
- https://access.redhat.com/errata/RHSA-2026:56519
- https://access.redhat.com/errata/RHSA-2026:56520
- https://access.redhat.com/errata/RHSA-2026:56523
- https://access.redhat.com/errata/RHSA-2026:56524
- https://access.redhat.com/security/cve/CVE-2026-18963
- https://bugzilla.redhat.com/show_bug.cgi?id=2511595
- https://github.com/keycloak/keycloak
