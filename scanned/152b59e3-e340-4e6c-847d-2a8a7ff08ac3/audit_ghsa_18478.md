# [H] NodeJS version of HAX CMS Has Disabled Content Security Policy That Enables Cross-Site Scripting

## Summary
Severity: High
Advisory: GHSA-59g8-h59f-8hjp
CVE: CVE-2025-54128
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:L/VA:H/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-07-21
Source: https://github.com/advisories/GHSA-59g8-h59f-8hjp
Type: github-advisory

## Affected
- npm: `@haxtheweb/haxcms-nodejs` — affected >=0 <11.0.8

## Details
### Summary
The NodeJS version of HAX CMS has a disabled Content Security Policy (CSP). This configuration is insecure for a production application because it does not protect against cross-site-scripting attacks.

### Details
The `contentSecurityPolicy` value is explicitly disabled in the application's Helmet configuration in `app.js`.

![permissive-csp-code](https://github.com/user-attachments/assets/8ec6c63c-9f9f-413e-be7e-ed14913da91c)

#### Affected Resources
- [app.js:52](https://github.com/haxtheweb/haxcms-nodejs/blob/b1f95880b42fea6ed07855b5804b29b182ec5e07/src/app.js#L52)

### PoC
To reproduce this vulnerability, [install](https://github.com/haxtheweb/haxcms-nodejs) HAX CMS NodeJS. The application will load without a CSP configured.

### Impact
In conjunction with an XSS vulnerability, an attacker could execute arbitrary scripts and exfiltrate data, including session tokens and sensitive local data.

#### Additional Information
- [OWASP: Content Security Policy](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)

## References
- https://github.com/haxtheweb/issues/security/advisories/GHSA-59g8-h59f-8hjp
- https://nvd.nist.gov/vuln/detail/CVE-2025-54128
- https://github.com/haxtheweb/haxcms-nodejs/commit/ddb9351c6d6418008d4084a5b17fd6d611bc4e30
- https://github.com/haxtheweb/haxcms-nodejs
