# [M] Silverstripe XSS in Director::force_redirect()

## Summary
Severity: Medium
Advisory: GHSA-jqp8-v74p-g8px
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-jqp8-v74p-g8px
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.1.0 <3.1.12

## Details
A low level XSS vulnerability has been found in the Framework affecting http redirection via the Director::force_redirect method.

Attempts to redirect to a url may generate HTML which is not safely escaped, and may pose a risk of XSS in some environments.

This vulnerability is marked low as it is difficult to exploit, as any injected HTML will only be returned from the server if the Location HTTP header is also sent, meaning that any user browsing the site would not be exposed to the body of the response before their browser redirects them.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/ee9bddb808df6d27db4d56bb5d522dcfe6788715
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2015-010-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/software/download/security-releases/ss-2015-010-xss-in-directorforce-redirect
