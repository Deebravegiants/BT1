# [H] TYPO3 PHP remote file inclusion vulnerability

## Summary
Severity: High
Advisory: GHSA-4h9j-f98m-p4hg
CVE: CVE-2010-1153
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-4h9j-f98m-p4hg
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=4.3.0 <4.3.3

## Details
PHP remote file inclusion vulnerability in the autoloader in TYPO3 4.3.x before 4.3.3 allows remote attackers to execute arbitrary PHP code via a URL in an input field associated with the className variable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-1153
- https://github.com/TYPO3/typo3
- https://web.archive.org/web/20100813082506/http://typo3.org/teams/security/security-bulletins/typo3-sa-2010-008
- http://marc.info/?l=oss-security&m=127092306209177&w=2
- http://www.openwall.com/lists/oss-security/2010/04/12/1
