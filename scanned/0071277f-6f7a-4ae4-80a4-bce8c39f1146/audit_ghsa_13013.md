# [M] hCaptcha for EXT:form Broken Access Control vulnerability

## Summary
Severity: Medium
Advisory: GHSA-93wx-j2qv-49fg
CVE: CVE-2023-41100
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-08-23
Source: https://github.com/advisories/GHSA-93wx-j2qv-49fg
Type: github-advisory

## Affected
- Packagist: `waldhacker/hcaptcha` — affected >=0 <2.1.2

## Details
An issue was discovered in the hcaptcha (aka hCaptcha for EXT:form) extension before 2.1.2 for TYPO3. It fails to check that the required captcha field is submitted in the form data. allowing a remote user to bypass the CAPTCHA check.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41100
- https://github.com/FriendsOfPHP/security-advisories/blob/master/waldhacker/hcaptcha/CVE-2023-41100.yaml
- https://github.com/waldhacker/ext-hcaptcha
- https://typo3.org/security/advisory/typo3-ext-sa-2023-007
