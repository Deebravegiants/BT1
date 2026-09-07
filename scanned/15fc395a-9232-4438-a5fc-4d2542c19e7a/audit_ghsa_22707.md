# [M] TYPO3 allows remote authenticated backend users to unserialize arbitrary objects

## Summary
Severity: Medium
Advisory: GHSA-m4hw-r893-xh4g
CVE: CVE-2012-3527
CWE: CWE-502
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-m4hw-r893-xh4g
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=4.5.0 <4.5.19
- Packagist: `typo3/cms` — affected >=4.6.0 <4.6.12
- Packagist: `typo3/cms` — affected >=4.7.0 <4.7.4

## Details
view_help.php in the backend help system in TYPO3 4.5.x before 4.5.19, 4.6.x before 4.6.12 and 4.7.x before 4.7.4 allows remote authenticated backend users to unserialize arbitrary objects and possibly execute arbitrary PHP code via an unspecified parameter, related to a "missing signature (HMAC)."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-3527
- https://exchange.xforce.ibmcloud.com/vulnerabilities/77791
- https://github.com/TYPO3/typo3
- https://web.archive.org/web/20120817233148/http://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2012-004
- http://www.debian.org/security/2012/dsa-2537
- http://www.openwall.com/lists/oss-security/2012/08/22/8
