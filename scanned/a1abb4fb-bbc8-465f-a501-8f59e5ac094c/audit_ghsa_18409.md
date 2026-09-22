# [M] Keycloak Privilege Escalation Vulnerability in Admin Console (FGAPv2 Enabled)

## Summary
Severity: Medium
Advisory: GHSA-27gp-8389-hm4w
CVE: CVE-2025-7784
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-07-30
Source: https://github.com/advisories/GHSA-27gp-8389-hm4w
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=26.2.0 <26.2.6

## Details
A Privilege Escalation vulnerability was identified in the Keycloak identity and access management solution, specifically when FGAPv2 is enabled in version 26.2.x. The flaw lies in the admin permission enforcement logic, where a user with manage-users privileges can self-assign realm-admin rights. The escalation occurs due to missing privilege boundary checks in role mapping operations via the admin REST interface. A malicious administrator with limited permissions can exploit this by editing their own user roles, gaining unauthorized full access to realm configuration and user data.

This issue has been fixed in versions 26.2.6, and 26.3.0.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-27gp-8389-hm4w
- https://nvd.nist.gov/vuln/detail/CVE-2025-7784
- https://github.com/keycloak/keycloak/issues/41137
- https://github.com/keycloak/keycloak/pull/41168
- https://access.redhat.com/errata/RHSA-2025:12015
- https://access.redhat.com/errata/RHSA-2025:12016
- https://access.redhat.com/security/cve/CVE-2025-7784
- https://bugzilla.redhat.com/show_bug.cgi?id=2381861
- https://github.com/keycloak/keycloak
