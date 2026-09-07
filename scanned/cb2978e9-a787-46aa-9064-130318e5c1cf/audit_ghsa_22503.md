# [M] Typo3 Backend History Module Vulnerable to SQL Injection

## Summary
Severity: Medium
Advisory: GHSA-947m-vgqc-x6v4
CVE: CVE-2012-6144
CWE: CWE-89
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-947m-vgqc-x6v4
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=4.5.0 <4.5.21
- Packagist: `typo3/cms` — affected >=4.6.0 <4.6.14
- Packagist: `typo3/cms` — affected >=4.7.0 <4.7.6

## Details
SQL injection vulnerability in the Backend History module in TYPO3 4.5.x before 4.5.21, 4.6.x before 4.6.14, and 4.7.x before 4.7.6  Due to missing encoding of user input, the history module is susceptible to SQL Injection and Cross-Site Scripting. A valid backend login is required to exploit this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-6144
- https://exchange.xforce.ibmcloud.com/vulnerabilities/79964
- http://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2012-005
- http://www.openwall.com/lists/oss-security/2013/06/19/4
