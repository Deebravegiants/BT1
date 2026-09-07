# [M] frp_form_answers allows Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-q3r2-23r8-wqr9
CVE: CVE-2023-26091
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-26
Source: https://github.com/advisories/GHSA-q3r2-23r8-wqr9
Type: github-advisory

## Affected
- Packagist: `frappant/frp-form-answers` — affected >=0 <3.1.2
- Packagist: `frappant/frp-form-answers` — affected >=4.0.0 <4.0.2

## Details
The frp_form_answers (aka Forms Export) extension before 3.1.2, and 4.x before 4.0.2, for TYPO3 allows XSS via saved emails.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26091
- https://github.com/frappant/frp_form_answers/commit/39fa16c8c792abdfc33e38bae17847364ff6a71d
- https://github.com/FriendsOfPHP/security-advisories/blob/master/frappant/frp-form-answers/CVE-2023-26091.yaml
- https://github.com/frappant/frp_form_answers
- https://typo3.org/help/security-advisories
- https://typo3.org/security/advisory/typo3-ext-sa-2023-002
