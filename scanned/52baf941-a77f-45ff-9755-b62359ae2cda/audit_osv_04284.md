# [M] BIT-codeigniter-2022-39284

## Summary
Severity: Medium
Advisory: BIT-codeigniter-2022-39284
Aliases: CVE-2022-39284, GHSA-745p-r637-7vvp
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-codeigniter-2022-39284
Type: osv

## Affected
- Bitnami: `codeigniter` — affected >=4.0.0 <4.2.7

## Details
CodeIgniter is a PHP full-stack web framework. In versions prior to 4.2.7 setting `$secure` or `$httponly` value to `true` in `Config\Cookie` is not reflected in `set_cookie()` or `Response::setCookie()`. As a result cookie values are erroneously exposed to scripts. It should be noted that this vulnerability does not affect session cookies. Users are advised to upgrade to v4.2.7 or later. Users unable to upgrade are advised to manually construct their cookies either by setting the options in code or by constructing Cookie objects. Examples of each workaround are available in the linked GHSA.

## References
- https://codeigniter4.github.io/userguide/helpers/cookie_helper.html#set_cookie
- https://codeigniter4.github.io/userguide/outgoing/response.html#CodeIgniter%5CHTTP%5CResponse::setCookie
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies#restrict_access_to_cookies
- https://github.com/codeigniter4/CodeIgniter4/issues/6540
- https://github.com/codeigniter4/CodeIgniter4/pull/6544
- https://github.com/codeigniter4/CodeIgniter4/security/advisories/GHSA-745p-r637-7vvp
