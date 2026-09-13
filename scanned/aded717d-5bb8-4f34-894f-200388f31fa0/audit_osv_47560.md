# [H] CVE-2016-7980

## Summary
Severity: High
Advisory: CVE-2016-7980
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-01-18
Source: https://osv.dev/vulnerability/CVE-2016-7980
Type: osv

## Details
Cross-site request forgery (CSRF) vulnerability in ecrire/exec/valider_xml.php in SPIP 3.1.2 and earlier allows remote attackers to hijack the authentication of administrators for requests that execute the XML validator on a local file via a crafted valider_xml request.  NOTE: this issue can be combined with CVE-2016-7998 to execute arbitrary PHP code.

## References
- https://sysdream.com/news/lab/2016-10-19-spip-3-1-2-exec-code-cross-site-request-forgery-cve-2016-7980/
- http://www.securityfocus.com/bid/93451
- http://www.openwall.com/lists/oss-security/2016/10/05/17
- http://www.openwall.com/lists/oss-security/2016/10/12/6
- http://www.openwall.com/lists/oss-security/2016/10/06/6
- https://core.spip.net/projects/spip/repository/revisions/23201
- https://core.spip.net/projects/spip/repository/revisions/23202
- https://core.spip.net/projects/spip/repository/revisions/23203
