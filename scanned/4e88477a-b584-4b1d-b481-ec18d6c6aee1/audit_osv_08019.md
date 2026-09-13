# [C] CVE-2016-10033

## Summary
Severity: Critical
Advisory: CVE-2016-10033
Aliases: GHSA-5f37-gxvh-23v6
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-30
Source: https://osv.dev/vulnerability/CVE-2016-10033
Type: osv

## Details
The mailSend function in the isMail transport in PHPMailer before 5.2.18 might allow remote attackers to pass extra parameters to the mail command and consequently execute arbitrary code via a \" (backslash double quote) in a crafted Sender property.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2016-10033
- http://www.securityfocus.com/archive/1/539963/100/0/threaded
- http://www.securitytracker.com/id/1037533
- https://developer.joomla.org/security-centre/668-20161205-phpmailer-security-advisory.html
- https://www.drupal.org/psa-2016-004
- http://seclists.org/fulldisclosure/2016/Dec/78
- https://github.com/PHPMailer/PHPMailer/releases/tag/v5.2.18
- https://github.com/PHPMailer/PHPMailer/wiki/About-the-CVE-2016-10033-and-CVE-2016-10045-vulnerabilities
- https://legalhackers.com/advisories/PHPMailer-Exploit-Remote-Code-Exec-CVE-2016-10033-Vuln.html
- https://www.exploit-db.com/exploits/40968/
- https://www.exploit-db.com/exploits/40970/
- http://packetstormsecurity.com/files/140291/PHPMailer-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/140350/PHPMailer-Sendmail-Argument-Injection.html
- http://www.rapid7.com/db/modules/exploit/multi/http/phpmailer_arg_injection
- http://www.securityfocus.com/bid/95108
- https://www.exploit-db.com/exploits/40969/
- https://www.exploit-db.com/exploits/40974/
- https://www.exploit-db.com/exploits/40986/
- https://www.exploit-db.com/exploits/41962/
- https://www.exploit-db.com/exploits/41996/
