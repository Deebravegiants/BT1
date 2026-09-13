# [M] PHPMailer Local file inclusion

## Summary
Severity: Medium
Advisory: GHSA-8jc3-5p29-qgjx
CVE: CVE-2006-5734
Ecosystem: Packagist
Published: 2024-02-02
Source: https://github.com/advisories/GHSA-8jc3-5p29-qgjx
Type: github-advisory

## Affected
- Packagist: `phpmailer/phpmailer` — affected >=0 <5.2.0

## Details
### Impact
Arbitrary local file inclusion via the `$lang` property, remotely exploitable if host application passes unfiltered user data into that property. The 3 CVEs listed are applications that used PHPMailer that were vulnerable to this problem.

### Patches
It's not known exactly when this was fixed in the host applications, but it was fixed in PHPMailer 5.2.0.

### Workarounds
Filter and validate user-supplied data before use.

### References
https://nvd.nist.gov/vuln/detail/CVE-2006-5734
https://nvd.nist.gov/vuln/detail/CVE-2007-3215
https://nvd.nist.gov/vuln/detail/CVE-2007-2021
Example exploit: https://www.exploit-db.com/exploits/14893

### For more information
If you have any questions or comments about this advisory:
* Open a private issue in [the PHPMailer project](https://github.com/PHPMailer/PHPMailer)

## References
- https://github.com/PHPMailer/PHPMailer/security/advisories/GHSA-8jc3-5p29-qgjx
- https://github.com/PHPMailer/PHPMailer
