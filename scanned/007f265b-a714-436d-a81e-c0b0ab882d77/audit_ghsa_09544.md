# [M] Keycloak has a Time-of-check Time-of-use (TOCTOU) Race Condition

## Summary
Severity: Medium
Advisory: GHSA-pq65-77rc-7r8c
CVE: CVE-2026-9796
CWE: CWE-367
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-pq65-77rc-7r8c
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-server` — affected >=0 <26.6.4

## Details
A flaw was found in Keycloak. An authenticated administrator with the `manage-clients` role can exploit a Time-of-check to time-of-use (TOCTOU) vulnerability in the name-based admin role checks. This allows the attacker to escalate their privileges to `realm-admin` for all users within the realm, granting them extensive control over the system. The composite role relationship persists even after the attacker's own permissions are revoked and across system reboots.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9796
- https://github.com/keycloak/keycloak/issues/49427
- https://github.com/keycloak/keycloak/pull/49624
- https://github.com/keycloak/keycloak/commit/39cb8de54c8517efeda4baa8bc314fd40e9c6934
- https://access.redhat.com/errata/RHSA-2026:56523
- https://access.redhat.com/errata/RHSA-2026:56524
- https://access.redhat.com/security/cve/CVE-2026-9796
- https://bugzilla.redhat.com/show_bug.cgi?id=2482464
- https://github.com/keycloak/keycloak
