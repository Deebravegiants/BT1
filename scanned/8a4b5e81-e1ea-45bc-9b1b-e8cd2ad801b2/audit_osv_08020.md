# [C] CVE-2016-10034

## Summary
Severity: Critical
Advisory: CVE-2016-10034
Aliases: GHSA-r9mw-gwx9-v3h5
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-30
Source: https://osv.dev/vulnerability/CVE-2016-10034
Type: osv

## Details
The setFrom function in the Sendmail adapter in the zend-mail component before 2.4.11, 2.5.x, 2.6.x, and 2.7.x before 2.7.2, and Zend Framework before 2.4.11 might allow remote attackers to pass extra parameters to the mail command and consequently execute arbitrary code via a \" (backslash double quote) in a crafted e-mail address.

## References
- http://www.securitytracker.com/id/1037539
- https://www.exploit-db.com/exploits/40979/
- https://www.exploit-db.com/exploits/40986/
- https://www.exploit-db.com/exploits/42221/
- http://www.securityfocus.com/bid/95144
- https://security.gentoo.org/glsa/201804-10
- https://framework.zend.com/security/advisory/ZF2016-04
- https://legalhackers.com/advisories/ZendFramework-Exploit-ZendMail-Remote-Code-Exec-CVE-2016-10034-Vuln.html
