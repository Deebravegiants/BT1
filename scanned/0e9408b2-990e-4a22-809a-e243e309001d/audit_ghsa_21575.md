# [M] Silverstipe CMS Stored XSS in custom meta tags

## Summary
Severity: Medium
Advisory: GHSA-pp74-g2q5-j4jf
CVE: CVE-2022-37421
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-pp74-g2q5-j4jf
Type: github-advisory

## Affected
- Packagist: `silverstripe/cms` — affected >=4.0.0 <4.11.3

## Details
A malicious content author could create a custom meta tag and execute an arbitrary JavaScript payload. This would require convincing a legitimate user to access a page and enter a custom keyboard shortcut.
This requires CMS access to exploit.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37421
- https://forum.silverstripe.org/c/releases
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/cms/CVE-2022-37421.yaml
- https://www.silverstripe.org/blog/tag/release
- https://www.silverstripe.org/download/security-releases
- https://www.silverstripe.org/download/security-releases/cve-2022-37421
