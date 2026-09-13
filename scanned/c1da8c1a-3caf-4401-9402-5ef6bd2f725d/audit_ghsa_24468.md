# [M] Symfony SSRF Vulnerability via Form Component

## Summary
Severity: Medium
Advisory: GHSA-cqqh-94r6-wjrg
CVE: CVE-2017-16790
CWE: CWE-20, CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-cqqh-94r6-wjrg
Type: github-advisory

## Affected
- Packagist: `symfony/form` — affected >=2.7.0 <2.7.38
- Packagist: `symfony/form` — affected >=2.8.0 <2.8.31
- Packagist: `symfony/form` — affected >=3.0.0 <3.2.14
- Packagist: `symfony/form` — affected >=3.3.0 <3.3.13
- Packagist: `symfony/symfony` — affected >=2.7.0 <2.7.38
- Packagist: `symfony/symfony` — affected >=2.8.0 <2.8.31
- Packagist: `symfony/symfony` — affected >=3.0.0 <3.2.14
- Packagist: `symfony/symfony` — affected >=3.3.0 <3.3.13

## Details
An issue was discovered in Symfony before 2.7.38, 2.8.31, 3.2.14, 3.3.13, 3.4-BETA5, and 4.0-BETA5. When a form is submitted by the user, the request handler classes of the Form component merge POST data and uploaded files data into one array. This big array forms the data that are then bound to the form. At this stage there is no difference anymore between submitted POST data and uploaded files. A user can send a crafted HTTP request where the value of a "FileType" is sent as normal POST data that could be interpreted as a local file path on the server-side (for example, "file:///etc/passwd"). If the application did not perform any additional checks about the value submitted to the "FileType", the contents of the given file on the server could have been exposed to the attacker.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16790
- https://github.com/symfony/symfony/pull/24993
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/form/CVE-2017-16790.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2017-16790.yaml
- https://github.com/symfony/form
- https://symfony.com/blog/cve-2017-16790-ensure-that-submitted-data-are-uploaded-files
- https://symfony.com/cve-2017-16790
- https://www.debian.org/security/2018/dsa-4262
