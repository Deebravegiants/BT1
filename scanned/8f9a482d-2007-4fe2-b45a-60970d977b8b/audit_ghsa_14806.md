# [M] FriendlyCaptcha Plugin for TYPO3 Captcha Check Bypass

## Summary
Severity: Medium
Advisory: GHSA-jg62-h7pv-hxgv
CVE: CVE-2024-38873
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-06-21
Source: https://github.com/advisories/GHSA-jg62-h7pv-hxgv
Type: github-advisory

## Affected
- Packagist: `studiomitte/friendlycaptcha` — affected >=0 <0.1.4

## Details
An issue was discovered in the friendlycaptcha_official (aka Integration of Friendly Captcha) extension before 0.1.4 for TYPO3. The extension fails to check the requirement of the captcha field in submitted form data, allowing a remote user to bypass the captcha check. This only affects the captcha integration for the ext:form extension.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38873
- https://github.com/FriendsOfPHP/security-advisories/blob/master/studiomitte/friendlycaptcha/CVE-2024-38873.yaml
- https://github.com/studiomitte/friendlycaptcha-typo3
- https://typo3.org/security/advisory/typo3-ext-sa-2024-004
