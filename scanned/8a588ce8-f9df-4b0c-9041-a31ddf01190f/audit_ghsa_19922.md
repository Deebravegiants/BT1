# [H] TYPO3 CMS vulnerable to Arbitrary Code Execution via Form Framework

## Summary
Severity: High
Advisory: GHSA-c5wx-6c2c-f7rm
CVE: CVE-2022-23503
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-13
Source: https://github.com/advisories/GHSA-c5wx-6c2c-f7rm
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=8.0.0 <8.7.49
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.38
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.33
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.20
- Packagist: `typo3/cms-core` — affected >=12.0.0 <12.1.1
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.33
- Packagist: `typo3/cms` — affected >=11.0.0 <11.5.20
- Packagist: `typo3/cms` — affected >=12.0.0 <12.1.1

## Details
### Problem
Due to the lack of separating user-submitted data from the internal configuration in the Form Designer backend module, it was possible to inject code instructions to be processed and executed via TypoScript as PHP code.

The existence of individual TypoScript instructions for a particular form item (known as [`formDefinitionOverrides`](https://docs.typo3.org/c/typo3/cms-form/main/en-us/I/Concepts/FrontendRendering/Index.html#form-element-properties)) and a valid backend user account with access to the form module are needed to exploit this vulnerability.

### Solution
Update to TYPO3 versions 8.7.49 ELTS, 9.5.38 ELTS, 10.4.33, 11.5.20, 12.1.1 that fix the problem described above.

### References
* [TYPO3-CORE-SA-2022-015](https://typo3.org/security/advisory/typo3-core-sa-2022-015)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-c5wx-6c2c-f7rm
- https://nvd.nist.gov/vuln/detail/CVE-2022-23503
- https://github.com/TYPO3/typo3/commit/1302e88565821f2159e08b5d818d28de17ecc830
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2022-23503.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2022-23503.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2022-015
