# [M] Keycloak Cross-site Scripting (XSS) via assertion consumer service URL in SAML POST-binding flow

## Summary
Severity: Medium
Advisory: GHSA-8rmm-gm28-pj8q
CVE: CVE-2023-6717
CWE: CWE-20, CWE-601, CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2024-04-17
Source: https://github.com/advisories/GHSA-8rmm-gm28-pj8q
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <22.0.10
- Maven: `org.keycloak:keycloak-services` — affected >=23.0.0 <24.0.3

## Details
Keycloak allows arbitrary URLs as SAML Assertion Consumer Service POST Binding URL (ACS), including JavaScript URIs (javascript:).

Allowing JavaScript URIs in combination with HTML forms leads to JavaScript evaluation in the context of the embedding origin on form submission.

#### Acknowledgements:
Special thanks to Lauritz Holtmann for reporting this issue and helping us improve our project.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-8rmm-gm28-pj8q
- https://nvd.nist.gov/vuln/detail/CVE-2023-6717
- https://access.redhat.com/errata/RHSA-2024:1353
- https://access.redhat.com/errata/RHSA-2024:1867
- https://access.redhat.com/errata/RHSA-2024:1868
- https://access.redhat.com/errata/RHSA-2024:2945
- https://access.redhat.com/errata/RHSA-2024:4057
- https://access.redhat.com/security/cve/CVE-2023-6717
- https://bugzilla.redhat.com/show_bug.cgi?id=2253952
- https://github.com/keycloak/keycloak
