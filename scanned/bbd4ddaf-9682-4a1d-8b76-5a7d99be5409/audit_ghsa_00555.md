# [M] Ckeditor XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g68x-vvqq-pvw3
CVE: CVE-2018-17960
CWE: CWE-79
Ecosystem: Packagist, npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-11-21
Source: https://github.com/advisories/GHSA-g68x-vvqq-pvw3
Type: github-advisory

## Affected
- npm: `ckeditor` — affected >=0 <4.11.0
- Packagist: `typo3/cms-core` — affected >=8.0.0 <8.7.21
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.2
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.21
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.2

## Details
CKEditor 4.x before 4.11.0 allows user-assisted XSS involving a source-mode paste. It was possible to execute XSS inside the CKEditor source area after persuading the victim to: (i) switch CKEditor to source mode, then (ii) paste a specially crafted HTML code, prepared by the attacker, into the opened CKEditor source area, and (iii) switch back to WYSIWYG mode. Although this is an unlikely scenario, it is recommended to upgrade to the latest editor version.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17960
- https://ckeditor.com/blog/CKEditor-4.11-with-emoji-dropdown-and-auto-link-on-typing-released
- https://ckeditor.com/cke4/release/CKEditor-4.11.0
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2018-17960.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2018-17960.yaml
- https://github.com/advisories/GHSA-g68x-vvqq-pvw3
- https://typo3.org/security/advisory/typo3-core-sa-2018-005
- https://web.archive.org/web/20200227030123/http://www.securityfocus.com/bid/109205
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
