# [?] chore(deps): bump rustls to 0.23.45 to fix RUSTSEC-2026-0285 (#12911)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-09-15
Source: https://github.com/iotaledger/iota/commit/35cbbe23b6542372c9b23760962b0aec124ec33d
Type: security-commit

## Details
chore(deps): bump rustls to 0.23.45 to fix RUSTSEC-2026-0285 (#12911)

# Description of change

- Bump `rustls` 0.23.35 → 0.23.45 (and `rustls-webpki` 0.103.13 →
0.103.15) in `Cargo.lock`.
- Fixes
[RUSTSEC-2026-0285](https://rustsec.org/advisories/RUSTSEC-2026-0285):
rustls accepted TLS 1.3 handshake messages sent at the wrong encryption
level, which made `cargo deny check advisories` fail.
- Lockfile-only patch bump, no source changes.

## Links to any relevant issues

None.

## How the change has been tested

- [x] Basic tests (linting, compilation, formatting, unit/integration
tests)
- [ ] Patch-specific tests (correctness, functionality coverage)
- [ ] I have added tests that prove my fix is effective or that my
feature works
- [x] I have checked that new and existing unit tests pass locally with
my changes

`cargo deny check advisories --hide-inclusion-graph` now reports
`advisories ok`; `cargo check -p iota-tls --all-targets` compiles
cleanly.

### Release Notes

- [ ] Protocol:
- [x] Nodes (Validators and Full nodes): Bump `rustls` to 0.23.45 to fix
RUSTSEC-2026-0285 (TLS 1.3 handshake messages accepted at the wrong
encryption level).
- [ ] Indexer:
- [ ] JSON-RPC:
- [ ] GraphQL:
- [ ] CLI:
- [ ] Rust SDK:
- [ ] gRPC:

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude Fable 5.1 <noreply@anthropic.com>

## Patch
### Cargo.lock
```diff
@@ -12553,9 +12553,9 @@ dependencies = [
 
 [[package]]
 name = "rustls"
-version = "0.23.35"
+version = "0.23.45"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "533f54bc6a7d4f647e46ad909549eda97bf5afc1585190ef692b4286b198bd8f"
+checksum = "0d41d731c7d2f962d1ccc364cec258de3c0e93b38c2fb3ba97ac74513048d634"
 dependencies = [
  "log",
  "once_cell",
@@ -12617,9 +12617,9 @@ checksum = "f87165f0995f63a9fbeea62b64d10b4d9d8e78ec6d7d51fb2125fda7bb36788f"
 
 [[package]]
 name = "rustls-webpki"
-version = "0.103.13"
+version = "0.103.15"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "61c429a8649f110dddef65e2a5ad240f747e85f7758a6bccc7e5777bd33f756e"
+checksum = "f3c3cf1d8b1e7d4927e2d154c3fcb02979afb9939629c62cd9048d4f07b60ac2"
 dependencies = [
  "ring",
  "rustls-pki-types",
```
