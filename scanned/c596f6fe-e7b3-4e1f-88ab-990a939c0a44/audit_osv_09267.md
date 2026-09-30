# [M] CVE-2016-9286

## Summary
Severity: Medium
Advisory: CVE-2016-9286
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2016-11-11
Source: https://osv.dev/vulnerability/CVE-2016-9286
Type: osv

## Details
framework/modules/users/controllers/usersController.php in Exponent CMS v2.4.0patch1 does not properly restrict access to user records, which allows remote attackers to read address information, as demonstrated by an address/show/id/1 URI.

## References
- http://www.securitytracker.com/id/1037281
- http://www.securityfocus.com/bid/94296
- https://github.com/exponentcms/exponent-cms/commit/e38aae66c785f08f3907aa121378caf71ca5f2d7
