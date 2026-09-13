# [?] chore(ci): bump lru to 0.18.2 and allow RUSTSEC-2026-0253 (#16210)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-08-17
Source: https://github.com/near/nearcore/commit/ff6ed2096f8bd281f9c9534291f3c312026beb3a
Type: security-commit

## Details
chore(ci): bump lru to 0.18.2 and allow RUSTSEC-2026-0253 (#16210)

`cargo audit -D warnings` fails on master. RUSTSEC-2026-0253 was filed
against `lru`: `LruCache::pop()` was not panic-safe, so a panicking key
`Drop` could leave dangling pointers in the internal linked list. Fixed
in 0.18.2.

Bumps the workspace dependency from 0.16.3 to 0.18.2.

The other copy is `lru` 0.7.8 under `reed-solomon-erasure`, which
requires `^0.7.8` in its latest release, 6.0.0 (2022-09-23), so no
published version resolves to a patched `lru`. That one is added to
`.cargo/audit.toml` instead: the bug needs unwinding plus a key with a
panicking `Drop`, and that cache is keyed by `Vec<usize>`.

Not urgent either way, since release builds set `panic = 'abort'`
(`Cargo.toml:398`).
