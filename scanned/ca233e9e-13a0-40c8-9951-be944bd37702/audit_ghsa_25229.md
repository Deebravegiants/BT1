# [M] Silverstripe CMS Arbitrary Code Execution

## Summary
Severity: Medium
Advisory: GHSA-gv6c-59h4-9pmg
CVE: CVE-2011-4962
CWE: CWE-20, CWE-502
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-gv6c-59h4-9pmg
Type: github-advisory

## Affected
- Packagist: `silverstripe/cms` — affected >=2.4.0 <2.4.6

## Details
`code/sitefeatures/PageCommentInterface.php` in SilverStripe 2.4.x before 2.4.6 might allow remote attackers to execute arbitrary code via a crafted cookie in a user comment submission, which is not properly handled when it is deserialized.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4962
- https://github.com/silverstripe/silverstripe-cms/commit/d15e8509b01ff2dbbe3028a055021a29b1065b22
- https://github.com/silverstripe/silverstripe-cms
- https://web.archive.org/web/20120621234353/http://doc.silverstripe.org/framework/en/trunk/changelogs/2.4.6
- http://www.openwall.com/lists/oss-security/2012/04/30/1
- http://www.openwall.com/lists/oss-security/2012/04/30/3
