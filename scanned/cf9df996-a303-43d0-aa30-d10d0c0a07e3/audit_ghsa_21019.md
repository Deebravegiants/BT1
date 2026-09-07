# [H] Twig may load a template outside a configured directory when using the filesystem loader

## Summary
Severity: High
Advisory: GHSA-52m2-vc4m-jj33
CVE: CVE-2022-39261
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-30
Source: https://github.com/advisories/GHSA-52m2-vc4m-jj33
Type: github-advisory

## Affected
- Packagist: `twig/twig` — affected >=1.0.0 <1.44.7
- Packagist: `twig/twig` — affected >=2.0.0 <2.15.3
- Packagist: `twig/twig` — affected >=3.0.0 <3.4.3

## Details
# Description

When using the filesystem loader to load templates for which the name is a user input, it is possible to use the `source` or `include` statement to read arbitrary files from outside the templates directory when using a namespace like `@somewhere/../some.file` (in such a case, validation is bypassed).

# Resolution

We fixed validation for such template names.

Even if the 1.x branch is not maintained anymore, a new version has been released.

# Credits

We would like to thank Dariusz Tytko for reporting the issue and Fabien Potencier for fixing the issue.

## References
- https://github.com/twigphp/Twig/security/advisories/GHSA-52m2-vc4m-jj33
- https://nvd.nist.gov/vuln/detail/CVE-2022-39261
- https://github.com/twigphp/Twig/commit/35f3035c5deb0041da7b84daf02dea074ddc7a0b
- https://github.com/FriendsOfPHP/security-advisories/blob/master/twig/twig/CVE-2022-39261.yaml
- https://github.com/twigphp/Twig
- https://lists.debian.org/debian-lts-announce/2022/10/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2OKRUHPVLIQVFPPJ2UWC3WV3WQO763NR
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AUVTXMNPSZAHS3DWZEM56V5W4NPVR6L7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NWRFPZSR74SYVJKBTKTMYUK36IJ3SQJP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TW53TFJ6WWNXMUHOFACKATJTS7NIHVQE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WV5TNNJLGG536TJH6DLCIAAZZIPV2GUD
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YU4ZYX62H2NUAKKGUES4RZIM4KMTKZ7F
- https://symfony.com/blog/twig-security-release-possibility-to-load-a-template-outside-a-configured-directory-when-using-the-filesystem-loader
- https://www.debian.org/security/2022/dsa-5248
- https://www.drupal.org/sa-core-2022-016
