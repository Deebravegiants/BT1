# [H] Composer: Arbitrary file write outside vendor via malicious transitive package name

## Summary
Severity: High
Advisory: GHSA-499r-g7pc-vmp9
CVE: CVE-2026-59948
CWE: CWE-22, CWE-787
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-499r-g7pc-vmp9
Type: github-advisory

## Affected
- Packagist: `composer/composer` — affected >=2.3.0 <2.10.2
- Packagist: `composer/composer` — affected >=1.0.0 <2.2.29

## Details
## Summary

A maliciously crafted package, published on an untrusted third party repository other than Packagist.org or Private Packagist, can cause Composer to write files outside the `vendor/` directory and outside your project, with attacker-controlled content, during a normal `install` or `update` through using an invalid package name, which was not correctly validated by Composer.

This is an arbitrary file write that can be used to execute code outside the Composer project's context in which you expected the package code to execute (for example by writing shell startup files, SSH `authorized_keys`, or a cron entry). It is a supply-chain issue: it requires a malicious or compromised package to be present in the dependency graph, it is not otherwise remotely exploitable against a machine.

The fix makes Composer validate every package produced by dependency resolution before anything is written to `composer.lock` or installed, and abort with a security error if a package name is not a valid `vendor/package` name.

## Am I affected?

You may be affected if you install packages from an untrusted third party repository, which does not sufficiently validate package names. Packagist.org and Private Packagist are safe, as they validate package names correctly.

## Patched versions

Fixed in **2.2.29** and **2.10.2**. Composer 1.x is also affected and you should move to a safe 2.x release.

## Workarounds

Do not use untrusted package repositories. If you have to, mirror them through an internal repository like Private Packagist.

## References
- https://github.com/composer/composer/security/advisories/GHSA-499r-g7pc-vmp9
- https://nvd.nist.gov/vuln/detail/CVE-2026-59948
- https://github.com/composer/composer/commit/502c6c4f699802d9cf464728b3e8a95674f919a0
- https://github.com/composer/composer/commit/c50b1efd13ebd73f6dca19b31424c5a02bf93cc1
- https://github.com/composer/composer
- https://github.com/composer/composer/releases/tag/2.10.2
- https://github.com/composer/composer/releases/tag/2.2.29
