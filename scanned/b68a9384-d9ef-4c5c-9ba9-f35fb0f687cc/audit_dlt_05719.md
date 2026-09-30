# [?] docs(changelog): link GHSA-x93j and remove duplicate entry  (#11064)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-07-23
Source: https://github.com/ZcashFoundation/zebra/commit/95c0b7c533098f1b4ed81608a47f0acd1226cf96
Type: security-commit

## Details
docs(changelog): link GHSA-x93j and remove duplicate entry  (#11064)

* Link the security advisory to the changelog

Ensure there's a way for readers to obtain more information.

* Remove entry placed in the incorrect version

Artifact of merging.

## Patch
### CHANGELOG.md
```diff
@@ -27,7 +27,8 @@ and this project adheres to [Semantic Versioning](https://semver.org).
 ### Security
 
 - Allow chain synchronization to immediately retry an honest block body after rejecting a body
-  with the same header hash, without waiting for a child block to trigger cleanup.
+  with the same header hash, without waiting for a child block to trigger cleanup
+  ([GHSA-x93j-mj2f-q338](https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-x93j-mj2f-q338)).
 - Mitigate a peer-driven CPU-exhaustion vector on nodes with NU6.3 (Ironwood) active: reject
   underpaying and structurally invalid shielded mempool transactions before their expensive proof
   verification, and disconnect peers that send transactions with invalid shielded proofs.
@@ -62,12 +63,6 @@ and this project adheres to [Semantic Versioning](https://semver.org).
   source, so its generated command works with the published Zebra image
   ([#11008](https://github.com/ZcashFoundation/zebra/pull/11008)).
 
-### Security
-
-- Allow chain synchronization to immediately retry an honest block body after
-  rejecting a body with the same header hash, without waiting for a child block
-  to trigger cleanup.
-
 ## [Zebra 6.1.0](https://github.com/ZcashFoundation/zebra/releases/tag/v6.1.0) - 2026-07-17
 
 ### Added
```

### zebra-state/CHANGELOG.md
```diff
@@ -11,7 +11,8 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 
 - Known block queries now clear notifications for rejected non-finalized blocks before
   checking sent hashes, allowing an honest block body with the same header hash to be
-  retried immediately.
+  retried immediately
+  ([GHSA-x93j-mj2f-q338](https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-x93j-mj2f-q338)).
 
 ## [11.1.0] - 2026-07-17
 
```
