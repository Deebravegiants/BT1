# [H] Composer has a command injection via malicious git branch name

## Summary
Severity: High
Advisory: GHSA-47f6-5gq3-vx9c
CVE: CVE-2024-35241
CWE: CWE-77
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-10
Source: https://github.com/advisories/GHSA-47f6-5gq3-vx9c
Type: github-advisory

## Affected
- Packagist: `composer/composer` — affected >=2.0 <2.2.24
- Packagist: `composer/composer` — affected >=2.3 <2.7.7

## Details
### Impact

The `status`, `reinstall` and `remove` commands with packages installed from source via git containing specially crafted branch names in the repository can be used to execute code.

### Patches

2.2.24 for 2.2 LTS or 2.7.7 for mainline

### Workarounds

Avoid installing dependencies via git by using `--prefer-dist` or the `preferred-install: dist` config setting.

## References
- https://github.com/composer/composer/security/advisories/GHSA-47f6-5gq3-vx9c
- https://nvd.nist.gov/vuln/detail/CVE-2024-35241
- https://github.com/composer/composer/commit/b93fc6ca437da35ae73d667d0618749c763b67d4
- https://github.com/composer/composer/commit/ee28354ca8d33c15949ad7de2ce6656ba3f68704
- https://github.com/composer/composer
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PO4MU2BC7VR6LMHEX4X7DKGHVFXZV2MC
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VLPJHM2WWSYU2F6KHW2BYFGYL4IGTKHC
- https://www.vicarius.io/vsociety/posts/cve-2024-35241-detect-composer-vulnerability
- https://www.vicarius.io/vsociety/posts/cve-2024-35241-mitigate-vulnerable-composer
