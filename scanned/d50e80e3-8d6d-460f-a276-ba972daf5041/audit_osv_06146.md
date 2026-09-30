# [M] Keycloak: keycloak: attacker can re-enable and take over disabled clients via registration access token

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-9705
Aliases: CVE-2026-9705
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-9705
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=26.6.0 <26.6.4

## Details
A flaw was found in Keycloak's client registration service. A remote attacker, possessing a previously issued Registration Access Token (RAT), could exploit this vulnerability to re-enable a client that an administrator had explicitly disabled. This bypasses security controls, allowing the attacker to reset the client's secret and potentially regain privileged API access. The primary impact includes unauthorized information disclosure and potential integrity compromise.

## References
- https://access.redhat.com/errata/RHSA-2026:30049
- https://access.redhat.com/errata/RHSA-2026:30050
- https://access.redhat.com/errata/RHSA-2026:30083
- https://access.redhat.com/errata/RHSA-2026:30084
- https://access.redhat.com/security/cve/CVE-2026-9705
- https://bugzilla.redhat.com/show_bug.cgi?id=2481878
- https://nvd.nist.gov/vuln/detail/CVE-2026-9705
