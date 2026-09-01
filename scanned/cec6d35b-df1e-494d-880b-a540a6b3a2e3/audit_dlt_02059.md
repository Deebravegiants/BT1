# [?] fix(core): prevent overflow in storage UI callback

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2025-05-04
Source: https://github.com/trezor/trezor-firmware/commit/9a709303880a8224f1e4f35558f1a4813536f320
Type: security-commit

## Details
fix(core): prevent overflow in storage UI callback

- this PR makes sure that the reported `wait` argument (in seconds) does
not underflows to "4294967 seconds"
- this can ocassionaly happen in animated loader

[no changelog]
