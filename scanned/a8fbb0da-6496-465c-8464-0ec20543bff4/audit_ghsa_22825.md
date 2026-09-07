# [C] TYPO3 vulnerable to authentication bypass via leveraging knowledge of password hash

## Summary
Severity: Critical
Advisory: GHSA-h7wf-jg4f-x2wc
CVE: CVE-2014-3945
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-h7wf-jg4f-x2wc
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=0 <6.2.0

## Details
The Authentication component in TYPO3 before 6.2, when salting for password hashing is disabled, does not require knowledge of the cleartext password if the password hash is known, which allows remote attackers to bypass authentication and gain access to the backend by leveraging knowledge of a password hash.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3945
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2014-001
- http://www.debian.org/security/2014/dsa-2942
- http://www.openwall.com/lists/oss-security/2014/06/03/2
