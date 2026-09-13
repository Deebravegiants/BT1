# [H] PHPMailer vulnerable to email header injection

## Summary
Severity: High
Advisory: GHSA-398j-f7m7-795j
CVE: CVE-2012-0796
CWE: CWE-94
Ecosystem: Packagist
Published: 2022-10-06
Source: https://github.com/advisories/GHSA-398j-f7m7-795j
Type: github-advisory

## Affected
- Packagist: `phpmailer/phpmailer` — affected >=0 <2.2.1

## Details
### Impact
Arbitrary additional email headers can be injected via crafted From or Sender headers.

### Patches
Fixed in 2.2.1

### Workarounds
Filter user-supplied values prior to using them in From or Sender properties.

### References
https://nvd.nist.gov/vuln/detail/CVE-2012-0796

### For more information
If you have any questions or comments about this advisory:
* Open a private issue in [the PHPMailer project](https://github.com/PHPMailer/PHPMailer)

## References
- https://github.com/PHPMailer/PHPMailer/security/advisories/GHSA-398j-f7m7-795j
- https://nvd.nist.gov/vuln/detail/CVE-2012-0796
- https://bugzilla.redhat.com/show_bug.cgi?id=783532
- https://git.moodle.org/gw?p=moodle.git&a=commit&h=62988bf0bbc73df655f51884aaf1f523928abff9
- https://github.com/PHPMailer/PHPMailer
- http://moodle.org/mod/forum/discuss.php?d=194015
- http://www.debian.org/security/2012/dsa-2421
