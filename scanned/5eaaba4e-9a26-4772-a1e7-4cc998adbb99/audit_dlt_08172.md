# [?] docs(changelog): add entries for GHSA-4g24-549m-hp75

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-07-17
Source: https://github.com/ZcashFoundation/zebra/commit/2ad4223ab51220f1c8b7663d8e9970425f1f9981
Type: security-commit

## Details
docs(changelog): add entries for GHSA-4g24-549m-hp75

## Patch
### CHANGELOG.md
```diff
@@ -5,6 +5,13 @@ All notable changes to Zebra are documented in this file.
 The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
 and this project adheres to [Semantic Versioning](https://semver.org).
 
+## [Unreleased]
+
+### Security
+
+- Avoid quadratic validation work when checking the remaining transparent value of blocks with
+  many transactions ([GHSA-4g24-549m-hp75](https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-4g24-549m-hp75)).
+
 ## [Zebra 6.0.0](https://github.com/ZcashFoundation/zebra/releases/tag/v6.0.0) - 2026-07-10
 
 ### Added
```

### zebra-chain/CHANGELOG.md
```diff
@@ -5,6 +5,13 @@ All notable changes to this project will be documented in this file.
 The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
 and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
 
+## [Unreleased]
+
+### Security
+
+- Computing `transaction::Transaction::value_balance` no longer clones the entire UTXO map per
+  call (GHSA-4g24-549m-hp75).
+
 ## [11.1.0] - 2026-07-10
 
 ### Added
```

### zebra-state/CHANGELOG.md
```diff
@@ -5,6 +5,13 @@ All notable changes to this project will be documented in this file.
 The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
 and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
 
+## [Unreleased]
+
+### Security
+
+- Checking the remaining transaction value of a block is no longer quadratic in the number of
+  transactions (GHSA-4g24-549m-hp75).
+
 ## [10.1.0] - 2026-07-10
 
 ### Added
```
