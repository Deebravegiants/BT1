# [M] Keycloak Insufficient Session Expiry

## Summary
Severity: Medium
Advisory: GHSA-8xj2-47xw-q78c
CVE: CVE-2020-1724
CWE: CWE-613
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8xj2-47xw-q78c
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <9.0.2

## Details
A flaw was found in Keycloak in versions before 9.0.2. This flaw allows a malicious user that is currently logged in, to see the personal information of a previously logged out user in the account manager section.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1724
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1724
- https://github.com/keycloak/keycloak
