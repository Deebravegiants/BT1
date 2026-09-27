# [M] Composer vulnerable to ANSI sequence injection

## Summary
Severity: Medium
Advisory: BIT-composer-2025-67746
Aliases: CVE-2025-67746, GHSA-59pp-r3rg-353g
Ecosystem: Bitnami
Published: 2026-01-08
Source: https://osv.dev/vulnerability/BIT-composer-2025-67746
Type: osv

## Affected
- Bitnami: `composer` — affected >=2.3.0 <2.9.3

## Details
Composer is a dependency manager for PHP. In versions on the 2.x branch prior to 2.2.26 and 2.9.3, attackers controlling remote sources that Composer downloads from might in some way inject ANSI control characters in the terminal output of various Composer commands, causing mangled output and potentially leading to confusion or DoS of the terminal application. There is no proven exploit and this has thus a low severity but we still publish a CVE as it has potential for abuse, and we want to be on the safe side informing users that they should upgrade. Versions 2.2.26 and 2.9.3 contain a patch for the issue.

## References
- https://github.com/composer/composer/commit/1d40a95c9d39a6b7f80d404ab30336c586da9917
- https://github.com/composer/composer/commit/5db1876a76fdef76d3c4f8a27995c434c7a43e71
- https://github.com/composer/composer/releases/tag/2.2.26
- https://github.com/composer/composer/releases/tag/2.9.3
- https://github.com/composer/composer/security/advisories/GHSA-59pp-r3rg-353g
- https://nvd.nist.gov/vuln/detail/CVE-2025-67746
