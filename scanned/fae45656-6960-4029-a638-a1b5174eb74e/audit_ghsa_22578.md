# [H] Extbase for TYPO3 allows RCE

## Summary
Severity: High
Advisory: GHSA-jxg5-35fj-ccwf
CVE: CVE-2016-5091
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-jxg5-35fj-ccwf
Type: github-advisory

## Affected
- Packagist: `typo3/cms-extbase` — affected >=0 <6.2.24
- Packagist: `typo3/cms-extbase` — affected >=7.0 <7.6.8
- Packagist: `typo3/cms-extbase` — affected 8.1.1

## Details
Extbase in TYPO3 4.3.0 before 6.2.24, 7.x before 7.6.8, and 8.1.1 allows remote attackers to obtain sensitive information or possibly execute arbitrary code via a crafted Extbase action.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5091
- https://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2016-013
- http://www.openwall.com/lists/oss-security/2016/05/25/4
- http://www.openwall.com/lists/oss-security/2016/05/26/2
