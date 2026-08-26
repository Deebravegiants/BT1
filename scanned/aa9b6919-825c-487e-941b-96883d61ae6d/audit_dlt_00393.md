# [?] Fix cargo-deny advisory failures (RUSTSEC-2026-0172/0173/0174) (#26948)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2026-06-11
Source: https://github.com/MystenLabs/sui/commit/c8f4a24ceeba07f517fc50cf65db9a2437d2506e
Type: security-commit

## Details
Fix cargo-deny advisory failures (RUSTSEC-2026-0172/0173/0174) (#26948)

## Summary

Three RustSec advisories published this week broke the `cargo-deny
(advisories)` checks on every PR with Rust changes (e.g. [this
run](https://github.com/MystenLabs/sui/actions/runs/27360485434/job/80846274215)
on #26946):

| Advisory | Crate | Severity | Fix |
|---|---|---|---|
| RUSTSEC-2026-0172 | `diesel` 2.3.9 | unsound (use-after-free in
`SqliteConnection::deserialize_readonly_database`) | **upgraded to
2.3.10** (patched; lockfile-only, workspace pins `diesel = "2.3"`) |
| RUSTSEC-2026-0173 | `proc-macro-error2` 2.0.1 | unmaintained, no safe
upgrade | deny.toml ignore — transitive via `alloy-sol-macro`
(sui-bridge ethereum stack) in the root workspace and via `aquamarine`
(dev-dep of `move-package-alt`) in external-crates; waiting for
upstreams to migrate |
| RUSTSEC-2026-0174 | `http-types` 2.12.0 | notice (ASCII invariants in
`Authorization::value`), no safe upgrade | deny.toml ignore —
dev-dependency only, via `wiremock` 0.5 test mocks; not used to
construct auth headers |

The diesel advisory is the only one with real code impact and it has a
patched release, so it's upgraded rather than ignored. Sui doesn't call
`deserialize_readonly_database` (diesel is used with postgres), but
taking the patch is strictly better than an ignore.

## Test plan

All three CI commands run locally with cargo-deny 0.19.4:

- [x] `cargo deny check advisories --hide-inclusion-graph` → `advisories
ok` (was failing with the 3 advisories)
- [x] `cargo deny --manifest-path external-crates/move/Cargo.toml check
--hide-inclusion-graph` → `advisories ok, bans ok, licenses ok, sources
ok`

_Trimmed to 38 lines — full report: https://github.com/MystenLabs/sui/commit/c8f4a24ceeba07f517fc50cf65db9a2437d2506e_
