# [H] PHPMailer Shell command injection

## Summary
Severity: High
Advisory: GHSA-6h78-85v2-mmch
CVE: CVE-2007-3215
Ecosystem: Packagist
Published: 2024-02-02
Source: https://github.com/advisories/GHSA-6h78-85v2-mmch
Type: github-advisory

## Affected
- Packagist: `phpmailer/phpmailer` — affected >=0 <1.7.4

## Details
PHPMailer before 1.7.4, when configured to use sendmail, allows remote attackers to execute arbitrary shell commands via shell metacharacters in the SendmailSend function in `class.phpmailer.php`.

### Impact
Shell command injection, remotely exploitable if host application does not filter user data appropriately.

### Patches
Fixed in 1.7.4

### Workarounds
Filter and validate user-supplied data before putting in the into the `Sender` property.

### References
https://nvd.nist.gov/vuln/detail/CVE-2007-3215

### For more information
If you have any questions or comments about this advisory:
* Open a private issue in [the PHPMailer project](https://github.com/PHPMailer/PHPMailer)

## References
- https://github.com/PHPMailer/PHPMailer/security/advisories/GHSA-6h78-85v2-mmch
- https://cxsecurity.com/issue/WLB-2007060063
- https://exchange.xforce.ibmcloud.com/vulnerabilities/34818
- https://github.com/PHPMailer/PHPMailer
- https://seclists.org/fulldisclosure/2011/Oct/223
- https://sourceforge.net/p/phpmailer/bugs/192
- https://web.archive.org/web/20070714054359/http://larholm.com/2007/06/11/phpmailer-0day-remote-execution
- https://yehg.net/lab/pr0js/advisories/%5BvTiger_5.2.1%5D_rce
