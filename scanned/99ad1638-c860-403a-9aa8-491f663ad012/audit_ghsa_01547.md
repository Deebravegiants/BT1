# [H] Exposure of Sensitive Information to an Unauthorized Actor in TYPO3 CMS

## Summary
Severity: High
Advisory: GHSA-3x94-fv5h-5q2c
CVE: CVE-2020-15099
CWE: CWE-20, CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-07-29
Source: https://github.com/advisories/GHSA-3x94-fv5h-5q2c
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.20
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.6
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.6
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.20

## Details
> ### Meta
> * CVSS: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H/E:F/RL:O/RC:C` (7.5)
> * CWE-20, CWE-200

### Problem
In case an attacker manages to generate a valid cryptographic message authentication code (HMAC-SHA1) - either by using a different existing vulnerability or in case the internal _encryptionKey_ was exposed - it is possible to retrieve arbitrary files of a TYPO3 installation. This includes the possibility to fetch _typo3conf/LocalConfiguration.php_ which again contains the _encryptionKey_ as well as credentials of the database management system being used.

In case a database server is directly accessible either via internet or in a shared hosting network, this allows to completely retrieve, manipulate or delete database contents. This includes creating an administration user account - which can be used to trigger remote code execution by injecting custom extensions.

### Solution
Update to TYPO3 versions 9.5.20 or 10.4.6 that fix the problem described.

### Credits
Thanks to TYPO3 security team member Oliver Hader who reported and fixed the issue.

### References
* [TYPO3-CORE-SA-2020-007](https://typo3.org/security/advisory/typo3-core-sa-2020-007)

## References
- https://github.com/TYPO3/TYPO3.CMS/security/advisories/GHSA-3x94-fv5h-5q2c
- https://nvd.nist.gov/vuln/detail/CVE-2020-15099
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2020-15099.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2020-15099.yaml
- https://github.com/TYPO3/TYPO3.CMS
- https://typo3.org/security/advisory/typo3-core-sa-2020-007
