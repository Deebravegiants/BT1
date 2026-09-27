# [H] Keycloak: UMA Policy Resource Injection Allows Unauthorized Cross-User Permission Grants

## Summary
Severity: High
Advisory: GHSA-f2hx-5fx3-hmcv
CVE: CVE-2026-4636
CWE: CWE-551
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-f2hx-5fx3-hmcv
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.5.7

## Details
A flaw was found in Keycloak. An authenticated user with the uma_protection role can bypass User-Managed Access (UMA) policy validation. This allows the attacker to include resource identifiers owned by other users in a policy creation request, even if the URL path specifies an attacker-owned resource. Consequently, the attacker gains unauthorized permissions to victim-owned resources, enabling them to obtain a Requesting Party Token (RPT) and access sensitive information or perform unauthorized actions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4636
- https://github.com/keycloak/keycloak/issues/47717
- https://github.com/keycloak/keycloak/commit/995832f8b74b02833d106c8788bb7a78634aa725
- https://access.redhat.com/errata/RHSA-2026:6475
- https://access.redhat.com/errata/RHSA-2026:6476
- https://access.redhat.com/errata/RHSA-2026:6477
- https://access.redhat.com/errata/RHSA-2026:6478
- https://access.redhat.com/security/cve/CVE-2026-4636
- https://bugzilla.redhat.com/show_bug.cgi?id=2450251
- https://github.com/keycloak/keycloak
