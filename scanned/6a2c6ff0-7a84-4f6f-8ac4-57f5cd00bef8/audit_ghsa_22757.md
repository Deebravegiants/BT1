# [C] Contao Does Not Expire Tokens Correctly

## Summary
Severity: Critical
Advisory: GHSA-j99g-qjvx-995g
CVE: CVE-2019-10643
CWE: CWE-287, CWE-324
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-j99g-qjvx-995g
Type: github-advisory

## Affected
- Packagist: `contao/contao` — affected >=4.7.0 <4.7.3
- Packagist: `contao/core-bundle` — affected >=4.7.0 <4.7.3

## Details
Security researcher Ali Razzaq has discovered that confirming an opt-in token does not invalidate previous opt-in tokens in Contao 4.7.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10643
- https://github.com/contao/contao/commit/70348cc812b110831ad66a4f9857883f75649b88
- https://contao.org/en/news.html
- https://contao.org/en/news/security-vulnerability-cve-2019-10643.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/contao/CVE-2019-10643.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/core-bundle/CVE-2019-10643.yaml
