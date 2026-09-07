# [M] Koajs vulnerable to Cross-Site Scripting (XSS) at ctx.redirect() function

## Summary
Severity: Medium
Advisory: GHSA-x2rg-q646-7m2v
CVE: CVE-2025-32379
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-04-09
Source: https://github.com/advisories/GHSA-x2rg-q646-7m2v
Type: github-advisory

## Affected
- npm: `koa` — affected >=0 <2.16.1
- npm: `koa` — affected >=3.0.0-alpha.1 <3.0.0-alpha.5

## Details
### Summary
In koa < 2.16.1 and < 3.0.0-alpha.5, passing untrusted user input to ctx.redirect() even after sanitizing it, may execute javascript code on the user who use the app.

### Patches
This issue is patched in  2.16.1 and 3.0.0-alpha.5.

### PoC
Coming soon...

### Impact
1. Redirect user to another phishing site
2. Make request to another endpoint of the application based on user's cookie
3. Steal user's cookie

## References
- https://github.com/koajs/koa/security/advisories/GHSA-x2rg-q646-7m2v
- https://nvd.nist.gov/vuln/detail/CVE-2025-32379
- https://github.com/koajs/koa/commit/ff25eb4a7f2392df46481fe86355161067687312
- https://github.com/koajs/koa
