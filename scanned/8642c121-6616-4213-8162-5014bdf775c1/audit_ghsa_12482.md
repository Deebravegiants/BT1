# [H] The redirect_uri validation logic allows for bypassing explicitly allowed hosts that would otherwise be restricted

## Summary
Severity: High
Advisory: GHSA-mpwq-j3xf-7m5w
CVE: CVE-2023-6291
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2023-12-21
Source: https://github.com/advisories/GHSA-mpwq-j3xf-7m5w
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <23.0.3

## Details
An issue was found in the redirect_uri validation logic that allows for a bypass of otherwise explicitly allowed hosts.

The problem arises in the verifyRedirectUri method, which attempts to enforce rules on user-controllable input, but essentially causes a desynchronization in how Keycloak and browsers interpret URLs. Keycloak, for example, receives "[www%2ekeycloak%2eorg%2fapp%2f:y@example.com](https://www%2ekeycloak%2eorg%2fapp%2f:y@example.com/)" and thinks the authority to be keycloak.org when it is actually example.com. This happens because the validation logic is performed on a URL decoded version, which no longer represents the original input.

### Acknowledgements
Karel Knibbe

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-mpwq-j3xf-7m5w
- https://nvd.nist.gov/vuln/detail/CVE-2023-6291
- https://github.com/keycloak/keycloak/commit/b2e91105315ccf2c1df549b4f6c5948322cbfd1b
- https://access.redhat.com/errata/RHSA-2023:7854
- https://access.redhat.com/errata/RHSA-2023:7855
- https://access.redhat.com/errata/RHSA-2023:7856
- https://access.redhat.com/errata/RHSA-2023:7857
- https://access.redhat.com/errata/RHSA-2023:7858
- https://access.redhat.com/errata/RHSA-2023:7860
- https://access.redhat.com/errata/RHSA-2023:7861
- https://access.redhat.com/security/cve/CVE-2023-6291
- https://bugzilla.redhat.com/show_bug.cgi?id=2251407
- https://github.com/keycloak/keycloak
