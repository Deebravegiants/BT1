# [M] Local file disclosure in PHPMailer

## Summary
Severity: Medium
Advisory: GHSA-4x5h-cr29-fhp6
CVE: CVE-2017-5223
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-03-05
Source: https://github.com/advisories/GHSA-4x5h-cr29-fhp6
Type: github-advisory

## Affected
- Packagist: `phpmailer/phpmailer` — affected >=5.0.0 <5.2.22

## Details
An issue was discovered in PHPMailer before 5.2.22. PHPMailer&#39;s `msgHTML` method applies transformations to an HTML document to make it usable as an email message body. One of the transformations is to convert relative image URLs into attachments using a script-provided base directory. If no base directory is provided, it resolves to `/`, meaning that relative image URLs get treated as absolute local file paths and added as attachments. To form a remote vulnerability, the msgHTML method must be called, passed an unfiltered, user-supplied HTML document, and must not set a base directory.

### Impact
Arbitrary local files can be attached to email messages.

### Patches
Fixed in 5.2.22

### Workarounds
Validate input before using user-supplied file paths.

### References
https://nvd.nist.gov/vuln/detail/CVE-2017-5223

### For more information
If you have any questions or comments about this advisory:
* Open a private issue in [the PHPMailer project](https://github.com/PHPMailer/PHPMailer)

## References
- https://github.com/PHPMailer/PHPMailer/security/advisories/GHSA-4x5h-cr29-fhp6
- https://nvd.nist.gov/vuln/detail/CVE-2017-5223
- https://github.com/FriendsOfPHP/security-advisories/blob/master/phpmailer/phpmailer/CVE-2017-5223.yaml
- https://github.com/PHPMailer/PHPMailer/blob/master/SECURITY.md
- https://github.com/PHPMailer/PHPMailer/releases/tag/v5.2.22
- https://www.exploit-db.com/exploits/43056
- http://kalilinux.co/2017/01/12/phpmailer-cve-2017-5223-local-information-disclosure-vulnerability-analysis
- http://www.securityfocus.com/bid/95328
