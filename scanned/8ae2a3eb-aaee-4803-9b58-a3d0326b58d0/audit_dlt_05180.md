# [?] Drop stale RUSTSEC-2026-0097 ignore

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-07-02
Source: https://github.com/Conflux-Chain/conflux-rust/commit/90febe83aba0eb8661100b4951d68e1294ecf6f9
Type: security-commit

## Details
Drop stale RUSTSEC-2026-0097 ignore

rand 0.7 is gone from the tree and the remaining rand 0.8.6 contains the backported ThreadRng fix, so the advisory no longer matches any crate (cargo-deny warned advisory-not-detected).

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
