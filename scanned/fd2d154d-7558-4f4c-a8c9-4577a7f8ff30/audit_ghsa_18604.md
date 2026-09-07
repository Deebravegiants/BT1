# [M] Keycloak error_description injection on error pages that can trigger phishing attacks

## Summary
Severity: Medium
Advisory: GHSA-27gc-wj6x-9w55
CVE: CVE-2025-10044
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-10-17
Source: https://github.com/advisories/GHSA-27gc-wj6x-9w55
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-account-ui` — affected >=0 <26.2.9
- Maven: `org.keycloak:keycloak-account-ui` — affected >=26.3.0 <26.3.4
- Maven: `org.keycloak:keycloak-admin-ui` — affected >=0 <26.2.9
- Maven: `org.keycloak:keycloak-admin-ui` — affected >=26.3.0 <26.3.4

## Details
Keycloak’s account console accepts arbitrary text in the `error_description` query parameter. This text is directly rendered in error pages without validation or sanitization. While HTML encoding prevents XSS, an attacker can craft URLs with misleading messages (e.g., fake support phone numbers or URLs), which are displayed within the trusted Keycloak UI. This creates a phishing vector, potentially tricking users into contacting malicious actors.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-27gc-wj6x-9w55
- https://nvd.nist.gov/vuln/detail/CVE-2025-10044
- https://github.com/keycloak/keycloak/pull/42035
- https://access.redhat.com/errata/RHSA-2025:16399
- https://access.redhat.com/errata/RHSA-2025:16400
- https://access.redhat.com/security/cve/CVE-2025-10044
- https://bugzilla.redhat.com/show_bug.cgi?id=2393551
- https://github.com/keycloak/keycloak
