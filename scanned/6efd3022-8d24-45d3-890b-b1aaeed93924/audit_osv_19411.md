# [H] CVE-2021-21247

## Summary
Severity: High
Advisory: CVE-2021-21247
Aliases: GHSA-6pxf-75cf-vwjp
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-15
Source: https://osv.dev/vulnerability/CVE-2021-21247
Type: osv

## Details
OneDev is an all-in-one devops platform. In OneDev before version 4.0.3, the application's BasePage registers an AJAX event listener (`AbstractPostAjaxBehavior`) in all pages other than the login page. This listener decodes and deserializes the `data` query parameter. We can access this listener by submitting a POST request to any page. This issue may lead to `post-auth RCE` This endpoint is subject to authentication and, therefore, requires a valid user to carry on the attack. This issue was addressed in 4.0.3 by encrypting serialization payload with secrets only known to server.

## References
- https://github.com/theonedev/onedev/security/advisories/GHSA-6pxf-75cf-vwjp
