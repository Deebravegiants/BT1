# [C] Apache Camel: KeycloakSecurityPolicy does not validate issuer of JWT tokens against configured realm

## Summary
Severity: Critical
Advisory: GHSA-c3f3-cc42-xr9v
CVE: CVE-2026-23552
CWE: CWE-346
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-23
Source: https://github.com/advisories/GHSA-c3f3-cc42-xr9v
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-keycloak` — affected >=4.15.0 <4.18.0

## Details
Cross-Realm Token Acceptance Bypass in KeycloakSecurityPolicy Apache Camel Keycloak component. 

The Camel-Keycloak KeycloakSecurityPolicy does not validate the iss (issuer) claim of JWT tokens against the configured realm. A token issued by one Keycloak realm is silently accepted by a policy configured for a completely different realm, breaking tenant isolation.
This issue affects Apache Camel: from 4.15.0 before 4.18.0.

Users are recommended to upgrade to version 4.18.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-23552
- https://github.com/apache/camel/commit/c1ed776e3a4fa23d15acf4b9a48fdf758d4316ff
- https://camel.apache.org/security/CVE-2026-23552.html
- https://github.com/apache/camel
- https://github.com/oscerd/CVE-2026-23552
- https://issues.apache.org/jira/browse/CAMEL-22854
- http://www.openwall.com/lists/oss-security/2026/02/18/7
