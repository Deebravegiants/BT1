# [H] Symfony Host Header Injection

## Summary
Severity: High
Advisory: GHSA-66p6-7p29-55p9
CVE: CVE-2018-14774
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-66p6-7p29-55p9
Type: github-advisory

## Affected
- Packagist: `symfony/symfony` — affected >=2.7.0 <2.7.49
- Packagist: `symfony/symfony` — affected >=2.8.0 <2.8.44
- Packagist: `symfony/symfony` — affected >=3.3.0 <3.3.18
- Packagist: `symfony/symfony` — affected >=3.4.0 <3.4.14
- Packagist: `symfony/symfony` — affected >=4.0.0 <4.0.14
- Packagist: `symfony/symfony` — affected >=4.1.0 <4.1.3

## Details
An issue was discovered in HttpKernel in Symfony 2.7.0 through 2.7.48, 2.8.0 through 2.8.43, 3.3.0 through 3.3.17, 3.4.0 through 3.4.13, 4.0.0 through 4.0.13, and 4.1.0 through 4.1.2. When using HttpCache, the values of the X-Forwarded-Host headers are implicitly set as trusted while this should be forbidden, leading to potential host header injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14774
- https://github.com/symfony/symfony/commit/725dee4cd8b4ccd52e335ae4b4522242cea9bd4a
- https://github.com/symfony/symfony/commit/7f912bbb78377c2ea331b3da28363435fbd91337
- https://github.com/symfony/symfony/commit/96504fb8c9f91204727d2930eb837473ce154956
- https://github.com/symfony/symfony/commit/974240e178bb01d734bf1df1ad5c3beba6a2f982
- https://github.com/symfony/symfony/commit/9cfcaba0bf71f87683510b5f47ebaac5f5d6a5ba
- https://github.com/symfony/symfony/commit/bcf5897bb1a99d4acae8bf7b73e81bfdeaac0922
- https://github.com/symfony/symfony
- https://symfony.com/blog/cve-2018-14774-possible-host-header-injection-when-using-httpcache
