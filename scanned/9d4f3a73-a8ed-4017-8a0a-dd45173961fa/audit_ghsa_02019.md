# [H] PHPMailer untrusted code may be run from an overridden address validator

## Summary
Severity: High
Advisory: GHSA-77mr-wc79-m8j3
CVE: CVE-2021-3603
CWE: CWE-74, CWE-829
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-22
Source: https://github.com/advisories/GHSA-77mr-wc79-m8j3
Type: github-advisory

## Affected
- Packagist: `phpmailer/phpmailer` — affected >=0 <6.5.0

## Details
If a function is defined that has the same name as the default built-in email address validation scheme (`php`), it will be called in default configuration as when no validation scheme is provided, the default scheme's callable `php` was being called. If an attacker is able to inject such a function into the application (a much bigger issue), it will be called whenever an email address is validated, such as when calling `validateAddress()`.

### Impact
Low impact – exploitation requires that an attacker can already inject code into an application, but it provides a trigger pathway.

### Patches
This is patched in PHPMailer 6.5.0 by denying the use of simple strings as validator function names, which is a very minor BC break.

### Workarounds
Inject your own email validator function.

### References
Reported by [Vikrant Singh Chauhan](mailto:vi@hackberry.xyz) via [huntr.dev](https://www.huntr.dev/).
[CVE-2021-3603](https://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2021-3603)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the PHPMailer project](https://github.com/PHPMailer/PHPMailer)
* [Email us](mailto:phpmailer@synchromedia.co.uk).

## References
- https://github.com/PHPMailer/PHPMailer/security/advisories/GHSA-77mr-wc79-m8j3
- https://nvd.nist.gov/vuln/detail/CVE-2021-3603
- https://github.com/PHPMailer/PHPMailer/commit/45f3c18dc6a2de1cb1bf49b9b249a9ee36a5f7f3
- https://github.com/FriendsOfPHP/security-advisories/blob/master/phpmailer/phpmailer/CVE-2021-3603.yaml
- https://github.com/PHPMailer/PHPMailer
- https://github.com/PHPMailer/PHPMailer/releases/tag/v6.5.0
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3YRMWGA4VTMXFB22KICMB7YMFZNFV3EJ
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FJYSOFCUBS67J3TKR74SD3C454N7VTYM
- https://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2021-3603
- https://www.huntr.dev/bounties/1-PHPMailer/PHPMailer
