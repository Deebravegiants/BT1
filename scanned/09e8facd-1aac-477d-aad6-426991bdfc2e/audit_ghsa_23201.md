# [M] TYPO3 Backend vulnerable to Frame Hijacking

## Summary
Severity: Medium
Advisory: GHSA-mg66-3x8x-r8g2
CVE: CVE-2009-3630
Ecosystem: Packagist
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-mg66-3x8x-r8g2
Type: github-advisory

## Affected
- Packagist: `typo3/cms-backend` — affected >=0
- Packagist: `typo3/cms-backend` — affected >=4.1.0 <4.1.13
- Packagist: `typo3/cms-backend` — affected >=4.2.0 <4.2.10
- Packagist: `typo3/cms-backend` — affected >=4.3alpha1 <4.3beta2

## Details
The Backend subcomponent in TYPO3 4.0.13 and earlier, 4.1.x before 4.1.13, 4.2.x before 4.2.10, and 4.3.x before 4.3beta2 allows remote authenticated users to place arbitrary web sites in TYPO3 backend framesets via crafted parameters, related to a "frame hijacking" issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-3630
- https://exchange.xforce.ibmcloud.com/vulnerabilities/53920
- https://github.com/TYPO3-CMS/backend
- https://web.archive.org/web/20101223093042/http://www.securityfocus.com/bid/36801
- http://marc.info/?l=oss-security&m=125632856206736&w=2
- http://typo3.org/teams/security/security-bulletins/typo3-sa-2009-016
