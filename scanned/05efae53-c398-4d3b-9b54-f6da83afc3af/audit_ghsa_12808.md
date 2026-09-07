# [M] Nuxeo vulnerable to Reflected Cross-Site Scripting leading to Remote Code Execution

## Summary
Severity: Medium
Advisory: GHSA-x347-fc9w-w7c3
CVE: CVE-2021-32828
CWE: CWE-502, CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-01-06
Source: https://github.com/advisories/GHSA-x347-fc9w-w7c3
Type: github-advisory

## Affected
- Maven: `org.nuxeo.ecm.platform:nuxeo-platform-oauth` — affected >=0

## Details
The Nuxeo Platform is an open source content management platform for building business applications. In version 11.5.109, the `oauth2` REST API is vulnerable to Reflected Cross-Site Scripting (XSS). This XSS can be escalated to Remote Code Execution (RCE) by levering the automation API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32828
- https://github.com/nuxeo/nuxeo
- https://github.com/nuxeo/nuxeo/blob/master/modules/platform/nuxeo-platform-oauth/src/main/java/org/nuxeo/ecm/webengine/oauth2/OAuth2Callback.java
- https://securitylab.github.com/advisories/GHSL-2021-072-nuxeo
