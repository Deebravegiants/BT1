# [M] Keycloak XSS via use of malicious payload as group name when creating new group from admin console

## Summary
Severity: Medium
Advisory: GHSA-fqc7-5xxc-ph7r
CVE: CVE-2022-0225
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-08-27
Source: https://github.com/advisories/GHSA-fqc7-5xxc-ph7r
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0

## Details
A flaw was found in Keycloak. This flaw allows a privileged attacker to use the malicious payload as the group name while creating a new group from the admin console, leading to a stored Cross-site scripting (XSS) attack.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-755v-r4x4-qf7m
- https://nvd.nist.gov/vuln/detail/CVE-2022-0225
- https://bugzilla.redhat.com/show_bug.cgi?id=2040268
- https://github.com/keycloak/keycloak
