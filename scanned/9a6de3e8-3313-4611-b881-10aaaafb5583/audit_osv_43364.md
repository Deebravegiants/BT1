# [H] phpList < 3.7.0-RC5 Cross-Site Request Forgery via admins.php

## Summary
Severity: High
Advisory: CVE-2026-73482
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73482
Type: osv

## Details
phpList before 3.7.0-RC5 contains a cross-site request forgery (CSRF) vulnerability in lists/admin/admins.php. The administrator deletion action is triggered via an unauthenticated GET request (?page=admins&delete=N) that is not protected by a CSRF token (the central verifyCsrfGetToken check uses enforce=false and is bypassed when the token parameter is absent). A remote attacker can trick a logged-in super-administrator into loading a crafted URL (e.g., embedded as an image in an email) to delete any non-self administrator account.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73482.json
- https://github.com/phpList/phplist3/releases/tag/v3.7.0-RC5
- https://nvd.nist.gov/vuln/detail/CVE-2026-73482
- https://www.vulncheck.com/advisories/phplist-rc5-cross-site-request-forgery-via-admins-php
- https://github.com/phpList/phplist3/issues/1117
- https://github.com/phpList/phplist3/commit/5159c3ed33a5674a8169472b50d146d97f630746
- https://github.com/phpList/phplist3/pull/1121
- https://github.com/phpList/phplist3
