# [M] openssl-encrypt has non-cryptographic PRNG used for steganography pixel selection

## Summary
Severity: Medium
Advisory: GHSA-vfgx-5q85-58q3
CWE: CWE-330
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-vfgx-5q85-58q3
Type: github-advisory

## Affected
- PyPI: `openssl-encrypt` — affected >=0 <1.4.0

## Details
### Summary

The `generate_pseudorandom_sequence()` function in `openssl_encrypt/plugins/steganography/core/utils.py` at **lines 89-91** uses Python's `random` module (Mersenne Twister) for steganographic pixel/sample selection.

### Affected Code

```python
random.seed(seed)
sequence = random.sample(range(max_value), min(length, max_value))
return sequence
```

Additionally, the steganography password is stored as a plain Python string (not `SecureBytes`) and only 8 bytes (64 bits) of the SHA-256 hash are used for the seed, reducing effective security to 64 bits.

### Impact

The Mersenne Twister's state can be recovered from approximately 624 outputs. An attacker who knows or guesses the password can predict the PRNG sequence and determine exactly which pixels contain hidden data, potentially extracting the hidden data without the password.

### Recommended Fix

- Use HMAC-DRBG or `secrets` module for cryptographically secure pixel selection
- Use full 32-byte SHA-256 output as seed material
- Store the password in `SecureBytes` instead of a plain string

### Fix

Fixed in commit `09e96e0` on branch `releases/1.4.x` — replaced random.seed(hash(password)) with HMAC-SHA256 based CSPRNG (Fisher-Yates shuffle) and numpy Generator with HMAC-derived seeds across all steganography format modules.

## References
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-vfgx-5q85-58q3
- https://github.com/jahlives/openssl_encrypt/commit/09e96e090417d34d2f533f6810d3cd4f77810101
- https://github.com/jahlives/openssl_encrypt
