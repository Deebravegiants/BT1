# [C] CVE-2016-7565

## Summary
Severity: Critical
Advisory: CVE-2016-7565
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-13
Source: https://osv.dev/vulnerability/CVE-2016-7565
Type: osv

## Details
install/index.php in Exponent CMS 2.3.9 allows remote attackers to execute arbitrary commands via shell metacharacters in the sc array parameter.

## References
- https://github.com/exponentcms/exponent-cms/releases/tag/v2.4.0
- http://www.openwall.com/lists/oss-security/2016/09/22/6
- https://exponentcms.lighthouseapp.com/projects/61783/changesets/4ae457ff1bf80e8b61286cd125ca794b25564e86
- https://github.com/exponentcms/exponent-cms/commit/4ae457ff1bf80e8b61286cd125ca794b25564e86
