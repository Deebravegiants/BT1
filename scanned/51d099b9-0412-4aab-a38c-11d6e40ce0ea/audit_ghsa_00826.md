# [M] CSRF Vulnerability in polaris-website

## Summary
Severity: Medium
Advisory: GHSA-whrh-9j4q-g7ph
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2020-08-05
Source: https://github.com/advisories/GHSA-whrh-9j4q-g7ph
Type: github-advisory

## Affected
- npm: `polaris-website` — affected >=0 <1.1.1

## Details
### Impact
CSRF vulnerability:
In some very specific circumstances, an attacker would be able to update your settings.
Basically you would need to navigate to hackersite.com while logged into our panel. Then they could modify your settings. They couldn't check if it worked, nor could they read your settings.

### Patches
As of v1.1.1 this has been patched by implementing the Double submit pattern using a cookie.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Polaris-React](https://github.com/polaris-rbx/polaris-react)
* Email us at [hi@nezto.re](mailto:hi@nezto.re)
* Join our discord (preferred): https://discord.gg/QevWabU

## References
- https://github.com/polaris-rbx/Polaris-React/security/advisories/GHSA-whrh-9j4q-g7ph
- https://github.com/polaris-rbx/Polaris-React/commit/b64673d91e83c0737616a0770d8208727730808b
- https://github.com/polaris-rbx/Polaris-React
- https://medium.com/cross-site-request-forgery-csrf/double-submit-cookie-pattern-65bb71d80d9f
- https://owasp.org/www-community/attacks/csrf
- https://snyk.io/vuln/SNYK-JS-POLARISWEBSITE-597473
- https://www.barracuda.com/glossary/csrf
