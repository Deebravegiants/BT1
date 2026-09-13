# [H] CVE-2017-8114

## Summary
Severity: High
Advisory: CVE-2017-8114
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-29
Source: https://osv.dev/vulnerability/CVE-2017-8114
Type: osv

## Details
Roundcube Webmail allows arbitrary password resets by authenticated users. This affects versions before 1.0.11, 1.1.x before 1.1.9, and 1.2.x before 1.2.5. The problem is caused by an improperly restricted exec call in the virtualmin and sasl drivers of the password plugin.

## References
- http://www.securityfocus.com/bid/98445
- https://roundcube.net/news/2017/04/28/security-updates-1.2.5-1.1.9-and-1.0.11
- https://security.gentoo.org/glsa/201707-11
- https://github.com/ilsani/rd/tree/master/security-advisories/web/roundcube/cve-2017-8114
