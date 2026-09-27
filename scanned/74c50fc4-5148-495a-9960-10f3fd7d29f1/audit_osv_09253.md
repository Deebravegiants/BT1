# [H] CVE-2016-9242

## Summary
Severity: High
Advisory: CVE-2016-9242
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-11-07
Source: https://osv.dev/vulnerability/CVE-2016-9242
Type: osv

## Details
Multiple SQL injection vulnerabilities in the update method in framework/modules/core/controllers/expRatingController.php in Exponent CMS 2.4.0 allow remote authenticated users to execute arbitrary SQL commands via the (1) content_type or (2) subtype parameter.

## References
- http://www.securityfocus.com/bid/94194
- https://github.com/exponentcms/exponent-cms/commit/6172f67620ac13fc2f4e9d650c61937d48e9ecb9
