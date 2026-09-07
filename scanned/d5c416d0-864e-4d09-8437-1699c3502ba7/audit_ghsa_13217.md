# [M] Neos CMS Cross Site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6qjf-7g3j-qx25
CVE: CVE-2023-37611
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-09-19
Source: https://github.com/advisories/GHSA-6qjf-7g3j-qx25
Type: github-advisory

## Affected
- Packagist: `neos/media-browser` — affected >=0 <7.3.19
- Packagist: `neos/media-browser` — affected >=8.0.0 <8.0.16
- Packagist: `neos/media-browser` — affected >=8.1.0 <8.1.11
- Packagist: `neos/media-browser` — affected >=8.2.0 <8.2.11
- Packagist: `neos/media-browser` — affected >=8.3.0 <8.3.9

## Details
Cross Site Scripting (XSS) vulnerability in Neos CMS 8.3.3 allows a remote authenticated attacker to execute arbitrary code via a crafted SVG file uploaded to the `neos/management/media` component. To make use of this attack vector, the attacker must either be able to upload a maliciously crafted file or coerce someone with the needed access to upload said file to Neos. Even if such a file is uploaded and subsequently delivered, it is possible to use CSP to protect against attacks being executed from such a file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37611
- https://github.com/neos/neos-development-collection/issues/4833
- https://github.com/neos/neos-development-collection/pull/4812
- https://github.com/neos/neos-development-collection/commit/4ac0df04d2e44e164e95887b466075dde3f04045
- https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html
- https://digi.ninja/blog/svg_xss.php
- https://github.com/neos/neos-development-collection
- https://github.com/neos/neos-ui/releases/tag/8.3.4
- https://rodelllemit.medium.com/stored-xss-in-neo-cms-8-3-3-9bd1cb973c5b
