# [M] Keycloak Server Private SPI: Improper Access Control Allows Administrators to Bypass Attribute Visibility Restrictions and Modify Unmanaged User Profile Attributes

## Summary
Severity: Medium
Advisory: GHSA-v4jw-m6rm-399h
CVE: CVE-2026-0871
CWE: CWE-266, CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-02-27
Source: https://github.com/advisories/GHSA-v4jw-m6rm-399h
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-server-spi-private` — affected >=0 <26.5.2

## Details
A flaw was found in Keycloak. An administrator with `manage-users` permission can bypass the "Only administrators can view" setting for unmanaged attributes, allowing them to modify these attributes. This improper access control can lead to unauthorized changes to user profiles, even when the system is configured to restrict such modifications.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-0871
- https://github.com/keycloak/keycloak/issues/45873
- https://github.com/keycloak/keycloak/commit/9d0f679ecea405958f167fcd0f4a6db6ae32c3fa
- https://access.redhat.com/errata/RHSA-2026:2365
- https://access.redhat.com/errata/RHSA-2026:2366
- https://access.redhat.com/security/cve/CVE-2026-0871
- https://bugzilla.redhat.com/show_bug.cgi?id=2428881
- https://github.com/keycloak/keycloak
