# [M] Keycloak vulnerable to Improper Certificate Validation

## Summary
Severity: Medium
Advisory: GHSA-rpj2-w6fr-79hc
CVE: CVE-2020-35509
CWE: CWE-20, CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-08-24
Source: https://github.com/advisories/GHSA-rpj2-w6fr-79hc
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <14.0.0

## Details
keycloak accepts an expired certificate by the direct-grant authenticator because of missing time stamp validations. The highest threat from this vulnerability is to data confidentiality and integrity.

This issue was partially fixed in version [13.0.1](https://github.com/keycloak/keycloak/pull/6330) and more completely fixed in version [14.0.0](https://github.com/keycloak/keycloak/pull/8067).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35509
- https://github.com/keycloak/keycloak/pull/6330
- https://github.com/keycloak/keycloak/pull/8067
- https://github.com/keycloak/keycloak/commit/478319348bdfdb9b6d39122f41edf2af79f679bb
- https://access.redhat.com/security/cve/cve-2020-35509
- https://bugzilla.redhat.com/show_bug.cgi?id=1912427
- https://github.com/keycloak/keycloak
- https://github.com/keycloak/keycloak/blob/4f330f4a57cbfcf6202b60546518261c66e59a35/services/src/main/java/org/keycloak/authentication/authenticators/x509/ValidateX509CertificateUsername.java#L74-L76
