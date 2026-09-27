# [H] Cleartext storage of session identifier

## Summary
Severity: High
Advisory: GHSA-954j-f27r-cj52
CVE: CVE-2020-26228
CWE: CWE-312
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-11-23
Source: https://github.com/advisories/GHSA-954j-f27r-cj52
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.23
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.10
- Packagist: `typo3/cms-core` — affected >=8.7.0 <8.7.38
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.10
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.23
- Packagist: `typo3/cms` — affected >=8.7.0 <8.7.38

## Details
User session identifiers were stored in cleartext - without processing of additional cryptographic hashing algorithms. This vulnerability cannot be exploited directly and occurs in combination with a chained attack - like for instance SQL injection in any other component of the system.

### Solution
Update to TYPO3 versions 9.5.23 or 10.4.10 that fix the problem described.

### Credits
Thanks to TYPO3 security team member Helmut Hummel who reported this issue and to TYPO3 core & security team members Benni Mack & Oliver Hader as well as TYPO3 contributor Markus Klein who fixed the issue.

## References
- https://github.com/TYPO3/TYPO3.CMS/security/advisories/GHSA-954j-f27r-cj52
- https://nvd.nist.gov/vuln/detail/CVE-2020-26228
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2020-26228.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2020-26228.yaml
- https://typo3.org/security/advisory/typo3-core-sa-2020-011
