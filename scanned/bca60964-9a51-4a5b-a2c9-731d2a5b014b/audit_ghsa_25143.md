# [H] Pimcore Discloses Usernames In Use

## Summary
Severity: High
Advisory: GHSA-8889-9g3f-73rj
CVE: CVE-2019-18986
CWE: CWE-307
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8889-9g3f-73rj
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <6.2.2

## Details
Pimcore before 6.2.2 allow attackers to brute-force (guess) valid usernames by using the 'forgot password' functionality as it returns distinct messages for invalid password and non-existing users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18986
- https://github.com/pimcore/pimcore/commit/4a7bba5c3f818852cbbd29fa124f7fb09a207185
- https://github.com/pimcore/pimcore
- https://github.com/pimcore/pimcore/compare/v6.2.1...v6.2.2
