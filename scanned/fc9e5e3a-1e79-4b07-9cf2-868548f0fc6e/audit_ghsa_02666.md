# [M] Cross-site Scripting in the femanager TYPO3 extension

## Summary
Severity: Medium
Advisory: GHSA-f3rf-v9qm-9c89
CVE: CVE-2021-36787
CWE: CWE-79
Ecosystem: Packagist
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-f3rf-v9qm-9c89
Type: github-advisory

## Affected
- Packagist: `in2code/femanager` — affected >=0 <5.5.1
- Packagist: `in2code/femanager` — affected >=6.0.0 <6.3.1

## Details
The extension allows by default to upload SVG files when a logged in frontend user uploads a new profile image. This may lead to Cross-Site Scripting, when the uploaded SVG image is used as is on the website.

Note: If SVG uploads are required, it is recommended to use the TYPO3 extension svg_sanitizer (added to TYPO3 core since versions 9.5.28, 10.4.18 and 11.3.0) to prevent upload of malicious SVG files or to set up a strict Content Security Policy for the destination folder of uploaded images.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36787
- https://github.com/in2code-de/femanager/commit/70f873c60f0e40ffd6a1300218ca368156fc1bf2
- https://extensions.typo3.org/extension/femanager
- https://github.com/in2code-de/femanager
- https://github.com/in2code-de/femanager/releases/tag/6.3.1
- https://typo3.org/help/security-advisories/security
- https://typo3.org/security/advisory/typo3-ext-sa-2021-010
- http://packetstormsecurity.com/files/165675/TYPO3-femanager-6.3.0-Cross-Site-Scripting.html
- http://seclists.org/fulldisclosure/2022/Jan/53
