# [M] TYPO3 Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-j5v7-9xr5-m7gx
CVE: CVE-2015-8759
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-j5v7-9xr5-m7gx
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.16
- Packagist: `typo3/cms` — affected >=7.0.0 <7.6.1

## Details
Cross-site scripting (XSS) vulnerability in the typoLink function in TYPO3 6.2.x before 6.2.16 and 7.x before 7.6.1 allows remote authenticated editors to inject arbitrary web script or HTML via a link field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8759
- https://github.com/TYPO3/typo3/commit/25a1473907f0f4b2bb0147c661981940c57a4555
- https://github.com/TYPO3/typo3/commit/de1755a6dcff9b037c6d5a1fa340ba100aff054a
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2015-12-15-2.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2015-012
- https://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2015-012
- https://web.archive.org/web/20200228051548/http://www.securityfocus.com/bid/79250
