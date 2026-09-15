# [M] Keycloak: Information Disclosure via evaluate-scopes Admin API

## Summary
Severity: Medium
Advisory: GHSA-rrv7-3mqf-hxfr
CVE: CVE-2026-37978
CWE: CWE-639
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-rrv7-3mqf-hxfr
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.6.2

## Details
A flaw was found in Keycloak. A low-privilege administrator with the 'view-clients' role can exploit this by invoking the 'evaluate-scopes' Admin API endpoints with an arbitrary user ID (userId) parameter. This vulnerability allows for cross-role personally identifiable information (PII) leakage, enabling unauthorized visibility into user identities and authorizations across the realm. Exploitation is possible remotely via network access to the Admin API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-37978
- https://github.com/keycloak/keycloak/commit/492d1f04cdad425dadb9d5e1faa94dd17a875573
- https://github.com/keycloak/keycloak/commit/ba9a18744dcec2ef46f284d25c1c0aa1c962a500
- https://access.redhat.com/errata/RHSA-2026:19596
- https://access.redhat.com/errata/RHSA-2026:19597
- https://access.redhat.com/security/cve/CVE-2026-37978
- https://bugzilla.redhat.com/show_bug.cgi?id=2455327
- https://github.com/keycloak/keycloak
