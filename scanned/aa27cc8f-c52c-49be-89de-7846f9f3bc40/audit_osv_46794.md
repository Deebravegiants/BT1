# [H] CVE-2015-3200

## Summary
Severity: High
Advisory: CVE-2015-3200
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2015-06-09
Source: https://osv.dev/vulnerability/CVE-2015-3200
Type: osv

## Details
mod_auth in lighttpd before 1.4.36 allows remote attackers to inject arbitrary log entries via a basic HTTP authentication string without a colon character, as demonstrated by a string containing a NULL and new line character.

## References
- http://jaanuskp.blogspot.com/2015/05/cve-2015-3200.html
- http://redmine.lighttpd.net/issues/2646
- http://www.oracle.com/technetwork/topics/security/bulletinoct2015-2511968.html
- http://www.securitytracker.com/id/1032405
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05247375
- http://jaanuskp.blogspot.com/2015/05/cve-2015-3200.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-August/163223.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-August/163286.html
- http://www.securityfocus.com/bid/74813
- https://kc.mcafee.com/corporate/index?page=content&id=SB10310
