# [M] TYPO3 is vulnerable to Spam Abuse in the native form content element

## Summary
Severity: Medium
Advisory: GHSA-48ww-8h7g-4hwq
CVE: CVE-2010-3667
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-04-21
Source: https://github.com/advisories/GHSA-48ww-8h7g-4hwq
Type: github-advisory

## Affected
- Packagist: `typo3/cms-frontend` — affected >=0 <4.1.14
- Packagist: `typo3/cms-frontend` — affected >=4.2.0 <4.2.13
- Packagist: `typo3/cms-frontend` — affected >=4.3.0 <4.3.4
- Packagist: `typo3/cms-frontend` — affected >=4.4.0 <4.4.1

## Details
TYPO3 before 4.1.14, 4.2.x before 4.2.13, 4.3.x before 4.3.4 and 4.4.x before 4.4.1 allows Spam Abuse in the native form content element. An attacker could abuse the form to send mails to arbitrary email addresses.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-3667
- https://github.com/TYPO3/typo3/commit/34da374183dd472fa7987ee25b47544a06bd2173
- https://github.com/TYPO3/typo3/commit/5eb60976cea268b879e02811208e6a1777674cbb
- https://github.com/TYPO3/typo3/commit/78dbe326df7ebc612f40882920a426c82b2ca9d3
- https://github.com/TYPO3/typo3/commit/f82696c7d62842edb0bf79ef21a85d56735a1527
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=590719
- https://github.com/TYPO3-CMS/frontend
- https://security-tracker.debian.org/tracker/CVE-2010-3667
- https://typo3.org/security/advisory/typo3-sa-2010-012/#Spam_Abuse
