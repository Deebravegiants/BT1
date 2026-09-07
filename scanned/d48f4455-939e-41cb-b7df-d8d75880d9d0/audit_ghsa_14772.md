# [H] TYPO3 Arbitrary Code Execution via File List Module

## Summary
Severity: High
Advisory: GHSA-8h4m-r4wm-xj7r
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-8h4m-r4wm-xj7r
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.23
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.4

## Details
Due to missing file extensions in $GLOBALS['TYPO3_CONF_VARS']['BE'][‘fileDenyPattern’], backend users are allowed to upload *.phar, *.shtml, *.pl or *.cgi files which can be executed in certain web server setups. A valid backend user account is needed in order to exploit this vulnerability.

Derivatives of Debian GNU Linux are handling *.phar files as PHP applications since PHP 7.1 (for unofficial packages) and PHP 7.2 (for official packages).

The file extension *.shtml is bound to server side includes which are not enabled per default in most common Linux based distributions. File extension *.pl and *.cgi require additional handlers to be configured which is also not the case in most common distributions (except for /cgi-bin/ location).

## References
- https://github.com/TYPO3/typo3/commit/095ae4ab6869d0f7dc7befedb851cdd7ad0c7ebf
- https://github.com/TYPO3/typo3/commit/9990278ce7cf8e4d6b8bf31edec6787722d38b0f
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2019-01-22-7.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2019-008
