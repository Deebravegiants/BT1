# [?] chore(deps): bumps h2 to avoid vulnerability alert (#895)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2024-01-18
Source: https://github.com/matter-labs/zksync-era/commit/3f0695d76e9bfd1ddf59ba67fb6f9a1173c37105
Type: security-commit

## Details
chore(deps): bumps h2 to avoid vulnerability alert (#895)

## What ❔

<!-- What are the changes this PR brings about? -->
<!-- Example: This PR adds a PR template to the repo. -->
<!-- (For bigger PRs adding more context is appreciated) -->

## Why ❔

<!-- Why are these changes done? What goal do they contribute to? What
are the principles behind them? -->
<!-- Example: PR templates ensure PR reviewers, observers, and future
iterators are in context about the evolution of repos. -->

## Checklist

<!-- Check your PR fulfills the following items. -->
<!-- For draft PRs check the boxes as you complete them. -->

- [ ] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [ ] Tests for the changes have been added / updated.
- [ ] Documentation comments have been added / updated.
- [ ] Code has been formatted via `zk fmt` and `zk lint`.
- [ ] Spellcheck has been run via `zk spellcheck`.

## Patch
### Cargo.lock
```diff
@@ -2873,17 +2873,17 @@ dependencies = [
 
 [[package]]
 name = "h2"
-version = "0.3.21"
+version = "0.3.24"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "91fc23aa11be92976ef4729127f1a74adf36d8436f7816b185d18df956790833"
+checksum = "bb2c4422095b67ee78da96fbb51a4cc413b3b25883c7717ff7ca1ab31022c9c9"
 dependencies = [
  "bytes",
  "fnv",
  "futures-core",
  "futures-sink",
  "futures-util",
  "http",
- "indexmap 1.9.3",
+ "indexmap 2.1.0",
  "slab",
  "tokio",
  "tokio-util",
```
