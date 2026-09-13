# [M] CVE-2016-9285

## Summary
Severity: Medium
Advisory: CVE-2016-9285
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2016-11-11
Source: https://osv.dev/vulnerability/CVE-2016-9285
Type: osv

## Details
framework/modules/addressbook/controllers/addressController.php in Exponent CMS v2.4.0 allows remote attackers to read user information via a modified id number, as demonstrated by address/edit/id/1, related to an "addresses, countries, and regions" issue.

## References
- http://www.securitytracker.com/id/1037281
- http://www.securityfocus.com/bid/94296
- https://github.com/exponentcms/exponent-cms/commit/9eeed1e82fb9e6d0d41e7dd10672df48045a9b59
