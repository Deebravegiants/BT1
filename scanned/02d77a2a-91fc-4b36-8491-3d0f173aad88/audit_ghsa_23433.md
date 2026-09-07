# [M] TYPO3 Sensitive Information Disclosure via escapeStrForLike method

## Summary
Severity: Medium
Advisory: GHSA-xgc2-q928-27wv
CVE: CVE-2010-5104
CWE: CWE-200
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-xgc2-q928-27wv
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=4.2.0 <4.2.16
- Packagist: `typo3/cms-core` — affected >=4.3.0 <4.3.9
- Packagist: `typo3/cms-core` — affected >=4.4.0 <4.4.5

## Details
The escapeStrForLike method in TYPO3 4.2.x before 4.2.16, 4.3.x before 4.3.9, and 4.4.x before 4.4.5 does not properly escape input when the MySQL database is set to sql_mode NO_BACKSLASH_ESCAPES, which allows remote attackers to obtain sensitive information via wildcard characters in a LIKE query.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-5104
- https://github.com/TYPO3/typo3/commit/9eb4be4ccf10e6959699b9cce375d48697f06cba
- https://github.com/TYPO3/typo3/commit/e8c32474a5571336681243465f42090cf056054f
- https://github.com/TYPO3/typo3/commit/fcabd2fc2aa557c94805f7505277185c4abb68ab
- https://exchange.xforce.ibmcloud.com/vulnerabilities/64185
- https://github.com/TYPO3-CMS/core
- https://web.archive.org/web/20101219052359/http://secunia.com/advisories/35770
- https://web.archive.org/web/20111025222220/http://typo3.org/teams/security/security-bulletins/typo3-sa-2010-022
- https://web.archive.org/web/20111223211753/http://www.securityfocus.com/bid/45470
- http://typo3.org/teams/security/security-bulletins/typo3-core/typo3-sa-2010-022
- http://www.openwall.com/lists/oss-security/2011/01/13/2
- http://www.openwall.com/lists/oss-security/2012/05/10/7
- http://www.openwall.com/lists/oss-security/2012/05/11/3
- http://www.openwall.com/lists/oss-security/2012/05/12/5
