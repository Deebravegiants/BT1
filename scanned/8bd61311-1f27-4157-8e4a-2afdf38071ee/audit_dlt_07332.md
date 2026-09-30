# [?] fix: Bumps webpki to fix RUSTSEC-2023-0052. (#130)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2023-10-02
Source: https://github.com/matter-labs/zksync-era/commit/51e02cb78cd56ecd9f5df31f2b590ba19d866e1b
Type: security-commit

## Details
fix: Bumps webpki to fix RUSTSEC-2023-0052. (#130)

# What ❔

Bumps webpki to 0.22.2 due to RUSTSEC-2023-0052.
<!-- What are the changes this PR brings about? -->
<!-- Example: This PR adds a PR template to the repo. -->
<!-- (For bigger PRs adding more context is appreciated) -->

## Why ❔

To fix vulnerability.
<!-- Why are these changes done? What goal do they contribute to? What
are the principles behind them? -->
<!-- Example: PR templates ensure PR reviewers, observers, and future
iterators are in context about the evolution of repos. -->

## Checklist

<!-- Check your PR fulfills the following items. -->
<!-- For draft PRs check the boxes as you complete them. -->

- [x] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [ ] Tests for the changes have been added / updated.
- [ ] Documentation comments have been added / updated.
- [ ] Code has been formatted via `zk fmt` and `zk lint`.

## Patch
### Cargo.lock
```diff
@@ -7176,9 +7176,9 @@ dependencies = [
 
 [[package]]
 name = "webpki"
-version = "0.22.1"
+version = "0.22.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f0e74f82d49d545ad128049b7e88f6576df2da6b02e9ce565c6f533be576957e"
+checksum = "07ecc0cd7cac091bf682ec5efa18b1cff79d617b84181f38b3951dbe135f607f"
 dependencies = [
  "ring",
  "untrusted",
```

### prover/Cargo.lock
```diff
@@ -6135,9 +6135,9 @@ dependencies = [
 
 [[package]]
 name = "webpki"
-version = "0.22.0"
+version = "0.22.2"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f095d78192e208183081cc07bc5515ef55216397af48b873e5edcd72637fa1bd"
+checksum = "07ecc0cd7cac091bf682ec5efa18b1cff79d617b84181f38b3951dbe135f607f"
 dependencies = [
  "ring",
  "untrusted",
```
