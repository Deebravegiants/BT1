# [H] Phar object injection in PHPMailer

## Summary
Severity: High
Advisory: GHSA-7w4p-72j7-v7c2
CVE: CVE-2018-19296
CWE: CWE-1321, CWE-502, CWE-915
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-03-05
Source: https://github.com/advisories/GHSA-7w4p-72j7-v7c2
Type: github-advisory

## Affected
- Packagist: `phpmailer/phpmailer` — affected >=5.0.0 <5.2.27
- Packagist: `phpmailer/phpmailer` — affected >=6.0.0 <6.0.6

## Details
PHPMailer versions prior to 6.0.6 and 5.2.27 are vulnerable to an object injection attack by passing phar:// paths into `addAttachment()` and other functions that may receive unfiltered local paths, possibly leading to RCE. See [this article](https://knasmueller.net/5-answers-about-php-phar-exploitation) for more info on this type of vulnerability. Mitigated by blocking the use of paths containing URL-protocol style prefixes such as `phar://`. Reported by Sehun Oh of cyberone.kr.

### Impact
Object injection, possible remote code execution

### Patches
Fixed in 6.0.6 and 5.2.27

### Workarounds
Validate and sanitise user input before using.

### References
https://nvd.nist.gov/vuln/detail/CVE-2018-19296

### For more information
If you have any questions or comments about this advisory:
* Open a private issue in [the PHPMailer project](https://github.com/PHPMailer/PHPMailer)

## References
- https://github.com/PHPMailer/PHPMailer/security/advisories/GHSA-7w4p-72j7-v7c2
- https://nvd.nist.gov/vuln/detail/CVE-2018-19296
- https://github.com/FriendsOfPHP/security-advisories/blob/master/phpmailer/phpmailer/CVE-2018-19296.yaml
- https://github.com/PHPMailer/PHPMailer/releases/tag/v5.2.27
- https://github.com/PHPMailer/PHPMailer/releases/tag/v6.0.6
- https://lists.debian.org/debian-lts-announce/2018/12/msg00020.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3B5WDPGUFNPG4NAZ6G4BZX43BKLAVA5B
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KPU66INRFY5BQ3ESVPRUXJR4DXQAFJVT
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3B5WDPGUFNPG4NAZ6G4BZX43BKLAVA5B
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KPU66INRFY5BQ3ESVPRUXJR4DXQAFJVT
- https://www.debian.org/security/2018/dsa-4351
