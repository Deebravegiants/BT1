# [M] TYPO3 CMS vulnerable to Insufficient Session Expiration after Password Reset

## Summary
Severity: Medium
Advisory: GHSA-mgj2-q8wp-29rr
CVE: CVE-2022-23502
CWE: CWE-613
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-13
Source: https://github.com/advisories/GHSA-mgj2-q8wp-29rr
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.33
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.20
- Packagist: `typo3/cms-core` — affected >=12.0.0 <12.1.1
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.33
- Packagist: `typo3/cms` — affected >=11.0.0 <11.5.20
- Packagist: `typo3/cms` — affected >=12.0.0 <12.1.1

## Details
### Problem
When users reset their password using the corresponding password recovery functionality, existing sessions for that particular user account were not revoked. This applied to both frontend user sessions and backend user sessions.

### Solution
Update to TYPO3 versions 10.4.33, 11.5.20, 12.1.1 that fix the problem described above.

### References
* [TYPO3-CORE-SA-2022-014](https://typo3.org/security/advisory/typo3-core-sa-2022-014)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-mgj2-q8wp-29rr
- https://nvd.nist.gov/vuln/detail/CVE-2022-23502
- https://github.com/TYPO3/typo3/commit/d9ffbf24fcc62068033ebb3912538347bd380a6c
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2022-23502.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2022-23502.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2022-014
