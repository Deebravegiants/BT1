# [H] PHP JWT Framework: JWSVerifier uses algorithm from unprotected header, enabling algorithm confusion attacks

## Summary
Severity: High
Advisory: GHSA-jc38-x7x8-2xc8
CWE: CWE-345
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-jc38-x7x8-2xc8
Type: github-advisory

## Affected
- Packagist: `web-token/jwt-library` — affected >=0 <3.4.10
- Packagist: `web-token/jwt-library` — affected >=4.0.0 <4.0.7
- Packagist: `web-token/jwt-library` — affected >=4.1.0 <4.1.7
- Packagist: `web-token/jwt-bundle` — affected >=0 <3.4.10
- Packagist: `web-token/jwt-bundle` — affected >=4.0.0 <4.0.7
- Packagist: `web-token/jwt-bundle` — affected >=4.1.0 <4.1.7
- Packagist: `web-token/jwt-experimental` — affected >=0 <3.4.10
- Packagist: `web-token/jwt-experimental` — affected >=4.0.0 <4.0.7
- Packagist: `web-token/jwt-experimental` — affected >=4.1.0 <4.1.7
- Packagist: `web-token/jwt-framework` — affected >=0 <3.4.10
- Packagist: `web-token/jwt-framework` — affected >=4.0.0 <4.0.7
- Packagist: `web-token/jwt-framework` — affected >=4.1.0 <4.1.7

## Details
## Summary

`JWSVerifier::getAlgorithm()` in `src/Library/Signature/JWSVerifier.php` (line 144) merges protected and unprotected headers using PHP's spread operator:

```php
$completeHeader = [...$signature->getProtectedHeader(), ...$signature->getHeader()];
```

In PHP, when spreading arrays with duplicate string keys, the **last array's values take precedence**. Since the unprotected header (`getHeader()`) is spread second, an attacker can override the integrity-protected `alg` parameter by placing a different value in the unprotected header.

This creates a Time-of-Check/Time-of-Use (TOCTOU) vulnerability:
1. `HeaderCheckerManager` validates `alg` from the **protected** header
2. `JWSVerifier` uses `alg` from the **unprotected** header for actual verification

The same issue exists in `JWEDecrypter.php` (lines 120-124) where `array_merge()` exhibits the same last-wins behavior for `alg` and `enc`.

## Affected Code

**JWSVerifier.php line 144** — Spread operator merge order allows unprotected header to override `alg`:
```php
$completeHeader = [...$signature->getProtectedHeader(), ...$signature->getHeader()];
```

**JWEDecrypter.php lines 120-124** — `array_merge()` with same last-wins behavior:
```php
$completeHeader = array_merge(
    $jwe->getSharedProtectedHeader(),
    $jwe->getSharedHeader(),
    $recipient->getHeader()
);
```

## Attack Vectors

### Vector A — Mixed key sets (HIGH probability)
If the application uses a JWKSet containing keys of different types (common in multi-tenant or federation scenarios), the JWSVerifier iterates all keys (line 86). An attacker can force a different algorithm that matches a different key in the set.

### Vector B — alg ONLY in unprotected header (HIGH probability)
If `alg` is placed EXCLUSIVELY in the unprotected header (not in the protected header at all), `HeaderCheckerManager::checkDuplicatedHeaderParameters()` does NOT trigger. The JSON Flattened/General serializers allow tokens with no protected header or a protected header without `alg`. RFC 7515 Section 4.1.1 states `alg` MUST be integrity-protected, but the library does not enforce this.

### Vector C — Direct JWSVerifier usage (HIGH probability)
`JWSLoader` takes `?HeaderCheckerManager` (nullable). If developers use `JWSVerifier` directly or create `JWSLoader` without a `HeaderCheckerManager`, the duplicate header check never runs.

## Contrast with JWSBuilder (safe)

`JWSBuilder::findSignatureAlgorithm()` (line 196) uses `[...$header, ...$protectedHeader]` where protected wins. It also has `checkDuplicatedHeaderParameters()` (line 218). The JWSVerifier has **neither** safeguard.

## Proof of Concept

```php
<?php
// Demonstrate algorithm override via unprotected header
$protected = ["alg" => "RS256", "typ" => "JWT"];
$unprotected = ["alg" => "HS256"];
$merged = [...$protected, ...$unprotected];
// $merged["alg"] === "HS256" — unprotected wins!

// JSON Flattened JWS with algorithm override:
$maliciousJws = json_encode([
    'payload' => base64url_encode($payload),
    'protected' => base64url_encode('{"alg":"RS256"}'),
    'header' => ['alg' => 'HS256'],  // OVERRIDE
    'signature' => base64url_encode($sig),
]);
// HeaderCheckerManager validates RS256 from protected header -> PASS
// JWSVerifier uses HS256 from unprotected header -> attacker's algorithm choice
```

A full working PoC demonstrating HS512-to-HS256 downgrade with mixed keysets is available upon request.

## Suggested Fix

In `JWSVerifier::getAlgorithm()`, read `alg` exclusively from the protected header:

```php
private function getAlgorithm(Signature $signature): Algorithm
{
    $protectedHeader = $signature->getProtectedHeader();
    if (! isset($protectedHeader['alg'])) {
        throw new InvalidArgumentException('The "alg" parameter must be in the protected header.');
    }
    return $this->signatureAlgorithmManager->get($protectedHeader['alg']);
}
```

For `JWEDecrypter`, reverse the merge order so protected header wins, or extract `alg`/`enc` exclusively from the protected header.

## Résolution

Un correctif a été préparé sur une branche dédiée basée sur `3.4.x`, avec des tests anti-régression dédiés (fork privé temporaire de cette advisory, PR #1).

**JWS algorithm confusion** — `JWSVerifier` lit le paramètre `alg` exclusivement dans le header protégé en intégrité (RFC 7515 §4.1.1) ; un `alg` placé dans le header non protégé ne peut plus surcharger l'algorithme signé.

**Validation :** `php -l` OK, PHPUnit vert, aucune nouvelle erreur PHPStan introduite (différentiel nul vs `3.4.x`), aucun commentaire ajouté dans le code source. Après merge, cascade prévue `3.4.x → 4.0.x → 4.1.x`.

## References
- https://github.com/web-token/jwt-framework/security/advisories/GHSA-jc38-x7x8-2xc8
- https://github.com/FriendsOfPHP/security-advisories/blob/master/web-token/jwt-library/GHSA-jc38-x7x8-2xc8.yaml
- https://github.com/web-token/jwt-framework
