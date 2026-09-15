# [M] Improper Verification of Cryptographic Signature in keycloak

## Summary
Severity: Medium
Advisory: GHSA-4fgq-gq9g-3rw7
CVE: CVE-2019-10201
CWE: CWE-347
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2019-09-23
Source: https://github.com/advisories/GHSA-4fgq-gq9g-3rw7
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <7.0.0

## Details
It was found that Keycloak's SAML broker, versions up to 6.0.1, did not verify missing message signatures. If an attacker modifies the SAML Response and removes the <Signature> sections, the message is still accepted, and the message can be modified. An attacker could use this flaw to impersonate other users and gain access to sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10201
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10201
