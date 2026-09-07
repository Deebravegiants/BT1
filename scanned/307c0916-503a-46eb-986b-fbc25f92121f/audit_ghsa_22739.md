# [M] Typo3 Extbase Framework Unsafe Deserialization

## Summary
Severity: Medium
Advisory: GHSA-7jfm-px59-99w8
CVE: CVE-2012-1605
CWE: CWE-502
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-7jfm-px59-99w8
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=4.6 <4.6.7
- Packagist: `typo3/cms` — affected >=4.4.0 <4.4.14
- Packagist: `typo3/cms` — affected >=4.5.0 <4.5.14

## Details
The Extbase Framework in TYPO3 4.6.x through 4.6.6, 4.7, and 6.0 unserializes untrusted data, which allows remote attackers to unserialize arbitrary objects and possibly execute arbitrary code via vectors related to "a missing signature (HMAC) for a request argument."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-1605
- https://web.archive.org/web/20120527123559/http://www.securityfocus.com/bid/52771
- http://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2012-001
- http://www.openwall.com/lists/oss-security/2012/03/30/4
