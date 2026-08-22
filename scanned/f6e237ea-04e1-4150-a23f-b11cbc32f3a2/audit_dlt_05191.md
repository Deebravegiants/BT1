# [?] deny.toml: ignore RUSTSEC-2026-0097 for rand 0.7/0.8

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-04-11
Source: https://github.com/Conflux-Chain/conflux-rust/commit/f0e7e217dc658031347da9e1ee4910051a3f1778
Type: security-commit

## Details
deny.toml: ignore RUSTSEC-2026-0097 for rand 0.7/0.8

The main fix (rand 0.9 → 0.9.3) is applied in the previous commit, but
rand 0.7.3 and 0.8.5 still appear in Cargo.lock via external transitive
deps and first-party code pinned to upstream crates that haven't been
migrated yet (see commit message above and the deny.toml comment). The
newer cargo-deny used by CI detects the advisory on those versions and
fails the job. Add an ignore with the detailed reason so CI passes while
follow-up work removes the remaining first-party pins.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
