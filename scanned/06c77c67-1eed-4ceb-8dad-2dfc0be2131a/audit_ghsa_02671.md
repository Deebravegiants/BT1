# [C] Directory Traversal in typo3/phar-stream-wrapper

## Summary
Severity: Critical
Advisory: GHSA-xv7v-rf6g-xwrc
CVE: CVE-2019-11831
CWE: CWE-22, CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-30
Source: https://github.com/advisories/GHSA-xv7v-rf6g-xwrc
Type: github-advisory

## Affected
- Packagist: `typo3/phar-stream-wrapper` — affected >=2.0.0 <2.1.1
- Packagist: `typo3/phar-stream-wrapper` — affected >=3.0.0 <3.1.1
- Packagist: `drupal/core` — affected >=7.0.0 <7.67.0
- Packagist: `drupal/core` — affected >=8.0.0 <8.6.16
- Packagist: `drupal/core` — affected >=8.7.0 <8.7.1
- Packagist: `drupal/drupal` — affected >=7.0.0 <7.67.0
- Packagist: `drupal/drupal` — affected >=8.0.0 <8.6.16
- Packagist: `drupal/drupal` — affected >=8.7.0 <8.7.1

## Details
The PharStreamWrapper (aka phar-stream-wrapper) package 2.x before 2.1.1 and 3.x before 3.1.1 for TYPO3 does not prevent directory traversal, which allows attackers to bypass a deserialization protection mechanism, as demonstrated by a phar:///path/bad.phar/../good.phar URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11831
- https://www.synology.com/security/advisory/Synology_SA_19_22
- https://www.drupal.org/sa-core-2019-007
- https://www.debian.org/security/2019/dsa-4445
- https://typo3.org/security/advisory/typo3-psa-2019-007
- https://seclists.org/bugtraq/2019/May/36
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Z246UWBXBEKTQUDTLRJTC7XYBIO4IBE4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/U6JX7WR6DPMKCZQP7EYFACYXSGJ3K523
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/E3NUKPG7V4QEM6QXRMHYR4ABFMW5MM2P
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AUEXS4HRI4XZ2DTZMWAVQBYBTFSJ34AR
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6QDJVUJPUW3RZ4746SC6BX4F4T6ZXNBH
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/65ODQHDHWR74L6TCAPAQR5FQHG6MCXAW
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Z246UWBXBEKTQUDTLRJTC7XYBIO4IBE4
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/U6JX7WR6DPMKCZQP7EYFACYXSGJ3K523
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/E3NUKPG7V4QEM6QXRMHYR4ABFMW5MM2P
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AUEXS4HRI4XZ2DTZMWAVQBYBTFSJ34AR
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6QDJVUJPUW3RZ4746SC6BX4F4T6ZXNBH
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/65ODQHDHWR74L6TCAPAQR5FQHG6MCXAW
- https://lists.debian.org/debian-lts-announce/2019/05/msg00029.html
- https://github.com/TYPO3/phar-stream-wrapper/releases/tag/v3.1.1
