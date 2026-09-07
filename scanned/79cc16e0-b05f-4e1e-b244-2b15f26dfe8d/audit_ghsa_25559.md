# [M] TYPO3 is vulnerable to Insecure randomness in uniqid function

## Summary
Severity: Medium
Advisory: GHSA-c7xr-736p-29j3
CVE: CVE-2010-3666
CWE: CWE-330
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-04-21
Source: https://github.com/advisories/GHSA-c7xr-736p-29j3
Type: github-advisory

## Affected
- Packagist: `typo3/cms-install` — affected >=0 <4.1.14
- Packagist: `typo3/cms-install` — affected >=4.2.0 <4.2.13
- Packagist: `typo3/cms-install` — affected >=4.3.0 <4.3.4
- Packagist: `typo3/cms-install` — affected >=4.4.0 <4.4.1

## Details
TYPO3 before 4.1.14, 4.2.x before 4.2.13, 4.3.x before 4.3.4 and 4.4.x before 4.4.1 contains insecure randomness in the `uniqid` function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-3666
- https://github.com/TYPO3/typo3/commit/302b35e714ca30ddb71ab36b9cbb2bea760a2f0e
- https://github.com/TYPO3/typo3/commit/352d6066bf09137e86705bc060fd4ab3ba8f9191
- https://github.com/TYPO3/typo3/commit/42324b30546b1e49fb16c916fc71cceb99ad9fd0
- https://github.com/TYPO3/typo3/commit/f6d2e33cfab87c9e44eca275d6755be747e3cd7e
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=590719
- https://github.com/TYPO3-CMS/install
- https://security-tracker.debian.org/tracker/CVE-2010-3666
- https://typo3.org/security/advisory/typo3-sa-2010-012/#Insecure_Randomness
