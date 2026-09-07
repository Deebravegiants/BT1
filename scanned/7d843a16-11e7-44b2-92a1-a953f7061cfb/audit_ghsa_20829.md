# [M] Smarty Cross-site Scripting vulnerability in pages that use smarty_function_mailto

## Summary
Severity: Medium
Advisory: GHSA-hwq7-5vv9-c6cf
CVE: CVE-2018-25047
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-hwq7-5vv9-c6cf
Type: github-advisory

## Affected
- Packagist: `smarty/smarty` — affected >=0 <3.1.47
- Packagist: `smarty/smarty` — affected >=4.0.0 <4.2.1

## Details
In Smarty before 3.1.47 and 4.x before 4.2.1, `libs/plugins/function.mailto.php` allows cross-site scripting. A web page that uses `smarty_function_mailto`, and that could be parameterized using GET or POST input parameters, could allow injection of JavaScript code by a user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25047
- https://github.com/smarty-php/smarty/issues/454
- https://github.com/smarty-php/smarty/commit/55ea25d1f50f0406fb1ccedd212c527977793fc9
- https://bugs.gentoo.org/870100
- https://github.com/FriendsOfPHP/security-advisories/blob/master/smarty/smarty/CVE-2018-25047.yaml
- https://github.com/smarty-php/smarty
- https://github.com/smarty-php/smarty/releases/tag/v3.1.47
- https://github.com/smarty-php/smarty/releases/tag/v4.2.1
- https://lists.debian.org/debian-lts-announce/2023/01/msg00002.html
- https://lists.debian.org/debian-lts-announce/2024/11/msg00013.html
- https://security.gentoo.org/glsa/202209-09
