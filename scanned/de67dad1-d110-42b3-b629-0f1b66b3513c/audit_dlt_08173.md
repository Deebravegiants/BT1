# [?] docs(changelog): add an entry for GHSA-g7c4-2w6c-cr3r

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-07-17
Source: https://github.com/ZcashFoundation/zebra/commit/bcf8efa0db4617f56de27b6d2caa617ab2ae1a9d
Type: security-commit

## Details
docs(changelog): add an entry for GHSA-g7c4-2w6c-cr3r

## Patch
### CHANGELOG.md
```diff
@@ -5,6 +5,14 @@ All notable changes to Zebra are documented in this file.
 The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
 and this project adheres to [Semantic Versioning](https://semver.org).
 
+## [Unreleased]
+
+### Security
+
+- Score misbehavior for peers that directly push consensus-invalid transactions, matching the
+  treatment of peers that advertise them
+  ([GHSA-g7c4-2w6c-cr3r](https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-g7c4-2w6c-cr3r)).
+
 ## [Zebra 6.0.0](https://github.com/ZcashFoundation/zebra/releases/tag/v6.0.0) - 2026-07-10
 
 ### Added
```
