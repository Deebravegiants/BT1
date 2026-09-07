# [H] TYPO3 SQL Injection in extension "Address List" (tt_address)

## Summary
Severity: High
Advisory: GHSA-3h52-6v6j-6wwv
CVE: CVE-2026-8827
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-3h52-6v6j-6wwv
Type: github-advisory

## Affected
- Packagist: `friendsoftypo3/tt-address` — affected >=10.0.0 <10.0.1
- Packagist: `friendsoftypo3/tt-address` — affected >=9.0.0 <9.1.1
- Packagist: `friendsoftypo3/tt-address` — affected >=0 <8.1.2

## Details
In the TYPO3 extension `tt_address`, the `AddressRepository::getSqlQuery()` method constructs a database query without properly sanitizing user input, leading to SQL Injection. The method is not invoked anywhere within the extension itself and therefore poses no direct risk in a default installation. However, custom extensions that call this method with untrusted input would expose the site to SQL injection. This has been patched in version 8.1.2, 9.1.1, and 10.0.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8827
- https://github.com/FriendsOfPHP/security-advisories/blob/master/friendsoftypo3/tt-address/CVE-2026-8827.yaml
- https://github.com/FriendsOfTYPO3/tt_address
- https://typo3.org/security/advisory/typo3-ext-sa-2026-012
