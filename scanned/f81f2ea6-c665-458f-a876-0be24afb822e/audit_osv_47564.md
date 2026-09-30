# [H] CVE-2016-7998

## Summary
Severity: High
Advisory: CVE-2016-7998
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-18
Source: https://osv.dev/vulnerability/CVE-2016-7998
Type: osv

## Details
The SPIP template composer/compiler in SPIP 3.1.2 and earlier allows remote authenticated users to execute arbitrary PHP code by uploading an HTML file with a crafted (1) INCLUDE or (2) INCLURE tag and then accessing it with a valider_xml action.

## References
- https://sysdream.com/news/lab/2016-10-19-spip-3-1-2-template-compiler-composer-php-code-execution-cve-2016-7998/
- http://www.openwall.com/lists/oss-security/2016/10/05/17
- http://www.securityfocus.com/bid/93451
- https://core.spip.net/projects/spip/repository/revisions/23192
- http://www.openwall.com/lists/oss-security/2016/10/07/5
- http://www.openwall.com/lists/oss-security/2016/10/08/6
- https://core.spip.net/projects/spip/repository/revisions/23186
- https://core.spip.net/projects/spip/repository/revisions/23189
