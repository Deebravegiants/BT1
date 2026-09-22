# [H] Composer has multiple command injections via malicious git/hg branch names

## Summary
Severity: High
Advisory: GHSA-v9qv-c7wm-wgmf
CVE: CVE-2024-35242
CWE: CWE-77
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-10
Source: https://github.com/advisories/GHSA-v9qv-c7wm-wgmf
Type: github-advisory

## Affected
- Packagist: `composer/composer` — affected >=2.0 <2.2.24
- Packagist: `composer/composer` — affected >=2.3 <2.7.7

## Details
### Impact

The `composer install` command running inside a git/hg repository which has specially crafted branch names can lead to command injection. So this requires cloning untrusted repositories.

### Patches

2.2.24 for 2.2 LTS or 2.7.7 for mainline

### Workarounds

Avoid cloning potentially compromised repositories.

## References
- https://github.com/composer/composer/security/advisories/GHSA-v9qv-c7wm-wgmf
- https://nvd.nist.gov/vuln/detail/CVE-2024-35242
- https://github.com/composer/composer/commit/6bd43dff859c597c09bd03a7e7d6443822d0a396
- https://github.com/composer/composer/commit/fc57b93603d7d90b71ca8ec77b1c8a9171fdb467
- https://github.com/composer/composer
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PO4MU2BC7VR6LMHEX4X7DKGHVFXZV2MC
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VLPJHM2WWSYU2F6KHW2BYFGYL4IGTKHC
