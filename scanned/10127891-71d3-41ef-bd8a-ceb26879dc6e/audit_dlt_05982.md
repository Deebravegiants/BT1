# [?] build(deps): bump ruint from 1.17.2 to 1.20.0 to fix RUSTSEC-2026-0220

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-07-31
Source: https://github.com/Conflux-Chain/conflux-rust/commit/1cd7e5e96675351c02d95d2bf0e1cb48751ba5eb
Type: security-commit

## Details
build(deps): bump ruint from 1.17.2 to 1.20.0 to fix RUSTSEC-2026-0220

ruint 1.17.2 has false-negative overflow flags in overflowing_shl/shr
(RUSTSEC-2026-0220), failing cargo-audit and cargo-deny CI jobs on all
branches. ruint is a pure transitive dependency (via the alloy stack),
so only the lockfiles of the three workspaces need updating. The bump
also introduces arkworks 0.6 crates as new optional deps of ruint,
coexisting with the 0.4/0.5 stacks.
