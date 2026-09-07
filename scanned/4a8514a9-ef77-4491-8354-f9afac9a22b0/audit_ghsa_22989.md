# [M] DCE extension for Typo3 Discloses Environment Information

## Summary
Severity: Medium
Advisory: GHSA-v4vm-gj2x-6qhm
CVE: CVE-2014-8328
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-v4vm-gj2x-6qhm
Type: github-advisory

## Affected
- Packagist: `t3/dce` — affected >=0 <0.11.5

## Details
The default configuration in the Dynamic Content Elements (dce) extension before 0.11.5 for TYPO3 allows remote attackers to obtain sensitive installation environment information by reading the update check request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-8328
- https://exchange.xforce.ibmcloud.com/vulnerabilities/97673
- https://github.com/a-r-m-i-n/dce
- http://typo3.org/extensions/repository/view/dce
- http://typo3.org/teams/security/security-bulletins/typo3-extensions/typo3-ext-sa-2014-015
