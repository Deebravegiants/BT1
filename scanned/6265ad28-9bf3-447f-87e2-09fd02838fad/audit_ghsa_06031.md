# [H] Phalcon: Non-constant-time HMAC verification in `Encryption\Crypt::decrypt` (timing side-channel)

## Summary
Severity: High
Advisory: GHSA-8jqh-95g6-7jpj
CVE: CVE-2026-54736
CWE: CWE-208, CWE-347
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-8jqh-95g6-7jpj
Type: github-advisory

## Affected
- Packagist: `phalcon/cphalcon` — affected >=0 <5.14.1

## Details
## Summary

`Phalcon\Encryption\Crypt` provides authenticated encryption: when `useSigning` is enabled (the default), `encrypt()` appends an HMAC tag and `decrypt()` verifies it before returning the plaintext. The verification compares the attacker-supplied tag against the freshly computed HMAC using PHP/Zephir identity comparison (`!==`), which the Zephir compiler lowers to `!ZEPHIR_IS_IDENTICAL(...)` — a byte-wise `memcmp` that returns early on the first differing byte. The comparison time therefore depends on how many leading bytes of the supplied tag are correct, a classic MAC-verification timing side-channel. Every other secret/MAC comparison in the framework uses the constant-time `hash_equals()` (`zephir_hash_equals`) — the CSRF token check (`Security::checkToken`) and the JWT signature check (`Signer\Hmac::verify`); `Crypt::decrypt` is the lone deviation.

## Details

### Vulnerable code

`phalcon/Encryption/Crypt.zep:246` (Zephir source):

```zephir
if true === this->useSigning {
    // Checks on the decrypted message digest using the HMAC method.
    if digest !== hash_hmac(hashAlgorithm, padded, decryptKey, true) {
        throw new Mismatch("Hash does not match.");
    }
}
```

Generated C --> `ext/phalcon/encryption/crypt.zep.c:364-367`:

```c
ZEPHIR_CALL_FUNCTION(&_8$$7, "hash_hmac", NULL, 245, &hashAlgorithm, &padded, &decryptKey, &__$true);
...
if (!ZEPHIR_IS_IDENTICAL(&digest, &_8$$7)) {                 // <-- non-constant-time
    ZEPHIR_THROW_EXCEPTION_DEBUG_STR(..., "Hash does not match.", "phalcon/Encryption/Crypt.zep", 247);
```

`ZEPHIR_IS_IDENTICAL` --> `zephir_is_identical()` (`ext/kernel/operators.c:472`) --> Zend `is_identical_function` --> for equal-length strings a `memcmp` that exits on the first mismatching byte (data-dependent timing).



### Impact

The HMAC is the integrity/authentication tag of Phalcon's authenticated-encryption scheme. A successful timing attack (Keyczar/CVE-2009-0654-style: fix the IV+ciphertext so the target tag is constant, then recover it byte-by-byte from response timing) yields a tag the attacker can attach to a chosen IV+ciphertext so that `decrypt()` accepts it as authentic, defeating the integrity guarantee. Combined with CFB malleability (flipping a ciphertext byte flips the corresponding plaintext byte), an attacker who recovers the forging capability can tamper with the decrypted contents the application trusts (e.g. encrypted cookies carrying authorization/identity state). There is no confidentiality break by itself.

## Suggested fix

Replace the identity comparison with the constant-time helper already used elsewhere in the framework. In `phalcon/Encryption/Crypt.zep:246`:

```zephir
// before
if digest !== hash_hmac(hashAlgorithm, padded, decryptKey, true) {
    throw new Mismatch("Hash does not match.");
}
// after
if true !== hash_equals(hash_hmac(hashAlgorithm, padded, decryptKey, true), digest) {
    throw new Mismatch("Hash does not match.");
}
```

`hash_equals()` returns false for unequal-length inputs, so it also covers the truncated-tag case. Optional further hardening: verify the MAC before unpadding (functionally moot here because `cryptUnpadText` never throws) and consider migrating the default toward an AEAD mode such as `aes-256-gcm`.

Addressed Issue: 

- https://github.com/phalcon/cphalcon/issues/17090

Patched Stream: 

- https://github.com/phalcon/cphalcon/issues/17090

## References
- https://github.com/phalcon/cphalcon/security/advisories/GHSA-8jqh-95g6-7jpj
- https://nvd.nist.gov/vuln/detail/CVE-2026-54736
- https://github.com/phalcon/cphalcon/issues/17090
- https://github.com/phalcon/cphalcon/pull/17091
- https://github.com/phalcon/cphalcon/commit/ad53ab1b2e7ec59b3af92b0b37b8aaa099011137
- https://github.com/phalcon/cphalcon
- https://github.com/phalcon/cphalcon/releases/tag/v5.14.1
