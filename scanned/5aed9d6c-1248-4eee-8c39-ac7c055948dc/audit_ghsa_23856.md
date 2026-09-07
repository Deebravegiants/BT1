# [M] TYPO3 Install Tool Subcomponent Allows Access Using Only a Password's MD5 Hash as a Credential

## Summary
Severity: Medium
Advisory: GHSA-hwrc-w5gg-f335
CVE: CVE-2009-3635
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-hwrc-w5gg-f335
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=0
- Packagist: `typo3/cms` — affected >=4.1.0 <4.1.13
- Packagist: `typo3/cms` — affected >=4.2.0 <4.2.10
- Packagist: `typo3/cms` — affected >=4.3beta1 <4.3beta2

## Details
The Install Tool subcomponent in TYPO3 4.0.13 and earlier, 4.1.x before 4.1.13, 4.2.x before 4.2.10, and 4.3.x before 4.3beta2 allows remote attackers to gain access by using only the password's md5 hash as a credential.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-3635
- https://exchange.xforce.ibmcloud.com/vulnerabilities/53928
- https://github.com/TYPO3/typo3
- https://web.archive.org/web/20100105023145/http://typo3.org/teams/security/security-bulletins/typo3-sa-2009-016
- https://web.archive.org/web/20200229210314/http://www.securityfocus.com/bid/36801
- http://marc.info/?l=oss-security&m=125632856206736&w=2
- http://typo3.org/teams/security/security-bulletins/typo3-sa-2009-016
