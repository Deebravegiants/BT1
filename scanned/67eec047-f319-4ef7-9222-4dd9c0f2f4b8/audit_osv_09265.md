# [M] CVE-2016-9284

## Summary
Severity: Medium
Advisory: CVE-2016-9284
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2016-11-11
Source: https://osv.dev/vulnerability/CVE-2016-9284
Type: osv

## Details
getUsersByJSON in framework/modules/users/controllers/usersController.php in Exponent CMS v2.4.0 allows remote attackers to read user information via users/getUsersByJSON/sort/ and a trailing string.

## References
- http://www.securitytracker.com/id/1037281
- http://www.securityfocus.com/bid/94296
- https://github.com/exponentcms/exponent-cms/commit/e7b6856ac384bf2b8ea7761a1e46d6e4186d36f4
