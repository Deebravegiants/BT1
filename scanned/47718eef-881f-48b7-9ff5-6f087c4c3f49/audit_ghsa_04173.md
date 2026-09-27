# [M] Spring Web Flow JS RemotingHandler renders non-HTML Response as HTML

## Summary
Severity: Medium
Advisory: GHSA-hw5c-xm3c-v96w
CVE: CVE-2026-40986
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-hw5c-xm3c-v96w
Type: github-advisory

## Affected
- Maven: `org.springframework.webflow:spring-webflow` — affected >=4.0.0 <4.0.1
- Maven: `org.springframework.webflow:spring-webflow` — affected >=3.0.0 <3.0.2
- Maven: `org.springframework.webflow:spring-webflow` — affected >=0

## Details
Spring Web Flow's JavaScript RemotingHandler renders the body of an error response as HTML even when the response is not "text/html", which can result in a scripting attack in the user's browser if the error response from the server contains error details with input reflected from an attacker.

Affected versions:
Spring Web Flow 4.0.0; 3.0.0 through 3.0.1; 2.5.0 through 2.5.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40986
- https://github.com/spring-projects/spring-webflow
- https://spring.io/security/cve-2026-40986
