# [M] Symfony Path Disclosure

## Summary
Severity: Medium
Advisory: GHSA-x3cf-w64x-4cp2
CVE: CVE-2018-19789
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-x3cf-w64x-4cp2
Type: github-advisory

## Affected
- Packagist: `symfony/symfony` — affected >=2.7.0 <2.7.50
- Packagist: `symfony/symfony` — affected >=2.8.0 <2.8.49
- Packagist: `symfony/symfony` — affected >=3.0.0 <3.4.20
- Packagist: `symfony/symfony` — affected >=4.0.0 <4.0.15
- Packagist: `symfony/symfony` — affected >=4.1.0 <4.1.9
- Packagist: `symfony/symfony` — affected >=4.2.0 <4.2.1
- Packagist: `symfony/form` — affected >=2.7.0 <2.7.50
- Packagist: `symfony/form` — affected >=2.8.0 <2.8.49
- Packagist: `symfony/form` — affected >=3.0.0 <3.4.20
- Packagist: `symfony/form` — affected >=4.0.0 <4.0.15
- Packagist: `symfony/form` — affected >=4.1.0 <4.1.9
- Packagist: `symfony/form` — affected >=4.2.0 <4.2.1

## Details
An issue was discovered in Symfony 2.7.x before 2.7.50, 2.8.x before 2.8.49, 3.x before 3.4.20, 4.0.x before 4.0.15, 4.1.x before 4.1.9, and 4.2.x before 4.2.1. When using the scalar type hint `string` in a setter method (e.g. `setName(string $name)`) of a class that's the `data_class` of a form, and when a file upload is submitted to the corresponding field instead of a normal text input, then `UploadedFile::__toString()` is called which will then return and disclose the path of the uploaded file. If combined with a local file inclusion issue in certain circumstances this could escalate it to a Remote Code Execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19789
- https://github.com/symfony/symfony/commit/b65e6f1a47b68f2713b60cdac9cc3a4af62a2d1c
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/form/CVE-2018-19789.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2018-19789.yaml
- https://github.com/symfony/symfony
- https://lists.debian.org/debian-lts-announce/2019/03/msg00009.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4TD3E7FZIXLVFG3SMFJPDEKPZ26TJOW7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JZMRJ7VTHCY5AZK24G4QGX36RLUDTDKE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OA4WVFN5FYPIXAPLWZI6N425JHHDSWAZ
- https://seclists.org/bugtraq/2019/May/21
- https://symfony.com/blog/cve-2018-19789-disclosure-of-uploaded-files-full-path
- https://symfony.com/cve-2018-19789
- https://web.archive.org/web/20210124224817/http://www.securityfocus.com/bid/106249
- https://www.debian.org/security/2019/dsa-4441
