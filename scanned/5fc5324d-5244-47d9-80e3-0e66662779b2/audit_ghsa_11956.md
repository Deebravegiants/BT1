# [M] Keycloak: Improper Access Control Leading to MFA Deletion and Account Takeover in Keycloak Account REST API

## Summary
Severity: Medium
Advisory: GHSA-8g9r-9wjw-37j4
CVE: CVE-2026-3429
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-8g9r-9wjw-37j4
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0

## Details
A flaw was identified in the Account REST API of Keycloak that allows a user authenticated at a lower security level to perform sensitive actions intended only for higher-assurance sessions. Specifically, an attacker who has already obtained a victim’s password can delete the victim’s registered MFA/OTP credential without first proving possession of that factor. The attacker can then register their own MFA device, effectively taking full control of the account. This weakness undermines the intended protection provided by multi-factor authentication.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3429
- https://github.com/keycloak/keycloak/issues/47069
- https://github.com/keycloak/keycloak/commit/68f5779230d08825e6a4b4e23471fade16434178
- https://access.redhat.com/errata/RHSA-2026:6477
- https://access.redhat.com/errata/RHSA-2026:6478
- https://access.redhat.com/security/cve/CVE-2026-3429
- https://bugzilla.redhat.com/show_bug.cgi?id=2443771
- https://github.com/keycloak/keycloak
