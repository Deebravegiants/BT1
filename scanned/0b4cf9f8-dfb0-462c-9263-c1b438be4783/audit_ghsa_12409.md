# [H] Configuration Injection in extension "Direct Mail" (direct_mail)

## Summary
Severity: High
Advisory: GHSA-p6xx-fhfw-7mj7
CVE: CVE-2023-50461
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-p6xx-fhfw-7mj7
Type: github-advisory

## Affected
- Packagist: `directmailteam/direct-mail` — affected >=8.0.0 <9.5.2
- Packagist: `directmailteam/direct-mail` — affected >=7.0.0 <7.0.3
- Packagist: `directmailteam/direct-mail` — affected >=0 <6.0.3

## Details
The “Configuration” backend module of the extension allows an authenticated user to write arbitrary page TSConfig for folders configured as “Direct Mail”. Exploiting the vulnerability may lead to Configuration Injection (TYPO3 10.4 and above) and to Arbitrary Code Execution (TYPO3 9.5 and below).

A valid backend user account having access to the Direct Mail "Configuration" backend  module is needed in order to exploit this vulnerability.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/directmailteam/direct-mail/CVE-2023-50461.yaml
- https://github.com/kartolo/direct_mail
- https://typo3.org/security/advisory/typo3-ext-sa-2023-011
