# [M] Moderate severity vulnerability that affects org.apache.juddi:juddi-client

## Summary
Severity: Medium
Advisory: GHSA-49h4-g8p5-jgq6
CVE: CVE-2015-5241
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-49h4-g8p5-jgq6
Type: github-advisory

## Affected
- Maven: `org.apache.juddi:juddi-client` — affected >=3.1.2 <3.2.0

## Details
After logging into the portal, the logout jsp page redirects the browser back to the login page after. It is feasible for malicious users to redirect the browser to an unintended web page in Apache jUDDI 3.1.2, 3.1.3, 3.1.4, and 3.1.5 when utilizing the portlets based user interface also known as 'Pluto', 'jUDDI Portal', 'UDDI Portal' or 'uddi-console'. User session data, credentials, and auth tokens are cleared before the redirect.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5241
- https://github.com/advisories/GHSA-49h4-g8p5-jgq6
- http://juddi.apache.org/security.html
