# [M] Smarty Path Traversal Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-65j5-vpm7-6xp4
CVE: CVE-2018-16831
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-65j5-vpm7-6xp4
Type: github-advisory

## Affected
- Packagist: `smarty/smarty` — affected >=0 <3.1.33

## Details
Smarty before 3.1.33-dev-4 allows attackers to bypass the trusted_dir protection mechanism via a `file:./../` substring in an include statement.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16831
- https://github.com/smarty-php/smarty/issues/486
- https://github.com/smarty-php/smarty/commit/f9ca3c63d1250bb56b2bda609dcc9dd81f0065f8
- https://github.com/FriendsOfPHP/security-advisories/blob/master/smarty/smarty/CVE-2018-16831.yaml
- https://github.com/smarty-php/smarty
