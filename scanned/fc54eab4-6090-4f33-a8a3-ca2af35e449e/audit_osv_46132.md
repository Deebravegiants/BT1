# [C] JLSEC-2026-713

## Summary
Severity: Critical
Advisory: JLSEC-2026-713
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/JLSEC-2026-713
Type: osv

## Affected
- Julia: `wolfSSL_jll` — affected >=0 <5.9.2+0

## Details
Heap-based buffer overflow in the KCAPI ECC code path of `wc_ecc_import_x963_ex()` in wolfSSL wolfcrypt allows a remote attacker to write attacker-controlled data past the bounds of the `pubkey_raw` buffer via a crafted oversized EC public key point. The `WOLFSSL_KCAPI_ECC` code path copies the input to key->`pubkey_raw` (132 bytes) using XMEMCPY without a bounds check, unlike the ATECC code path which includes a length validation. This can be triggered during TLS key exchange when a malicious peer sends a crafted ECPoint in ServerKeyExchange.

## References
- https://github.com/wolfSSL/wolfssl/pull/9988
