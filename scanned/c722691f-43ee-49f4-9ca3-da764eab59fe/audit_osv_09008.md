# [C] CVE-2016-7400

## Summary
Severity: Critical
Advisory: CVE-2016-7400
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-07
Source: https://osv.dev/vulnerability/CVE-2016-7400
Type: osv

## Details
Multiple SQL injection vulnerabilities in Exponent CMS before 2.4.0 allow remote attackers to execute arbitrary SQL commands via the (1) id parameter in an activate_address address controller action, (2) title parameter in a show blog controller action, or (3) content_id parameter in a showComments expComment controller action.

## References
- https://github.com/exponentcms/exponent-cms/releases/tag/v2.4.0
- https://www.exploit-db.com/exploits/40412/
- http://www.openwall.com/lists/oss-security/2016/09/18/10
- http://www.openwall.com/lists/oss-security/2016/09/18/2
- http://www.securityfocus.com/bid/93041
- https://exponentcms.lighthouseapp.com/projects/61783/changesets/e916702a91a6342bbab483a2be2ba2f11dca3aa3
- https://github.com/exponentcms/exponent-cms/commit/e916702a91a6342bbab483a2be2ba2f11dca3aa3
