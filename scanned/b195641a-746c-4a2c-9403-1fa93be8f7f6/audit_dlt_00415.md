# [?] fix(audit): bump time to 0.3.47 to fix RUSTSEC-2026-0009 (#15684)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-05-07
Source: https://github.com/near/nearcore/commit/d88271ea4fcc1eeb93646388318abcf0a73bb840
Type: security-commit

## Details
fix(audit): bump time to 0.3.47 to fix RUSTSEC-2026-0009 (#15684)

Bump `time` from 0.3.9 to 0.3.47 to address
[RUSTSEC-2026-0009](https://rustsec.org/advisories/RUSTSEC-2026-0009) —
a stack exhaustion DoS in RFC 2822 parsing. Drop the corresponding
ignore from `.cargo/audit.toml`.

This was previously blocked because `time >= 0.3.47` requires Rust 1.88;
the toolchain bump to 1.93 (#15681) unblocks it.

Supersedes #15009, which only updated the workspace `Cargo.toml`
constraint and didn't refresh the main `Cargo.lock`.

Closes #15026.
