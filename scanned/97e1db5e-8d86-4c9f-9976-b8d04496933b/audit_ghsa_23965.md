# [C] Swift Mailer mail transport Command Injection

## Summary
Severity: Critical
Advisory: GHSA-pr44-4jfr-286m
CVE: CVE-2016-10074
CWE: CWE-77
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-pr44-4jfr-286m
Type: github-advisory

## Affected
- Packagist: `swiftmailer/swiftmailer` — affected >=0 <5.4.5

## Details
The mail transport (aka Swift_Transport_MailTransport) in Swift Mailer before 5.4.5 might allow remote attackers to pass extra parameters to the mail command and consequently execute arbitrary code via a \" (backslash double quote) in a crafted e-mail address in the (1) From, (2) ReturnPath, or (3) Sender header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10074
- https://github.com/FriendsOfPHP/security-advisories/blob/master/swiftmailer/swiftmailer/CVE-2016-10074.yaml
- https://github.com/swiftmailer/swiftmailer/blob/5.x/CHANGES
- https://legalhackers.com/advisories/SwiftMailer-Exploit-Remote-Code-Exec-CVE-2016-10074-Vuln.html
- https://www.exploit-db.com/exploits/40972
- https://www.exploit-db.com/exploits/40986
- https://www.exploit-db.com/exploits/42221
- http://packetstormsecurity.com/files/140290/SwiftMailer-Remote-Code-Execution.html
- http://seclists.org/fulldisclosure/2016/Dec/86
- http://www.debian.org/security/2017/dsa-3769
- http://www.securityfocus.com/bid/95140
