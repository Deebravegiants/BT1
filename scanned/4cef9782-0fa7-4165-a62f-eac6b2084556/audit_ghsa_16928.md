# [H] WildFly Elytron: SSRF security issue

## Summary
Severity: High
Advisory: GHSA-v4mm-q8fv-r2w5
CVE: CVE-2024-1233
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-04-09
Source: https://github.com/advisories/GHSA-v4mm-q8fv-r2w5
Type: github-advisory

## Affected
- Maven: `org.wildfly.security:wildfly-elytron-realm-token` — affected >=0

## Details
A flaw was found in` JwtValidator.resolvePublicKey` in JBoss EAP, where the validator checks jku and sends a HTTP request. During this process, no whitelisting or other filtering behavior is performed on the destination URL address, which may result in a server-side request forgery (SSRF) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1233
- https://github.com/wildfly/wildfly/pull/17812/commits/0c02350bc0d84287bed46e7c32f90b36e50d3523
- https://github.com/wildfly/wildfly/commit/aa151a00d75d6dbc4a1bf1b68d58b9de3087bb62
- https://access.redhat.com/errata/RHSA-2024:3559
- https://access.redhat.com/errata/RHSA-2024:3560
- https://access.redhat.com/errata/RHSA-2024:3561
- https://access.redhat.com/errata/RHSA-2024:3563
- https://access.redhat.com/errata/RHSA-2024:3580
- https://access.redhat.com/errata/RHSA-2024:3581
- https://access.redhat.com/errata/RHSA-2024:3583
- https://access.redhat.com/errata/RHSA-2025:9582
- https://access.redhat.com/errata/RHSA-2025:9583
- https://access.redhat.com/security/cve/CVE-2024-1233
- https://bugzilla.redhat.com/show_bug.cgi?id=2262849
- https://github.com/wildfly-security/wildfly-elytron
- https://issues.redhat.com/browse/WFLY-19226
