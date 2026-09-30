# [C] Remote code execution in PHPMailer

## Summary
Severity: Critical
Advisory: GHSA-4pc3-96mx-wwc8
CVE: CVE-2016-10045
CWE: CWE-77
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-03-05
Source: https://github.com/advisories/GHSA-4pc3-96mx-wwc8
Type: github-advisory

## Affected
- Packagist: `phpmailer/phpmailer` — affected >=5.0.0 <5.2.20

## Details
### Impact
The `isMail` transport in PHPMailer before 5.2.20 might allow remote attackers to pass extra parameters to the `mail` command and consequently execute arbitrary code by leveraging improper interaction between the `escapeshellarg` function and internal escaping performed in the mail function in PHP. NOTE: this vulnerability exists because of an incorrect fix for CVE-2016-10033.

This issue really emphasises that it&#39;s worth avoiding the built-in PHP `mail()` function entirely.

### Patches
Fixed in 5.2.20

### Workarounds
Send via SMTP to localhost instead of calling the `mail()` function.

### References
https://nvd.nist.gov/vuln/detail/CVE-2016-10045
See also https://nvd.nist.gov/vuln/detail/CVE-2016-10033

### For more information
If you have any questions or comments about this advisory:
* Open a private issue in [the PHPMailer project](https://github.com/PHPMailer/PHPMailer)

## References
- https://github.com/PHPMailer/PHPMailer/security/advisories/GHSA-4pc3-96mx-wwc8
- https://nvd.nist.gov/vuln/detail/CVE-2016-10045
- https://developer.joomla.org/security-centre/668-20161205-phpmailer-security-advisory.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/phpmailer/phpmailer/CVE-2016-10045.yaml
- https://github.com/PHPMailer/PHPMailer
- https://github.com/PHPMailer/PHPMailer/releases/tag/v5.2.20
- https://github.com/PHPMailer/PHPMailer/wiki/About-the-CVE-2016-10033-and-CVE-2016-10045-vulnerabilities
- https://legalhackers.com/advisories/PHPMailer-Exploit-Remote-Code-Exec-CVE-2016-10045-Vuln-Patch-Bypass.html
- https://www.exploit-db.com/exploits/40969
- https://www.exploit-db.com/exploits/40986
- https://www.exploit-db.com/exploits/42221
- http://openwall.com/lists/oss-security/2016/12/28/1
- http://packetstormsecurity.com/files/140286/PHPMailer-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/140350/PHPMailer-Sendmail-Argument-Injection.html
- http://seclists.org/fulldisclosure/2016/Dec/81
- http://www.rapid7.com/db/modules/exploit/multi/http/phpmailer_arg_injection
