# [H] CVE-2016-7999

## Summary
Severity: High
Advisory: CVE-2016-7999
CVSS: 7.4 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:N)
Published: 2017-01-18
Source: https://osv.dev/vulnerability/CVE-2016-7999
Type: osv

## Details
ecrire/exec/valider_xml.php in SPIP 3.1.2 and earlier allows remote attackers to conduct server side request forgery (SSRF) attacks via a URL in the var_url parameter in a valider_xml action.

## References
- https://sysdream.com/news/lab/2016-10-19-spip-3-1-2-server-side-request-forgery-cve-2016-7999/
- http://www.openwall.com/lists/oss-security/2016/10/12/10
- http://www.securityfocus.com/bid/93451
- http://www.openwall.com/lists/oss-security/2016/10/05/17
- http://www.openwall.com/lists/oss-security/2016/10/08/6
- https://core.spip.net/projects/spip/repository/revisions/23188
- https://core.spip.net/projects/spip/repository/revisions/23193
- http://www.openwall.com/lists/oss-security/2016/10/07/5
