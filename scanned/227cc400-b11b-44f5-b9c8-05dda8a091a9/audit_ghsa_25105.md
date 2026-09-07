# [H] Indexed Search Engine for TYPO3 Command Execution via Metacharacter Injection

## Summary
Severity: High
Advisory: GHSA-74w6-ww7w-45j9
CVE: CVE-2009-0258
CWE: CWE-20, CWE-78
Ecosystem: Packagist
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-74w6-ww7w-45j9
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=4.0.0 <4.0.10
- Packagist: `typo3/cms` — affected >=4.1.0 <4.1.8
- Packagist: `typo3/cms` — affected >=4.2.0 <4.2.4

## Details
The Indexed Search Engine (indexed_search) system extension in TYPO3 4.0.0 through 4.0.9, 4.1.0 through 4.1.7, and 4.2.0 through 4.2.3 allows remote attackers to execute arbitrary commands via a crafted filename containing shell metacharacters, which is not properly handled by the command-line indexer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-0258
- https://exchange.xforce.ibmcloud.com/vulnerabilities/48138
- https://web.archive.org/web/20111210005350/http://www.securityfocus.com/bid/33376
- http://typo3.org/teams/security/security-bulletins/typo3-sa-2009-001
- http://www.debian.org/security/2009/dsa-1711
- http://www.openwall.com/lists/oss-security/2009/01/23/4
