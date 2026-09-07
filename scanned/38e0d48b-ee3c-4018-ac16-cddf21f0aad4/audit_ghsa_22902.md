# [M] Keycloak Authentication Error

## Summary
Severity: Medium
Advisory: GHSA-xvv8-8wh9-9fh2
CVE: CVE-2018-10894
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-xvv8-8wh9-9fh2
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-saml-adapter-core` — affected >=0 <4.4.0.Final
- Maven: `org.keycloak:keycloak-services` — affected >=0 <4.4.0.Final

## Details
It was found that SAML authentication in Keycloak 3.4.3.Final incorrectly authenticated expired certificates. A malicious user could use this to access unauthorized data or possibly conduct further attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-10894
- https://github.com/keycloak/keycloak/commit/812e76c39b1e693e8f11e5549cca2c90631f372e
- https://access.redhat.com/errata/RHSA-2018:3592
- https://access.redhat.com/errata/RHSA-2018:3593
- https://access.redhat.com/errata/RHSA-2018:3595
- https://access.redhat.com/errata/RHSA-2019:0877
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10894
- https://github.com/keycloak/keycloak
