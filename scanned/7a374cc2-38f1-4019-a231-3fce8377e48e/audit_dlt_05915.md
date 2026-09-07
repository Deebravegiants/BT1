# [?] fix(crypto): Fix side-channel vulnerability in BIP-39 mnemonic processing

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2025-11-12
Source: https://github.com/trezor/trezor-firmware/commit/9b1c06205c41811abe7de81d9e50abd22613f0b3
Type: security-commit

## Details
fix(crypto): Fix side-channel vulnerability in BIP-39 mnemonic processing

Fix function `mnemonic_to_bits` to be constant time. Replace binary search over the wordlist with a linear search to ensure the same number of comparisons.
Introduce function `constant_time_memeq` that comapres two parts of memory in costant time.
Remove integrity check in legacy to reduce the number of computations over seed.

(cherry picked from commit 4e6f0dee81b4d9e553d247faa3194b8053b74dcb)
