# [?] Merge pull request #4209 from oasisprotocol/ptrus/fix/RUSTSEC-2021-0093

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2021-08-23
Source: https://github.com/oasisprotocol/oasis-core/commit/75aa21f56c5c0156fb859f6ab9f2589738b36caa
Type: security-commit

## Details
Merge pull request #4209 from oasisprotocol/ptrus/fix/RUSTSEC-2021-0093

rust: update crossbeam-deque (RUSTSEC-2021-0093)

## Patch
### .changelog/4209.internal.md
```diff
@@ -0,0 +1 @@
+rust: update crossbeam-deque (RUSTSEC-2021-0093)
```

### Cargo.lock
```diff
@@ -401,7 +401,7 @@ checksum = "69323bff1fb41c635347b8ead484a5ca6c3f11914d784170b158d8449ab07f8e"
 dependencies = [
  "cfg-if 0.1.10",
  "crossbeam-channel 0.4.4",
- "crossbeam-deque 0.7.3",
+ "crossbeam-deque 0.7.4",
  "crossbeam-epoch 0.8.2",
  "crossbeam-queue 0.2.3",
  "crossbeam-utils 0.7.2",
@@ -415,7 +415,7 @@ checksum = "4ae5588f6b3c3cb05239e90bd110f257254aecd01e4635400391aeae07497845"
 dependencies = [
  "cfg-if 1.0.0",
  "crossbeam-channel 0.5.1",
- "crossbeam-deque 0.8.0",
+ "crossbeam-deque 0.8.1",
  "crossbeam-epoch 0.9.5",
  "crossbeam-queue 0.3.2",
  "crossbeam-utils 0.8.5",
@@ -443,9 +443,9 @@ dependencies = [
 
 [[package]]
 name = "crossbeam-deque"
-version = "0.7.3"
+version = "0.7.4"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "9f02af974daeee82218205558e51ec8768b48cf524bd01d550abe5573a608285"
+checksum = "c20ff29ded3204c5106278a81a38f4b482636ed4fa1e6cfbeef193291beb29ed"
 dependencies = [
  "crossbeam-epoch 0.8.2",
  "crossbeam-utils 0.7.2",
@@ -454,9 +454,9 @@ dependencies = [
 
 [[package]]
 name = "crossbeam-deque"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "94af6efb46fef72616855b036a624cf27ba656ffc9be1b9a3c931cfc7749a9a9"
+checksum = "6455c0ca19f0d2fbf751b908d5c55c1f5cbc65e03c4225427254b46890bdde1e"
 dependencies = [
  "cfg-if 1.0.0",
  "crossbeam-epoch 0.9.5",
```
