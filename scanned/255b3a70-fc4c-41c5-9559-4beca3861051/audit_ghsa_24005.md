# [C] Contao SQL injection in the file manager

## Summary
Severity: Critical
Advisory: GHSA-vq59-x6mq-4wgw
CVE: CVE-2019-11512
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vq59-x6mq-4wgw
Type: github-advisory

## Affected
- Packagist: `contao/contao` — affected >=4.1.0 <4.4.39
- Packagist: `contao/contao` — affected >=4.5.0 <4.7.5
- Packagist: `contao/core-bundle` — affected >=4.1.0 <4.4.39
- Packagist: `contao/core-bundle` — affected >=4.5.0 <4.7.5

## Details
David Wind, penetration tester with A1 Digital, has discovered that the SQL injection vulnerability originally published under CVE-2017-16558 can still be exploited in the file manager in Contao 4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11512
- https://github.com/contao/contao/commit/87d92f823b08b91a0aeb522284537c8afcdb8aba
- https://contao.org/en/news/security-vulnerability-cve-2019-11512.html
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/contao/CVE-2019-11512.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/contao/core-bundle/CVE-2019-11512.yaml
