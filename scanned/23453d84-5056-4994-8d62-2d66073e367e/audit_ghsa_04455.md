# [M] PHP JWT Library: RSA1_5 (RSAES-PKCS1-v1_5) decryption lacks implicit rejection, exposing a Bleichenbacher/Marvin padding oracle

## Summary
Severity: Medium
Advisory: GHSA-5739-39v2-5754
CWE: CWE-208, CWE-385
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-5739-39v2-5754
Type: github-advisory

## Affected
- Packagist: `web-token/jwt-library` — affected >=0 <3.4.10
- Packagist: `web-token/jwt-library` — affected >=4.0.0 <4.0.7
- Packagist: `web-token/jwt-library` — affected >=4.1.0 <4.1.7

## Details
### Impact

`RSACrypt::decryptWithRSA15()` (used by the `RSA1_5` key-encryption algorithm) implements RSAES-PKCS1-v1_5 decryption by inspecting the padding after RSADP and throwing `InvalidArgumentException` as soon as the padding is malformed. It does **not** implement the implicit-rejection countermeasure required by RFC 3447 §7.2.2 / RFC 8017 §7.1.2 (return a deterministic pseudo-random value of the expected length on padding failure and let the downstream step fail uniformly).

From a JWE caller this yields a Bleichenbacher/Marvin padding oracle: an attacker submitting adaptively crafted `encrypted_key` values can distinguish (a) padding rejected, (b) padding valid but wrong CEK length, and (c) padding valid and full AEAD executed — even though `JWEDecrypter` returns the same `false` in all cases — because each path performs a measurably different amount of work, amplifiable by enlarging the ciphertext (CWE-208 timing side channel). Enough adaptive queries can recover the wrapped CEK.

### Affected configurations

Applications that register `RSA1_5` in their decryption `AlgorithmManager` and hold an RSA private key.

### Patches

PKCS#1 v1.5 decryption now performs implicit rejection: on invalid padding (or unexpected recovered length) it returns a random CEK of the expected size selected in constant time, so the full content-decryption (AEAD) step always runs and fails uniformly, removing the observable difference between padding-valid and padding-invalid ciphertexts. Users are still strongly encouraged to migrate to `RSA-OAEP`.

### Workarounds

Prefer `RSA-OAEP`/`RSA-OAEP-256`; do not enable `RSA1_5` for untrusted tokens.

### References

- RFC 3447 §7.2.2 / RFC 8017 §7.1.2
- Bleichenbacher (1998); Marvin attack
- CWE-208: Observable Timing Discrepancy

## Résolution

Un correctif a été préparé sur une branche dédiée basée sur `3.4.x`, avec des tests anti-régression dédiés (fork privé temporaire de cette advisory, PR #1).

**RSA1_5** — déchiffrement PKCS#1 v1.5 avec *implicit rejection* en temps constant (RFC 3447 §7.2.2) : un padding invalide n'est plus distinguable d'un padding valide, neutralisant l'oracle Bleichenbacher.

**Validation :** `php -l` OK, PHPUnit vert, aucune nouvelle erreur PHPStan introduite (différentiel nul vs `3.4.x`), aucun commentaire ajouté dans le code source. Après merge, cascade prévue `3.4.x → 4.0.x → 4.1.x`.

## References
- https://github.com/web-token/jwt-framework/security/advisories/GHSA-5739-39v2-5754
- https://github.com/FriendsOfPHP/security-advisories/blob/master/web-token/jwt-library/GHSA-5739-39v2-5754.yaml
- https://github.com/web-token/jwt-framework
