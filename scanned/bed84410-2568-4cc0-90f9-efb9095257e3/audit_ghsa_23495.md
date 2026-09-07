# [H] TYPO3 Reveals Sensitive Information via Direct Request to `misc/phpcheck/`

## Summary
Severity: High
Advisory: GHSA-xj84-6q8f-qg2r
CVE: CVE-2005-4875
CWE: CWE-200
Ecosystem: Packagist
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-xj84-6q8f-qg2r
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=0 <3.8.1

## Details
TYPO3 3.8.0 and earlier allows remote attackers to obtain sensitive information via a direct request to misc/phpcheck/, which invokes the phpinfo function and prints values of unspecified environment variables.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2005-4875
- https://exchange.xforce.ibmcloud.com/vulnerabilities/42457
- https://github.com/TYPO3/typo3
- https://web.archive.org/web/20080228231555/http://typo3.org/teams/security/security-bulletins/typo3-20050725-1
- http://bugs.typo3.org/view.php?id=1250
- http://typo3.org/teams/security/security-bulletins/typo3-20050725-1
