# [C] Contao Does Not Invalidate Existing Sessions When Password Changes

## Summary
Severity: Critical
Advisory: GHSA-vcgg-hp4r-87gx
CVE: CVE-2019-10641
CWE: CWE-640
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-vcgg-hp4r-87gx
Type: github-advisory

## Affected
- Packagist: `contao/contao` — affected >=4.0.0 <4.4.37
- Packagist: `contao/contao` — affected >=4.5.0 <4.7.3
- Packagist: `contao/core-bundle` — affected >=4.0.0 <4.4.37
- Packagist: `contao/core-bundle` — affected >=4.5.0 <4.7.3
- Packagist: `contao/core` — affected >=3.0.0 <3.5.39

## Details
Security researcher Ali Razzaq has discovered that existing sessions are not correctly invalidated when a user changes their password in the backend or frontend.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10641
- https://github.com/contao/contao/commit/74c7dfafa0dfa5363a9463b486522d5d526e28fe
- https://github.com/contao/contao/commit/b92e27bc7c9e59226077937f840c74ffd0f672e8
- https://github.com/contao/core/commit/119a1b5bd9e62d27ca2838727084d04f3b7fcd32
- https://contao.org/en/news/security-vulnerability-cve-2019-10641.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/contao/CVE-2019-10641.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/core-bundle/CVE-2019-10641.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/core/CVE-2019-10641.yaml
