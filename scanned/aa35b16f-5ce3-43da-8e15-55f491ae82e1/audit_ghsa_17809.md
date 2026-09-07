# [M] TYPO3 Potential Open Redirect via Parsing Differences

## Summary
Severity: Medium
Advisory: GHSA-2fx5-pggv-6jjr
CVE: CVE-2024-55892
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-01-14
Source: https://github.com/advisories/GHSA-2fx5-pggv-6jjr
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.49
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.48
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.42
- Packagist: `typo3/cms-core` — affected >=12.0.0 <12.4.25
- Packagist: `typo3/cms-core` — affected >=13.0.0 <13.4.3

## Details
### Problem
Applications that use `TYPO3\CMS\Core\Http\Uri` to parse externally provided URLs (e.g., via a query parameter) and validate the host of the parsed URL may be vulnerable to open redirect or SSRF attacks if the URL is used after passing the validation checks.

### Solution
Update to TYPO3 versions 9.5.49 ELTS, 10.4.48 ELTS, 11.5.42 ELTS, 12.4.25 LTS, 13.4.3 LTS that fix the problem described.

### Credits
Thanks to Sam Mush and Christian Eßl who reported this issue and to TYPO3 core & security team member Benjamin Franzke who fixed the issue.

### References
* [TYPO3-CORE-SA-2025-002](https://typo3.org/security/advisory/typo3-core-sa-2025-002)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-2fx5-pggv-6jjr
- https://nvd.nist.gov/vuln/detail/CVE-2024-55892
- https://github.com/TYPO3/typo3/commit/a4abf48d254685f43383e6e7f80d48aebaea56af
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2025-002
