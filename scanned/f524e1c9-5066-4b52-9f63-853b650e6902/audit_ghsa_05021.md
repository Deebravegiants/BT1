# [M] TYPO3 HTML Sanitizer allows Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-p5j5-4j3q-8mq8
CVE: CVE-2026-47345
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-p5j5-4j3q-8mq8
Type: github-advisory

## Affected
- Packagist: `typo3/html-sanitizer` — affected >=0 <2.3.2

## Details
Namespace attributes are not encoded correctly during HTML serialization. This allows bypassing the cross-site scripting prevention mechanism of `typo3/html-sanitizer` before version 2.3.2.

Credits to Doyensec in collaboration with Claude and Anthropic Research for reporting this vulnerability.

## References
- https://github.com/TYPO3/html-sanitizer/security/advisories/GHSA-p5j5-4j3q-8mq8
- https://nvd.nist.gov/vuln/detail/CVE-2026-47345
- https://github.com/TYPO3/html-sanitizer/commit/8b5d0be44ded457ca993ec9ca93d859941c63764
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/html-sanitizer/CVE-2026-47345.yaml
- https://github.com/TYPO3/html-sanitizer
- https://typo3.org/security/advisory/typo3-core-sa-2026-006
