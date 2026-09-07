# [H] ghtml Cross-Site Scripting (XSS) vulnerability

## Summary
Severity: High
Advisory: GHSA-vvhj-v88f-5gxr
CVE: CVE-2024-37166
CWE: CWE-79, CWE-80
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2024-06-10
Source: https://github.com/advisories/GHSA-vvhj-v88f-5gxr
Type: github-advisory

## Affected
- npm: `ghtml` — affected >=0 <2.0.0

## Details
## Summary

It is possible to introduce user-controlled JavaScript code and trigger a Cross-Site Scripting (XSS) vulnerability in some cases.

## Actions Taken

- Updated the documentation to clarify that while `ghtml` escapes characters with special meaning in HTML, it does not provide comprehensive protection against all types of XSS attacks in every scenario. **_This aligns with the approach taken by other template engines. Developers should be cautious and take additional measures to sanitize user input and prevent potential vulnerabilities._** More reading: https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- The backtick character (`) is now also escaped to prevent the creation of strings in most cases where a malicious actor somehow gains the ability to write JavaScript. This does not provide comprehensive protection either.

## References
- https://github.com/gurgunday/ghtml/security/advisories/GHSA-vvhj-v88f-5gxr
- https://nvd.nist.gov/vuln/detail/CVE-2024-37166
- https://github.com/gurgunday/ghtml/commit/df1ea50fe8968a766fd2b9379a8f9806375227f8
- https://github.com/gurgunday/ghtml
