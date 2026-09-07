# [M] Cross-site scripting in PHPMailer

## Summary
Severity: Medium
Advisory: GHSA-58mj-pw57-4vm2
CVE: CVE-2017-11503
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-03-05
Source: https://github.com/advisories/GHSA-58mj-pw57-4vm2
Type: github-advisory

## Affected
- Packagist: `phpmailer/phpmailer` — affected >=5.0.0 <5.2.24

## Details
PHPMailer versions prior to 5.2.24 (released July 26th 2017) have an XSS vulnerability in one of the code examples, CVE-2017-11503. The code_generator.phps example did not filter user input prior to output. This file is distributed with a `.phps` extension, so it it not normally executable unless it is explicitly renamed, and the file is not included when PHPMailer is loaded through composer, so it is safe by default. There was also an undisclosed potential XSS vulnerability in the default exception handler (unused by default). Patches for both issues kindly provided by Patrick Monnerat of the Fedora Project.

### Impact
PHPMailer 5.2.23 has XSS in the &quot;From Email Address&quot; and &quot;To Email Address&quot; fields of code_generator.php.

### Patches
Fixed in 5.2.24

### Workarounds
None.

### References
https://nvd.nist.gov/vuln/detail/CVE-2017-11503

### For more information
If you have any questions or comments about this advisory:
* Open a private issue in [the PHPMailer project](https://github.com/PHPMailer/PHPMailer)

## References
- https://github.com/PHPMailer/PHPMailer/security/advisories/GHSA-58mj-pw57-4vm2
- https://nvd.nist.gov/vuln/detail/CVE-2017-11503
- https://cxsecurity.com/issue/WLB-2017060181
- https://github.com/FriendsOfPHP/security-advisories/blob/master/phpmailer/phpmailer/CVE-2017-11503.yaml
- https://github.com/PHPMailer/PHPMailer/releases/tag/v5.2.24
- https://packetstormsecurity.com/files/143138/phpmailer-xss.txt
- http://www.securityfocus.com/bid/99293
- http://www.securitytracker.com/id/1039026
