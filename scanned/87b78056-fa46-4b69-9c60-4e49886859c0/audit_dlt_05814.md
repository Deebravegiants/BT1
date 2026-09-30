# [?] chore(ci): bump h2 to 0.4.16 for RUSTSEC-2026-0258 (#16254)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-08-18
Source: https://github.com/near/nearcore/commit/c565ada084285f197b5f32ad37d93d847d66765a
Type: security-commit

## Details
chore(ci): bump h2 to 0.4.16 for RUSTSEC-2026-0258 (#16254)

`cargo audit -D warnings` fails on master with RUSTSEC-2026-0258 (h2
unbounded empty DATA frames), published 2026-08-17. The advisory affects
h2 < 0.4.16.

h2 is a transitive dependency only, reached through `hyper 1.7.0`,
`reqwest 0.12.28`, and `reqwest 0.13.2`. There is a single version in
the lockfile and the fix is semver-compatible, so `cargo update -p h2`
is enough.

`cargo audit -D warnings` is clean after this change.

## Patch
### Cargo.lock
```diff
@@ -2603,9 +2603,9 @@ dependencies = [
 
 [[package]]
 name = "h2"
-version = "0.4.8"
+version = "0.4.16"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5017294ff4bb30944501348f6f8e42e6ad28f42c8bbef7a74029aff064a4e3c2"
+checksum = "a9f37a958b41b3b19ee2707c06439c0e9e547e847223eb791ecb0cb821c65e27"
 dependencies = [
  "atomic-waker",
  "bytes",
```
