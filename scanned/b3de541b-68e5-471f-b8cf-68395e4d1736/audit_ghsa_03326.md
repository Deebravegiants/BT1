# [C] Object injection in PHPMailer/PHPMailer

## Summary
Severity: Critical
Advisory: GHSA-m298-fh5c-jc66
CVE: CVE-2020-36326
CWE: CWE-502, CWE-641
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-04
Source: https://github.com/advisories/GHSA-m298-fh5c-jc66
Type: github-advisory

## Affected
- Packagist: `phpmailer/phpmailer` — affected >=6.1.8 <6.4.1

## Details
### Impact
This is a reintroduction of an earlier issue (CVE-2018-19296) by an unrelated bug fix in PHPMailer 6.1.8.  An external file may be unexpectedly executable if it is used as a path to an attachment file via PHP's support for `.phar` files. Exploitation requires that an attacker is able to provide an unfiltered path to a file to attach, or to trick calling code into generating one. See [this article](https://knasmueller.net/5-answers-about-php-phar-exploitation) for more info.

### Patches
This issue was patched in the PHPMailer 6.4.1 release. This release also implements stricter filtering for attachment paths; paths that look like *any* kind of URL are rejected.

### Workarounds
Validate paths to loaded files using the same pattern as used in [`isPermittedPath()`](https://github.com/PHPMailer/PHPMailer/blob/master/src/PHPMailer.php#L1815) before using them in *any* PHP file function, such as `file_exists`. This method can't be used directly because it is protected, but you can implement the same thing in calling code. Note that this should be applied to *all* user-supplied paths passed into such functions; it's not a problem specific to PHPMailer.

### Credit
This issue was found by [Fariskhi Vidyan](https://github.com/farisv), reported and managed via Tidelift.

## References
- https://github.com/PHPMailer/PHPMailer/security/advisories/GHSA-m298-fh5c-jc66
- https://nvd.nist.gov/vuln/detail/CVE-2020-36326
- https://github.com/PHPMailer/PHPMailer/commit/e2e07a355ee8ff36aba21d0242c5950c56e4c6f9
- https://github.com/FriendsOfPHP/security-advisories/blob/master/phpmailer/phpmailer/CVE-2020-36326.yaml
- https://github.com/PHPMailer/PHPMailer
- https://github.com/PHPMailer/PHPMailer/releases/tag/v6.4.1
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3B5WDPGUFNPG4NAZ6G4BZX43BKLAVA5B
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KPU66INRFY5BQ3ESVPRUXJR4DXQAFJVT
