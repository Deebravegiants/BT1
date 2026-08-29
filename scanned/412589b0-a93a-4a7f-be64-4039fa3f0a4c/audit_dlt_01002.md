# [?] fix(wallet): reject BIP32 paths that overflow the harden bit (#16096)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-08-18
Source: https://github.com/foundry-rs/foundry/commit/40e0fe51e59c496d83752f314db645f1f51077d3
Type: security-commit

## Details
fix(wallet): reject BIP32 paths that overflow the harden bit (#16096)

* fix(wallet): reject BIP32 paths that overflow the harden bit

Narrow overflow guard only: strip one trailing ' or h, reject parsed
values >= BIP32_HARDEN, leave malformed syntax to MnemonicBuilder.
derive_key_path stays String; consumers use derive_key_path_checked.

* fix(wallet): collapse BIP32 overflow if for clippy

---------

Co-authored-by: Mablr <59505383+mablr@users.noreply.github.com>
