# [H] Shopware Storefront Reflected XSS in Storefront Login Page

## Summary
Severity: High
Advisory: GHSA-6w82-v552-wjw2
CVE: CVE-2025-67648
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2025-12-09
Source: https://github.com/advisories/GHSA-6w82-v552-wjw2
Type: github-advisory

## Affected
- Packagist: `shopware/shopware` — affected >=6.4.6.0 <6.6.10.10
- Packagist: `shopware/storefront` — affected >=6.4.6.0 <6.6.10.10
- Packagist: `shopware/shopware` — affected >=6.7.0.0 <6.7.5.1
- Packagist: `shopware/storefront` — affected >=6.7.0.0 <6.7.5.1

## Details
### Impact

By exploiting the XSS vulnerabilities, malicious actors can perform harmful actions in the user's web browser in the session context of the affected user. Some examples of this include, but are not limited to: Obtaining user session tokens. Performing administrative actions (when an administrative user is affected). These vulnerabilities pose a high security risk. Since a sensitive cookie is not configured with the HttpOnly attribute and administrator JWTs are stored in sessionStorage, any successful XSS attack could enable the theft of session cookies and administrative tokens.

### Description

A request parameter from the URL of the login page is directly rendered within the Twig template of the Storefront login page without further processing or input validation. This allows direct code injection into the template via the URL parameter. An attacker can create malicious links that could be used in a phishing attack. The parameter `waitTime` lacks proper input validation.

The attack can be tested with the following URL pattern:

```
/account/login?loginError=1&waitTime=<a%20href%3D"https%3A%2F%2Fde.wikipedia.org%2Fwiki%2FPhishing">Here<%2Fa>
```

The same applies to the `errorSnippet` parameter:

```
/account/login?loginError=1&errorSnippet=Reset%20your%20password%20%3Ca%20href%3D%22https%3A%2F%2Fde.wikipedia.org%2Fwiki%2FPhishing%22%3Ehere%3C%2Fa%3E.
```

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-6w82-v552-wjw2
- https://nvd.nist.gov/vuln/detail/CVE-2025-67648
- https://github.com/shopware/shopware/commit/c9242c02c84595d9fa3e2adf6a264bc90a657b58
- https://github.com/shopware/shopware
