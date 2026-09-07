# [M] JBoss KeyCloak Cross-site Scripting Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-px42-mr8m-cpgh
CVE: CVE-2014-3656
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-px42-mr8m-cpgh
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <1.1.0.Beta1

## Details
If a JBoss Keycloak application was configured to use `*` as a permitted web origin in the Keycloak administrative console, crafted requests to the `login-status-iframe.html` endpoint could inject arbitrary Javascript into the generated HTML code via the "origin" query parameter, leading to a cross-site scripting (XSS) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3656
- https://github.com/keycloak/keycloak/commit/63b41e2548cbc20bd3758e34a82d880e177bf24c
- https://access.redhat.com/security/cve/cve-2014-3656
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2014-3656
- https://issues.jboss.org/browse/KEYCLOAK-703
- https://security.snyk.io/vuln/SNYK-JAVA-ORGKEYCLOAK-31231
