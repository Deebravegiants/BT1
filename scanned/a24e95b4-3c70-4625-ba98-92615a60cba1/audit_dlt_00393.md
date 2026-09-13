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
- [x] `cargo deny check bans licenses sources --hide-inclusion-graph` →
still green (no regression from the diesel bump)
- [x] `cargo tree -i` verified the dependency paths quoted in the ignore
comments

(Pre-existing warning: external-crates' ignore for
RUSTSEC-2021-0145/`atty` no longer matches any crate — left untouched to
keep this PR single-purpose.)

---

## Release notes

Check each box that your changes affect. If none of the boxes relate to
your changes, release notes aren't required.

For each box you select, include information after the relevant heading
that describes the impact of your changes that a user might notice and
any actions they must take to implement updates.

- [ ] Protocol:
- [ ] Nodes (Validators and Full nodes):
- [ ] gRPC:
- [ ] JSON-RPC:
- [ ] GraphQL:
- [ ] CLI:
- [ ] Rust SDK:
- [ ] Indexing Framework:

---------

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

### Cargo.lock
```diff
@@ -4770,9 +4770,9 @@ dependencies = [
 
 [[package]]
 name = "diesel"
-version = "2.3.9"
+version = "2.3.10"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9940fb8467a0a06312218ed384185cb8536aa10d8ec017d0ce7fad2c1bd882d5"
+checksum = "29fe29a87fb84c631ffb3ba21798c4b1f3a964701ba78f0dce4bf8668562ec88"
 dependencies = [
  "bitflags 2.11.0",
  "byteorder",
```

### deny.toml
```diff
@@ -58,6 +58,12 @@ ignore = [
     # walrus, seal, and other downstream consumers. Deferred pending a coordinated
     # ecosystem-wide bump (likely driven by fastcrypto first).
     "RUSTSEC-2026-0097",
+    # `proc-macro-error2` is unmaintained, no safe upgrade — transitive via
+    # alloy-sol-macro (sui-bridge ethereum stack); waiting for alloy to migrate
+    "RUSTSEC-2026-0173",
+    # `http-types` ASCII invariant notice, no safe upgrade — dev-dependency only,
+    # via wiremock 0.5 test mocks; not used to construct auth headers
+    "RUSTSEC-2026-0174",
 ]
 # Threshold for security vulnerabilities, any vulnerability with a CVSS score
 # lower than the range specified will be ignored. Note that ignored advisories
```

### external-crates/move/deny.toml
```diff
@@ -59,6 +59,9 @@ ignore = [
     # thread-local RNG init — not present in this workspace. Deferred pending ecosystem
     # migration of rand 0.8 -> 0.9.
     "RUSTSEC-2026-0097",
+    # `proc-macro-error2` is unmaintained, no safe upgrade — transitive via
+    # aquamarine (doc diagrams), dev-dependency of move-package-alt
+    "RUSTSEC-2026-0173",
 ]
 # Threshold for security vulnerabilities, any vulnerability with a CVSS score
 # lower than the range specified will be ignored. Note that ignored advisories
```
