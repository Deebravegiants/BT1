# [H] Composer: Perforce source URL permits P4PORT `rsh:` command execution

## Summary
Severity: High
Advisory: BIT-composer-2026-84361
Aliases: CVE-2026-84361, GHSA-rvx4-ffvw-m9q3
Ecosystem: Bitnami
Published: 2026-09-07
Source: https://osv.dev/vulnerability/BIT-composer-2026-84361
Type: osv

## Affected
- Bitnami: `composer` — affected >=2.3.0 <2.10.3

## Details
Composer is a dependency Manager for the PHP language. From 1.0 until 2.2.30 and 2.10.3, a malicious dependency package from a custom Composer repository or an untrusted composer.lock file could set source.type to perforce and source.url to an rsh: or jsh: P4PORT value. When the Perforce p4 client was installed and Composer installed the package from source through composer install or composer update, including --prefer-source, Composer\Util\Perforce passed the address to p4 without validation, causing p4 to run a local command with the privileges of the user or CI account. Packagist.org does not permit Perforce source metadata. This issue is fixed in versions 2.2.30 and 2.10.3.

## References
- https://github.com/composer/composer/commit/0aac50528e83ed635cf788333635897469440220
- https://github.com/composer/composer/commit/199ad81a9cc6a2a5164ad79a8da26b2e19e521af
- https://github.com/composer/composer/releases/tag/2.10.3
- https://github.com/composer/composer/releases/tag/2.2.30
- https://github.com/composer/composer/security/advisories/GHSA-rvx4-ffvw-m9q3
- https://nvd.nist.gov/vuln/detail/CVE-2026-84361
