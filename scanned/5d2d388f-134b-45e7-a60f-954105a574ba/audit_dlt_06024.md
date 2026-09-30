# [?] chore(deps): update h2 to 0.4.17 to fix RUSTSEC-2026-0258 (#12704)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-08-20
Source: https://github.com/iotaledger/iota/commit/47734c9f2a3ad876d69550071824452346964575
Type: security-commit

## Details
chore(deps): update h2 to 0.4.17 to fix RUSTSEC-2026-0258 (#12704)

# Description of change

- Updates `h2` from 0.4.12 to 0.4.17 in `Cargo.lock` to resolve
[RUSTSEC-2026-0258](https://rustsec.org/advisories/RUSTSEC-2026-0258)
(h2 unbounded empty DATA frames).
- Fixes the failing nightly `cargo deny check advisories` job:
https://github.com/iotaledger/iota/actions/runs/32191017965/job/95885133803
- Also carries a few incidental transitive lockfile adjustments from
`cargo update -p h2` (`spin`, `socket2`, `windows-sys`).

## Links to any relevant issues

None.

## How the change has been tested

- [x] Basic tests (linting, compilation, formatting, unit/integration
tests)
- [x] Patch-specific tests (correctness, functionality coverage): `cargo
deny check advisories` passes locally.
- [ ] I have added tests that prove my fix is effective or that my
feature works
- [x] I have checked that new and existing unit tests pass locally with
my changes

<!-- Do not remove: everything below this line is ignored by the
release-notes check. -->

---

---------

Co-authored-by: Claude Fable 5 <noreply@anthropic.com>

## Patch
### Cargo.lock
```diff
@@ -4713,9 +4713,9 @@ dependencies = [
 
 [[package]]
 name = "h2"
-version = "0.4.12"
+version = "0.4.17"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f3c0b69cfcb4e1b9f1bf2f53f95f766e4661169728ec61cd3fe5a0166f2d1386"
+checksum = "9f877e75f39e9827ec50a572dd592684ac28c029578726c85f1b2aa6ab807449"
 dependencies = [
  "atomic-waker",
  "bytes",
@@ -10199,7 +10199,7 @@ version = "0.50.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "7957b9740744892f114936ab4a57b3f487491bbeafaf8083688b16841a4240e5"
 dependencies = [
- "windows-sys 0.61.2",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -11754,7 +11754,7 @@ dependencies = [
  "quinn-udp",
  "rustc-hash 2.1.2",
  "rustls",
- "socket2 0.6.3",
+ "socket2 0.5.7",
  "thiserror 2.0.18",
  "tokio",
  "tracing",
@@ -13369,9 +13369,9 @@ dependencies = [
 
 [[package]]
 name = "spin"
-version = "0.9.8"
+version = "0.9.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "6980e8d7511241f8acf4aebddbb1ff938df5eebe98691418c4468d0b72a96a67"
+checksum = "3763264f6b73151db08c50ff20d7d8a0b8796e021cdea7ceedad07b80155fa0e"
 
 [[package]]
 name = "spinning_top"
```
