# [M] Keycloak is vulnerable to IDN homograph attack

## Summary
Severity: Medium
Advisory: GHSA-pf38-cw3p-22q9
CVE: CVE-2021-3424
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-04-28
Source: https://github.com/advisories/GHSA-pf38-cw3p-22q9
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <18.0.0

## Details
A flaw was found in keycloak as shipped in Red Hat Single Sign-On 7.4 where IDN homograph attacks are possible. A malicious user can register himself with a name already registered and trick admin to grant him extra privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3424
- https://bugzilla.redhat.com/show_bug.cgi?id=1933320
- https://github.com/keycloak/keycloak
