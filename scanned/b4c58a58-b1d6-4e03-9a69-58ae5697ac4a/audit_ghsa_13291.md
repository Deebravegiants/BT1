# [M] By-passing Cross-Site Scripting Protection in HTML Sanitizer

## Summary
Severity: Medium
Advisory: GHSA-59jf-3q9v-rh6g
CVE: CVE-2023-38500
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-07-25
Source: https://github.com/advisories/GHSA-59jf-3q9v-rh6g
Type: github-advisory

## Affected
- Packagist: `typo3/html-sanitizer` — affected >=1.0.0 <1.5.1
- Packagist: `typo3/html-sanitizer` — affected >=2.0.0 <2.1.2

## Details
> ### CVSS: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N/E:F/RL:O/RC:C` (4.4)

### Problem
Due to an encoding issue in the serialization layer, malicious markup nested in a `noscript` element was not encoded correctly. `noscript` is disabled in the default configuration, but might have been enabled in custom scenarios. This allows bypassing the cross-site scripting mechanism of [`typo3/html-sanitizer`](https://packagist.org/packages/typo3/html-sanitizer).

### Solution
Update to `typo3/html-sanitizer` versions 1.5.1 or 2.1.2 that fix the problem described.

### Credits
Thanks to David Klein and Yaniv Nizry who reported this issue, and to TYPO3 security team members Oliver Hader and Benjamin Franzke who fixed the issue.

### References
* [TYPO3-CORE-SA-2023-002](https://typo3.org/security/advisory/typo3-core-sa-2023-002)

## References
- https://github.com/TYPO3/html-sanitizer/security/advisories/GHSA-59jf-3q9v-rh6g
- https://nvd.nist.gov/vuln/detail/CVE-2023-38500
- https://github.com/TYPO3/html-sanitizer/commit/e3026f589fef0be8c3574ee3f0a0bfbe33d7ebdb
- https://github.com/TYPO3/html-sanitizer
- https://typo3.org/security/advisory/typo3-core-sa-2023-002
