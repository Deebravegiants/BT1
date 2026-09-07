# [M] @dapperduckling/keycloak-connector-server has Reflected XSS Vulnerability in Authentication Flow URL Handling

## Summary
Severity: Medium
Advisory: GHSA-w5rq-g9r6-vrcg
CVE: CVE-2024-53843
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-11-26
Source: https://github.com/advisories/GHSA-w5rq-g9r6-vrcg
Type: github-advisory

## Affected
- npm: `@dapperduckling/keycloak-connector-server` — affected >=0 <2.5.5

## Details
**Impact**
A Reflected Cross-Site Scripting (XSS) vulnerability was discovered in the authentication flow of the application. This issue arises due to improper sanitization of the URL parameters, allowing the URL bar's contents to be injected and reflected into the HTML page. An attacker could craft a malicious URL to execute arbitrary JavaScript in the browser of a victim who visits the link.

**Who is impacted?**
Any application utilizing this authentication library is vulnerable. Users of the application are at risk if they can be lured into clicking on a crafted malicious link.

**Patches**
The vulnerability has been patched in **2.5.5** by ensuring proper sanitization and escaping of user input in the affected URL parameters.

Users are strongly encouraged to upgrade to the following versions:

**Workarounds**
If upgrading is not immediately possible, users can implement the following workarounds:
- Employ a Web Application Firewall (WAF) to block malicious requests containing suspicious URL parameters.
- Apply input validation and escaping directly within the application’s middleware or reverse proxy layer, specifically targeting the affected parameters.

**References**
- OWASP Cross-Site Scripting (XSS) Cheat Sheet: https://owasp.org/www-community/attacks/xss/

## References
- https://github.com/DapperDuckling/keycloak-connector/security/advisories/GHSA-w5rq-g9r6-vrcg
- https://nvd.nist.gov/vuln/detail/CVE-2024-53843
- https://github.com/DapperDuckling/keycloak-connector
