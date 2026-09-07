# [M] TYPO3 CMS vulnerable to Sensitive Information Disclosure via YAML Placeholder Expressions in Site Configuration

## Summary
Severity: Medium
Advisory: GHSA-8w3p-qh3x-6gjr
CVE: CVE-2022-23504
CWE: CWE-200, CWE-917
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2022-12-13
Source: https://github.com/advisories/GHSA-8w3p-qh3x-6gjr
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.38
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.33
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.20
- Packagist: `typo3/cms-core` — affected >=12.0.0 <12.1.1
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.33
- Packagist: `typo3/cms` — affected >=11.0.0 <11.5.20
- Packagist: `typo3/cms` — affected >=12.0.0 <12.1.1

## Details
> ### CVSS: `CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:L/A:L/E:F/RL:O/RC:C` (5.3)

### Problem
Due to the lack of handling user-submitted [YAML placeholder expressions](https://docs.typo3.org/m/typo3/reference-coreapi/main/en-us/Configuration/Yaml/YamlApi.html#custom-placeholder-processing) in the site configuration backend module, attackers could expose sensitive internal information, such as system configuration or HTTP request messages of other website visitors.

A valid backend user account having administrator privileges is needed to exploit this vulnerability.

### Solution
Update to TYPO3 versions 9.5.38 ELTS, 10.4.33, 11.5.20, 12.1.1 that fix the problem described above.

### Credits
Thanks to TYPO3 core & security team member Oliver Hader who reported and fixed the issue.

### References
* [TYPO3-CORE-SA-2022-016](https://typo3.org/security/advisory/typo3-core-sa-2022-016)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-8w3p-qh3x-6gjr
- https://nvd.nist.gov/vuln/detail/CVE-2022-23504
- https://github.com/TYPO3/typo3/commit/d1e627ff7eef07bd94c53db861e85977b203900a
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2022-23504.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2022-23504.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2022-016
