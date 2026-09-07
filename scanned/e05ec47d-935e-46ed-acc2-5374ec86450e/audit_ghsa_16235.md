# [M] TYPO3 vulnerable to Improper Access Control of Resources Referenced by t3:// URI Scheme

## Summary
Severity: Medium
Advisory: GHSA-wf85-8hx9-gj7c
CVE: CVE-2024-25120
CWE: CWE-200, CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-13
Source: https://github.com/advisories/GHSA-wf85-8hx9-gj7c
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=8.0.0 <8.7.57
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.46
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.43
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.35
- Packagist: `typo3/cms-core` — affected >=12.0.0 <12.4.11
- Packagist: `typo3/cms-core` — affected >=13.0.0 <13.0.1

## Details
### Problem
The TYPO3-specific [`t3://` URI scheme](https://docs.typo3.org/m/typo3/reference-typoscript/main/en-us/Functions/Typolink.html#resource-references) could be used to access resources outside of the users' permission scope. This encompassed files, folders, pages, and records (although only if a valid link-handling configuration was provided). Exploiting this vulnerability requires a valid backend user account.

### Solution
Update to TYPO3 versions 8.7.57 ELTS, 9.5.46 ELTS, 10.4.43 ELTS, 11.5.35 LTS, 12.4.11 LTS, 13.0.1 that fix the problem described.

### Credits
Thanks to Richie Lee who reported this issue and to TYPO3 core & security team member Benjamin Franzke who fixed the issue.

### References
* [TYPO3-CORE-SA-2024-005](https://typo3.org/security/advisory/typo3-core-sa-2024-005)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-wf85-8hx9-gj7c
- https://nvd.nist.gov/vuln/detail/CVE-2024-25120
- https://github.com/TYPO3/typo3/commit/2de87ff113ba24333ab7cbb8078588743f8958d6
- https://github.com/TYPO3/typo3/commit/33f4d279b82bca0a509227a17065244c6156e68f
- https://github.com/TYPO3/typo3/commit/ae0dfc4c058a90c10eedb3f49cfaf33164d21cdd
- https://docs.typo3.org/m/typo3/reference-typoscript/main/en-us/Functions/Typolink.html#resource-references
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2024-005
