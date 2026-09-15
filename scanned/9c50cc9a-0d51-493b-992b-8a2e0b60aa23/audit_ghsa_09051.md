# [M] Keycloak Vulnerable to Improper Validation of Specified Quantity in Input

## Summary
Severity: Medium
Advisory: GHSA-f6r7-6w34-x2gp
CVE: CVE-2026-9801
CWE: CWE-1284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-f6r7-6w34-x2gp
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-ldap-federation` — affected >=0 <26.6.3

## Details
A flaw was found in Keycloak. A remote attacker with high privileges, such as a realm administrator configuring a malicious Lightweight Directory Access Protocol (LDAP) server or an attacker compromising an upstream LDAP server, could exploit this vulnerability. By sending a malformed LDAP password policy response during a password authentication request, the attacker can trigger an OutOfMemoryError. This causes the Keycloak Java Virtual Machine (JVM) to terminate, leading to a denial of service (DoS) for all realms on the affected node.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9801
- https://github.com/keycloak/keycloak/issues/49434
- https://github.com/keycloak/keycloak/pull/49514
- https://github.com/keycloak/keycloak/commit/2c4fe42235ba8c265b1da3a30541a270d5bd8c39
- https://access.redhat.com/errata/RHSA-2026:25097
- https://access.redhat.com/errata/RHSA-2026:25098
- https://access.redhat.com/errata/RHSA-2026:30049
- https://access.redhat.com/errata/RHSA-2026:30050
- https://access.redhat.com/security/cve/CVE-2026-9801
- https://bugzilla.redhat.com/show_bug.cgi?id=2482473
- https://github.com/keycloak/keycloak
