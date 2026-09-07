# [M] Typo3 API Install Tool vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-c73w-4rcj-2622
CVE: CVE-2009-3636
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-c73w-4rcj-2622
Type: github-advisory

## Affected
- Packagist: `typo3/cms-install` — affected >=0
- Packagist: `typo3/cms-install` — affected >=4.1.0 <4.1.13
- Packagist: `typo3/cms-install` — affected >=4.2.0 <4.2.10
- Packagist: `typo3/cms-install` — affected >=4.3alpha1 <4.3beta2

## Details
Cross-site scripting (XSS) vulnerability in the Install Tool subcomponent in TYPO3 4.0.13 and earlier, 4.1.x before 4.1.13, 4.2.x before 4.2.10, and 4.3.x before 4.3beta2 allows remote attackers to inject arbitrary web script or HTML via unspecified parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-3636
- https://exchange.xforce.ibmcloud.com/vulnerabilities/53929
- https://github.com/TYPO3-CMS/install
- https://web.archive.org/web/20101223093042/http://www.securityfocus.com/bid/36801
- http://marc.info/?l=oss-security&m=125632856206736&w=2
- http://marc.info/?l=oss-security&m=125633199111438&w=2
- http://typo3.org/teams/security/security-bulletins/typo3-sa-2009-016
