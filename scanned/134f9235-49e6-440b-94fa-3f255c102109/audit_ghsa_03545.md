# [H] Broken Access Control in Form Framework

## Summary
Severity: High
Advisory: GHSA-3vg7-jw9m-pc3f
CVE: CVE-2021-21357
CWE: CWE-20, CWE-22, CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H/E:H/RL:O/RC:C (CVSS_V3)
Published: 2021-03-23
Source: https://github.com/advisories/GHSA-3vg7-jw9m-pc3f
Type: github-advisory

## Affected
- Packagist: `typo3/cms-form` — affected >=8.0.0 <8.7.40
- Packagist: `typo3/cms-form` — affected >=9.0.0 <9.5.25
- Packagist: `typo3/cms-form` — affected >=10.0.0 <10.4.14
- Packagist: `typo3/cms-form` — affected >=11.0.0 <11.1.1
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.14
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.1.1
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.25
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.14
- Packagist: `typo3/cms` — affected >=11.0.0 <11.1.1
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.25

## Details
### Problem
Due to improper input validation, attackers can by-pass restrictions of predefined options and submit arbitrary data in the Form Designer backend module of the Form Framework.

In the default configuration of the Form Framework this allows attackers to explicitly allow arbitrary mime-types for file uploads - however, default _fileDenyPattern_ successfully blocked files like _.htaccess_ or _malicious.php_. Besides that, attackers can persist those files in any writable directory of the corresponding TYPO3 installation.

A valid backend user account with access to the form module is needed to exploit this vulnerability.

### Solution
Update to TYPO3 versions 8.7.40, 9.5.25, 10.4.14, 11.1.1 that fix the problem described.

### Credits
Thanks to Richie Lee who reported this issue and to TYPO3 contributor Ralf Zimmermann who fixed the issue.

### References
* [TYPO3-CORE-SA-2021-003](https://typo3.org/security/advisory/typo3-core-sa-2021-003)

## References
- https://github.com/TYPO3/TYPO3.CMS/security/advisories/GHSA-3vg7-jw9m-pc3f
- https://nvd.nist.gov/vuln/detail/CVE-2021-21357
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2021-21357.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2021-21357.yaml
- https://packagist.org/packages/typo3/cms-form
- https://typo3.org/security/advisory/typo3-core-sa-2021-003
