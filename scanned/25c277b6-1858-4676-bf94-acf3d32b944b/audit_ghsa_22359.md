# [H] JBoss Keycloak CSRF Vulnerability

## Summary
Severity: High
Advisory: GHSA-xr6q-qqx7-553g
CVE: CVE-2014-3709
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-xr6q-qqx7-553g
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <1.0.3.Final

## Details
The `org.keycloak.services.resources.SocialResource.callback` method in JBoss KeyCloak before 1.0.3.Final allows remote attackers to conduct cross-site request forgery (CSRF) attacks by leveraging lack of CSRF protection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3709
- https://github.com/keycloak/keycloak/commit/bb132e1aa0b3b3a123883d0b8d0b788337df956d
- https://bugzilla.redhat.com/show_bug.cgi?id=1154971
- https://issues.jboss.org/browse/KEYCLOAK-765
- https://web.archive.org/web/20200227141715/http://www.securityfocus.com/bid/101508
