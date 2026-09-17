# [M] Composer: Path traversal in package bin field lets dependencies chmod arbitrary host files

## Summary
Severity: Medium
Advisory: BIT-composer-2026-59946
Aliases: CVE-2026-59946, GHSA-gjfg-22fp-rrxx
Ecosystem: Bitnami
Published: 2026-07-14
Source: https://osv.dev/vulnerability/BIT-composer-2026-59946
Type: osv

## Affected
- Bitnami: `composer` — affected >=2.3.0 <2.10.2

## Details
Composer is a dependency Manager for the PHP language. Prior to 2.2.29 and 2.10.2, a Composer package bin entry containing .. path segments can resolve outside the package install directory and cause Composer's binary installation flow to chmod an existing host file to a world-readable and world-executable mode during composer install, update, or require. This issue is fixed in versions 2.2.29 and 2.10.2.

## References
- https://github.com/composer/composer/commit/502c6c4f699802d9cf464728b3e8a95674f919a0
- https://github.com/composer/composer/commit/c50b1efd13ebd73f6dca19b31424c5a02bf93cc1
- https://github.com/composer/composer/releases/tag/2.10.2
- https://github.com/composer/composer/releases/tag/2.2.29
- https://github.com/composer/composer/security/advisories/GHSA-gjfg-22fp-rrxx
- https://nvd.nist.gov/vuln/detail/CVE-2026-59946
