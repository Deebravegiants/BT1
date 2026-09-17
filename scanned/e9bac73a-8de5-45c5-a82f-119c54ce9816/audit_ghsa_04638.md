# [H] PHP JWT Library: PBES2-HS*+A*KW unwrap accepts an unbounded p2c iteration count, enabling CPU-amplification denial of service

## Summary
Severity: High
Advisory: GHSA-3prj-6hqw-cm82
CWE: CWE-400, CWE-770
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-3prj-6hqw-cm82
Type: github-advisory

## Affected
- Packagist: `web-token/jwt-library` — affected >=0 <3.4.10
- Packagist: `web-token/jwt-framework` — affected >=0 <3.4.10
- Packagist: `web-token/jwt-library` — affected >=4.0.0 <4.0.7
- Packagist: `web-token/jwt-library` — affected >=4.1.0 <4.1.7
- Packagist: `web-token/jwt-framework` — affected >=4.0.0 <4.0.7
- Packagist: `web-token/jwt-framework` — affected >=4.1.0 <4.1.7

## Details
### Impact

When a JWE uses a password-based key-encryption algorithm (`PBES2-HS256+A128KW`, `PBES2-HS384+A192KW`, `PBES2-HS512+A256KW`), `PBES2AESKW::unwrapKey()` reads the `p2c` (PBKDF2 iteration count) parameter directly from the attacker-controlled JOSE header and passes it to `hash_pbkdf2()` with **no upper bound**. The only validation performed (`checkHeaderAdditionalParameters()`) was `is_int($p2c) && $p2c > 0`.

An unauthenticated attacker can craft a single JWE whose protected header sets a very large `p2c` (e.g. `100_000_000` ≈ 87 s of CPU, or `PHP_INT_MAX`), forcing a worker to spend an arbitrary amount of CPU inside PBKDF2 **before** the key unwrap can even fail. The decrypter swallows the eventual exception, so the attacker pays almost nothing while the server burns CPU. JSON General serialization (multiple recipients) and multi-key JWKSets multiply the cost. This is a classic uncontrolled-resource-consumption (CWE-400) denial of service.

### Affected configurations

Applications that register any `PBES2-HS*+A*KW` algorithm in their decryption `AlgorithmManager`.

### Patches

`PBES2AESKW` now enforces a configurable maximum iteration count (`DEFAULT_MAX_COUNT = 1_000_000`, well above realistic legitimate values which are a few thousand) in `checkHeaderAdditionalParameters()`, before any PBKDF2 computation. The bound is exposed as a constructor argument so operators can tune it.

### Workarounds

Before upgrading: validate/limit the `p2c` header with a custom header checker, or do not enable PBES2 algorithms for untrusted tokens.

### References

- RFC 7518 §4.8 (PBES2)
- CWE-400: Uncontrolled Resource Consumption

## Résolution

Un correctif a été préparé sur une branche dédiée basée sur `3.4.x`, avec des tests anti-régression dédiés (fork privé temporaire de cette advisory, PR #1).

**PBES2** — `PBES2AESKW::unwrapKey()` borne désormais le paramètre `p2c` (constante `DEFAULT_MAX_COUNT = 1_000_000`, configurable via le constructeur) avant tout appel à `hash_pbkdf2()`, empêchant l'amplification CPU (DoS).

**Validation :** `php -l` OK, PHPUnit vert, aucune nouvelle erreur PHPStan introduite (différentiel nul vs `3.4.x`), aucun commentaire ajouté dans le code source. Après merge, cascade prévue `3.4.x → 4.0.x → 4.1.x`.

## References
- https://github.com/web-token/jwt-framework/security/advisories/GHSA-3prj-6hqw-cm82
- https://github.com/FriendsOfPHP/security-advisories/blob/master/web-token/jwt-library/GHSA-3prj-6hqw-cm82.yaml
- https://github.com/web-token/jwt-framework
- https://github.com/web-token/jwt-framework/releases/tag/3.4.10
- https://github.com/web-token/jwt-framework/releases/tag/4.0.7
- https://github.com/web-token/jwt-framework/releases/tag/4.1.7
