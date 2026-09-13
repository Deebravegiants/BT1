# [M] Keycloak Authorization Bypass vulnerability

## Summary
Severity: Medium
Advisory: GHSA-46c8-635v-68r2
CVE: CVE-2023-6544
CWE: CWE-625
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-04-17
Source: https://github.com/advisories/GHSA-46c8-635v-68r2
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <22.0.10
- Maven: `org.keycloak:keycloak-services` — affected >=23.0.0 <24.0.3

## Details
Due to a permissive regular expression hardcoded for filtering allowed hosts to register a dynamic client, a malicious user with enough information about the environment could benefit and jeopardize an environment with this specific Dynamic Client Registration with TrustedDomain configuration previously unauthorized.

#### Acknowledgements:
Special thanks to Bastian Kanbach for reporting this issue and helping us improve our security.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-46c8-635v-68r2
- https://nvd.nist.gov/vuln/detail/CVE-2023-6544
- https://access.redhat.com/errata/RHSA-2024:1860
- https://access.redhat.com/errata/RHSA-2024:1861
- https://access.redhat.com/errata/RHSA-2024:1862
- https://access.redhat.com/errata/RHSA-2024:1864
- https://access.redhat.com/errata/RHSA-2024:1866
- https://access.redhat.com/errata/RHSA-2024:1867
- https://access.redhat.com/errata/RHSA-2024:1868
- https://access.redhat.com/security/cve/CVE-2023-6544
- https://bugzilla.redhat.com/show_bug.cgi?id=2253116
- https://github.com/keycloak/keycloak
