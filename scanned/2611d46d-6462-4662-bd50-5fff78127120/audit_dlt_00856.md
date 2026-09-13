# [?] fix(deps): bump anyhow to 1.0.103 to resolve RUSTSEC-2026-0190 (#4882)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2026-07-01
Source: https://github.com/matter-labs/zksync-era/commit/8a7adb26ed2adcd3fca21d96ca4130291785d98e
Type: security-commit

## Details
fix(deps): bump anyhow to 1.0.103 to resolve RUSTSEC-2026-0190 (#4882)

## What ❔

Bumps `anyhow` `1.0.98 → 1.0.103` in the `core` workspace lockfile.

## Why ❔

[RUSTSEC-2026-0190](https://rustsec.org/advisories/RUSTSEC-2026-0190)
flags an unsoundness in `anyhow` 1.0.98 (`Error::downcast_mut` after
`Error::context` violates borrow rules, causing UB). The `cargo-deny` CI
runs with `--allow unmaintained`, so this `unsound` advisory fails the
check on every open PR (e.g. #4879). Bumping to the patched `1.0.103`
resolves it without adding a fragile ignore entry to `core/deny.toml`.

Verified locally with `cargo-deny 0.19.9`: `advisories ok, bans ok,
licenses ok, sources ok`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---------

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
