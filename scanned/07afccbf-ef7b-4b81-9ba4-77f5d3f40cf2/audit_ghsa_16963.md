# [H] Keycloak's unvalidated cross-origin messages in checkLoginIframe leads to DDoS

## Summary
Severity: High
Advisory: GHSA-m6q9-p373-g5q8
CVE: CVE-2024-1249
CWE: CWE-346
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-17
Source: https://github.com/advisories/GHSA-m6q9-p373-g5q8
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <22.0.10
- Maven: `org.keycloak:keycloak-services` — affected >=23.0.0 <24.0.3

## Details
A potential security flaw in the "checkLoginIframe" which allows unvalidated cross-origin messages, enabling potential DDoS attacks. By exploiting this vulnerability, attackers could coordinate to send millions of requests in seconds using simple code, significantly impacting the application's availability without proper origin validation for incoming messages.

#### Acknowledgements
Special thanks to Adriano Márcio Monteiro from BRZTEC for reporting this issue and helping us improve our project.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-m6q9-p373-g5q8
- https://nvd.nist.gov/vuln/detail/CVE-2024-1249
- https://github.com/keycloak/keycloak/commit/9d9817e15a07195f16f554b7f60ee3a918369e26
- https://github.com/keycloak/keycloak/commit/e3598a53678a1e3698e78eb71e04ba10ca32e5e2
- https://access.redhat.com/errata/RHSA-2024:1860
- https://access.redhat.com/errata/RHSA-2024:1861
- https://access.redhat.com/errata/RHSA-2024:1862
- https://access.redhat.com/errata/RHSA-2024:1864
- https://access.redhat.com/errata/RHSA-2024:1866
- https://access.redhat.com/errata/RHSA-2024:1867
- https://access.redhat.com/errata/RHSA-2024:1868
- https://access.redhat.com/errata/RHSA-2024:2945
- https://access.redhat.com/errata/RHSA-2024:4057
- https://access.redhat.com/security/cve/CVE-2024-1249
- https://bugzilla.redhat.com/show_bug.cgi?id=2262918
- https://github.com/keycloak/keycloak
