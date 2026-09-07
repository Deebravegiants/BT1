# [M] TYPO3 is vulnerable to insecure randomness during hash generation in forgot password function

## Summary
Severity: Medium
Advisory: GHSA-3276-p9f2-8q89
CVE: CVE-2010-3670
CWE: CWE-326
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-21
Source: https://github.com/advisories/GHSA-3276-p9f2-8q89
Type: github-advisory

## Affected
- Packagist: `typo3/cms-frontend` — affected >=0 <4.3.4
- Packagist: `typo3/cms-frontend` — affected >=4.4.0 <4.4.1

## Details
TYPO3 before 4.3.4 and 4.4.x before 4.4.1 contains insecure randomness during generation of a hash with the "forgot password" function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-3670
- https://github.com/TYPO3/typo3/commit/09ab77653161f23e266470a5984d4d5e64588355
- https://github.com/TYPO3/typo3/commit/c03e944d200bf427bb18cad15f2ad36bc83061c9
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=590719
- https://github.com/TYPO3-CMS/frontend
- https://security-tracker.debian.org/tracker/CVE-2010-3670
- https://typo3.org/security/advisory/typo3-sa-2010-012/#Insecure_Randomness
