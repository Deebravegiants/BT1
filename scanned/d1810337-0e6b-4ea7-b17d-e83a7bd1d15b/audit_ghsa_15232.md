# [M] keycloak-core: open redirect via "form_post.jwt" JARM response mode

## Summary
Severity: Medium
Advisory: GHSA-9vm7-v8wj-3fqw
CVE: CVE-2023-6927
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-01-23
Source: https://github.com/advisories/GHSA-9vm7-v8wj-3fqw
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <23.0.4

## Details
An incomplete fix was found in Keycloak Core patch. An attacker can steal authorization codes or tokens from clients using a wildcard in the JARM response mode "form_post.jwt". It is observed that changing the response_mode parameter in the original proof of concept from "form_post" to "form_post.jwt" can bypass the security patch implemented to address CVE-2023-6134.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-9vm7-v8wj-3fqw
- https://nvd.nist.gov/vuln/detail/CVE-2023-6927
- https://access.redhat.com/errata/RHSA-2024:0094
- https://access.redhat.com/errata/RHSA-2024:0095
- https://access.redhat.com/errata/RHSA-2024:0096
- https://access.redhat.com/errata/RHSA-2024:0097
- https://access.redhat.com/errata/RHSA-2024:0098
- https://access.redhat.com/errata/RHSA-2024:0100
- https://access.redhat.com/errata/RHSA-2024:0101
- https://access.redhat.com/security/cve/CVE-2023-6927
- https://bugzilla.redhat.com/show_bug.cgi?id=2255027
- https://github.com/keycloak/keycloak
