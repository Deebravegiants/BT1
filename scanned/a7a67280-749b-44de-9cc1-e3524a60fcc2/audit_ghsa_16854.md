# [M] mdanter/ecc affected by timing vulnerability in cryptographic side-channels

## Summary
Severity: Medium
Advisory: GHSA-3494-cfwf-56hw
CVE: CVE-2024-33851
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-04-28
Source: https://github.com/advisories/GHSA-3494-cfwf-56hw
Type: github-advisory

## Affected
- Packagist: `paragonie/ecc` — affected >=0 <2.0.1
- Packagist: `mdanter/ecc` — affected >=0

## Details
phpecc, as used in **all versions** of mdanter/ecc, as well as paragonie/ecc before 2.0.1, has a branch-based timing leak in Point addition. (This Composer package is also known as phpecc/phpecc on GitHub, previously known as the Matyas Danter ECC library.)

Paragon Initiative Enterprises [hard-forked phpecc/phpecc](https://github.com/phpecc/phpecc/issues/289) and discovered the issue in the original code, then released v2.0.1 which fixes the vulnerability. [The upstream code](https://github.com/phpecc/phpecc) is no longer maintained and remains vulnerable for all versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-33851
- https://github.com/phpecc/phpecc/issues/289
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mdanter/ecc/CVE-2024-33851.yaml
- https://github.com/paragonie/phpecc/releases/tag/v2.0.0
- https://github.com/paragonie/phpecc/releases/tag/v2.0.1
