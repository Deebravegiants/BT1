# [C] CVE-2016-9287

## Summary
Severity: Critical
Advisory: CVE-2016-9287
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-11-15
Source: https://osv.dev/vulnerability/CVE-2016-9287
Type: osv

## Details
In /framework/modules/notfound/controllers/notfoundController.php of Exponent CMS 2.4.0 patch1, untrusted input is passed into getSearchResults. The method getSearchResults is defined in the search model with the parameter '$term' used directly in SQL. Impact is a SQL injection.

## References
- http://www.securityfocus.com/bid/94322
- https://github.com/exponentcms/exponent-cms/commit/4327ea96b3de89440693e06d03038121aa1fdcea
