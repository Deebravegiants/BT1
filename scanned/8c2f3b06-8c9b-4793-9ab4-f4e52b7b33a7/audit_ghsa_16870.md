# [H] WildFly Elytron: OIDC app attempting to access the second tenant, the user should be prompted to log

## Summary
Severity: High
Advisory: GHSA-jpmx-996v-48fm
CVE: CVE-2023-6236
CWE: CWE-345
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-04-10
Source: https://github.com/advisories/GHSA-jpmx-996v-48fm
Type: github-advisory

## Affected
- Maven: `org.wildfly.security:wildfly-elytron-http-oidc` — affected >=0 <2.2.5.Final

## Details
A flaw was found in JBoss EAP. When an OIDC app that serves multiple tenants attempts to access the second tenant, it should prompt the user to log in again since the second tenant is secured with a different OIDC configuration. The underlying issue is in OidcSessionTokenStore when determining if a cached token should be used or not. This logic needs to be updated to take into account the new "provider-url" option in addition to the "realm" option.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6236
- https://github.com/wildfly-security/wildfly-elytron/commit/6e94ec3476a279c0a130186209c50a2991ba4c84
- https://access.redhat.com/errata/RHSA-2024:3580
- https://access.redhat.com/errata/RHSA-2024:3581
- https://access.redhat.com/errata/RHSA-2024:3583
- https://access.redhat.com/security/cve/CVE-2023-6236
- https://bugzilla.redhat.com/show_bug.cgi?id=2250812
- https://github.com/wildfly-security/wildfly-elytron
