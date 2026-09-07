# [M] TYPO3 vulnerable to Weak Authentication in Session Handling

## Summary
Severity: Medium
Advisory: GHSA-3vmm-7h4j-69rm
CVE: CVE-2023-47127
CWE: CWE-287, CWE-302
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-11-14
Source: https://github.com/advisories/GHSA-3vmm-7h4j-69rm
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=8.0.0 <8.7.55
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.44
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.41
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.33
- Packagist: `typo3/cms-core` — affected >=12.0.0 <12.4.8

## Details
> ### CVSS: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N/E:X/RL:O/RC:C` (4.0)

### Problem
Given that there are at least two different sites in the same TYPO3 installation - for instance _first.example.org_ and _second.example.com_ - then a session cookie generated for the first site can be reused on the second site without requiring additional authentication.

This vulnerability primarily affects the frontend of the website. It's important to note that exploiting this vulnerability requires a valid user account.

### Solution
Update to TYPO3 versions 8.7.55 ELTS, 9.5.44 ELTS, 10.4.41 ELTS, 11.5.33, 12.4.8 that fix the problem described above.

### Credits
Thanks to Rémy Daniel who reported this issue, and to TYPO3 core & security team member Benjamin Franzke who fixed the issue.

### References
* [TYPO3-CORE-SA-2023-006](https://typo3.org/security/advisory/typo3-core-sa-2023-006)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-3vmm-7h4j-69rm
- https://nvd.nist.gov/vuln/detail/CVE-2023-47127
- https://github.com/TYPO3/typo3/commit/535dfbdc54fd5362e0bc08d911db44eac7f64019
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2023-47127.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2023-006
