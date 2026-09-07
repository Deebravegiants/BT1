# [C] PharStreamWrapper for Typo3 unsafe deserialization vulnerability

## Summary
Severity: Critical
Advisory: GHSA-3hxw-g85p-qgxm
CVE: CVE-2019-11830
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3hxw-g85p-qgxm
Type: github-advisory

## Affected
- Packagist: `typo3/phar-stream-wrapper` — affected >=2.0.0 <2.1.1
- Packagist: `typo3/phar-stream-wrapper` — affected >=3.0.0 <3.1.1

## Details
PharMetaDataInterceptor in the PharStreamWrapper (aka phar-stream-wrapper) package 2.x before 2.1.1 and 3.x before 3.1.1 for TYPO3 mishandles Phar stub parsing, which allows attackers to bypass a deserialization protection mechanism.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11830
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/phar-stream-wrapper/CVE-2019-11830.yaml
- https://github.com/TYPO3/phar-stream-wrapper
- https://github.com/TYPO3/phar-stream-wrapper/releases/tag/v2.1.1
- https://github.com/TYPO3/phar-stream-wrapper/releases/tag/v3.1.1
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/65ODQHDHWR74L6TCAPAQR5FQHG6MCXAW
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AUEXS4HRI4XZ2DTZMWAVQBYBTFSJ34AR
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/U6JX7WR6DPMKCZQP7EYFACYXSGJ3K523
- https://typo3.org/security/advisory/typo3-psa-2019-008
