# [H] Composer Remote Code Execution vulnerability via web-accessible composer.phar

## Summary
Severity: High
Advisory: GHSA-jm6m-4632-36hf
CVE: CVE-2023-43655
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-29
Source: https://github.com/advisories/GHSA-jm6m-4632-36hf
Type: github-advisory

## Affected
- Packagist: `composer/composer` — affected >=0 <1.10.27
- Packagist: `composer/composer` — affected >=2.0.0 <2.2.22
- Packagist: `composer/composer` — affected >=2.3.0 <2.6.4

## Details
### Impact

Users publishing a composer.phar to a public web-accessible server where the composer.phar can be executed as a php file may be impacted if PHP also has `register_argc_argv` enabled in php.ini.

### Patches

2.6.4, 2.2.22 and 1.10.27 patch this vulnerability.

### Workarounds

Make sure `register_argc_argv` is disabled in php.ini, and avoid publishing composer.phar to the web as this really should not happen.

## References
- https://github.com/composer/composer/security/advisories/GHSA-jm6m-4632-36hf
- https://nvd.nist.gov/vuln/detail/CVE-2023-43655
- https://github.com/composer/composer/commit/4fce14795aba98e40b6c4f5047305aba17a6120d
- https://github.com/composer/composer/commit/955a48e6319c8962e5cd421b07c00ab3c728968c
- https://github.com/composer/composer/commit/95e091c921037b7b6564942845e7b738f6b95c9c
- https://github.com/composer/composer
- https://lists.debian.org/debian-lts-announce/2024/03/msg00030.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/66H2WKFUO255T3BZTL72TNYJYH2XM5FG
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7AWYAUZNH565NWPIKGEIYBWHYNM5JGAE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KFOPGPW2KS37O3KJWBRGTUWHTXCQXBS2
