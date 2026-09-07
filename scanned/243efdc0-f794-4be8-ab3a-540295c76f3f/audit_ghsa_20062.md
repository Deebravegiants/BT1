# [M] TYPO3 CMS vulnerable to Denial of Service in Page Error Handling

## Summary
Severity: Medium
Advisory: GHSA-8c28-5mp7-v24h
CVE: CVE-2022-23500
CWE: CWE-405, CWE-674
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-13
Source: https://github.com/advisories/GHSA-8c28-5mp7-v24h
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.38
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.33
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.20
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.33
- Packagist: `typo3/cms` — affected >=11.0.0 <11.5.20

## Details
### Problem
Requesting invalid or non-existing resources via HTTP triggers the page error handler, which again could retrieve content to be shown as an error message from another page. This leads to a scenario in which the application is calling itself recursively - amplifying the impact of the initial attack until the limits of the web server are exceeded.

This vulnerability is very similar, but not identical, to the one described in [TYPO3-CORE-SA-2021-005](https://typo3.org/security/advisory/typo3-core-sa-2021-005) (CVE-2021-21359).

### Solution
Update to TYPO3 versions 9.5.38 ELTS, 10.4.33 or 11.5.20 that fix the problem described above.

### References
* [TYPO3-CORE-SA-2022-012](https://typo3.org/security/advisory/typo3-core-sa-2022-012)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-8c28-5mp7-v24h
- https://nvd.nist.gov/vuln/detail/CVE-2022-23500
- https://github.com/TYPO3/typo3/commit/1e5f44417f031c9c5a9f9d09a6a841cf89aa7b7a
- https://github.com/TYPO3/typo3/commit/73b46b6a627093112cfca4b895a198ca5e1970b7
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2022-23500.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2022-012
