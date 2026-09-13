# [H] Keycloak path traversal vulnerability in redirection validation

## Summary
Severity: High
Advisory: GHSA-72vp-xfrc-42xm
CVE: CVE-2024-1132
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-04-17
Source: https://github.com/advisories/GHSA-72vp-xfrc-42xm
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <22.0.10
- Maven: `org.keycloak:keycloak-services` — affected >=23.0.0 <24.0.3

## Details
A flaw was found in Keycloak, where it does not properly validate URLs included in a redirect. An attacker can use this flaw to construct a malicious request to bypass validation and access other URLs and potentially sensitive information within the domain or possibly conduct further attacks. This flaw affects any client that utilizes a wildcard in the Valid Redirect URIs field.

#### Acknowledgements:
Special thanks to Axel Flamcourt for reporting this issue and helping us improve our project.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-72vp-xfrc-42xm
- https://nvd.nist.gov/vuln/detail/CVE-2024-1132
- https://github.com/keycloak/keycloak
- https://bugzilla.redhat.com/show_bug.cgi?id=2262117
- https://access.redhat.com/security/cve/CVE-2024-1132
- https://access.redhat.com/errata/RHSA-2024:3989
- https://access.redhat.com/errata/RHSA-2024:3919
- https://access.redhat.com/errata/RHSA-2024:3762
- https://access.redhat.com/errata/RHSA-2024:3752
- https://access.redhat.com/errata/RHSA-2024:2945
- https://access.redhat.com/errata/RHSA-2024:1868
- https://access.redhat.com/errata/RHSA-2024:1867
- https://access.redhat.com/errata/RHSA-2024:1866
- https://access.redhat.com/errata/RHSA-2024:1864
- https://access.redhat.com/errata/RHSA-2024:1862
- https://access.redhat.com/errata/RHSA-2024:1861
- https://access.redhat.com/errata/RHSA-2024:1860
