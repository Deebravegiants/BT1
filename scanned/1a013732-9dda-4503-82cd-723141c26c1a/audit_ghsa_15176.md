# [M] Use-after-free when setting the locale

## Summary
Severity: Medium
Advisory: GHSA-c8v3-jhv9-4ppc
CWE: CWE-416
Ecosystem: crates.io
Published: 2024-01-23
Source: https://github.com/advisories/GHSA-c8v3-jhv9-4ppc
Type: github-advisory

## Affected
- crates.io: `rust-i18n-support` — affected >=3.0.0 <3.0.1

## Details
Version 3.0.0 introduced an `AtomicStr` type, that is used to store the current locale. It stores the locale as a raw pointer to an `Arc<String>`. The locale can be read with `AtomicStr::as_str()`. `AtomicStr::as_str()` does not increment the usage counter of the `Arc`.

If the locale is changed in one thread, another thread can have a stale -- possibly already freed -- reference to the stored string.

## References
- https://github.com/longbridgeapp/rust-i18n/issues/71
- https://github.com/longbridgeapp/rust-i18n/commit/22e0609591a2c08930f52a0e6bc860f02a0e88c0
- https://github.com/longbridgeapp/rust-i18n
- https://rustsec.org/advisories/RUSTSEC-2024-0007.html
