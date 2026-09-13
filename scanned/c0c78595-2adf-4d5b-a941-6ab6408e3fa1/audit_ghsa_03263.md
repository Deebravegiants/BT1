# [C] Autobinding vulnerability in MITREid Connect

## Summary
Severity: Critical
Advisory: GHSA-8p36-q63g-68qh
CVE: CVE-2021-27582
CWE: CWE-1321, CWE-915
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-05-13
Source: https://github.com/advisories/GHSA-8p36-q63g-68qh
Type: github-advisory

## Affected
- Maven: `org.mitre:openid-connect-parent` — affected >=0

## Details
org/mitre/oauth2/web/OAuthConfirmationController.java in the OpenID Connect server implementation for MITREid Connect through 1.3.3 contains a Mass Assignment (aka Autobinding) vulnerability. This arises due to unsafe usage of the @ModelAttribute annotation during the OAuth authorization flow, in which HTTP request parameters affect an authorizationRequest.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27582
- https://github.com/mitreid-connect/OpenID-Connect-Java-Spring-Server/commit/7eba3c12fed82388f917e8dd9b73e86e3a311e4c
- https://github.com/mitreid-connect/OpenID-Connect-Java-Spring-Server
- https://portswigger.net/research/hidden-oauth-attack-vectors
- http://agrrrdog.blogspot.com/2017/03/autobinding-vulns-and-spring-mvc.html
