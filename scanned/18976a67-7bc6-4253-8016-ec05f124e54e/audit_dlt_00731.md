# [?] fix(inbound): score peers for RouterError from invalid gossiped blocks (GHSA-8hh2-hrf2-cqf4)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-08-03
Source: https://github.com/ZcashFoundation/zebra/commit/dfb284116a50b257bf2656d8ce8a1d0255366ada
Type: security-commit

## Details
fix(inbound): score peers for RouterError from invalid gossiped blocks (GHSA-8hh2-hrf2-cqf4)

Co-Authored-By: Evan Forbes <42654277+evan-forbes@users.noreply.github.com>

During integration with the existing security fixes, retain their
release-note entries and add the invalid gossiped-block scoring
advisory under the shared Security section.

Conflicts:
    CHANGELOG.md

## Patch
### CHANGELOG.md
```diff
@@ -68,6 +68,11 @@ and this project adheres to [Semantic Versioning](https://semver.org).
   malicious `FindBlocks` responder get honest peers banned during initial block
   download (GHSA-qhr3-cvch-5fh2)
 
+- Peers that gossip consensus-invalid blocks are scored for misbehavior again. The inbound
+  download cleanup only recognized `VerifyBlockError`, but the gossiped block verifier is a
+  `BlockVerifierRouter`, which returns `RouterError`, so no score was ever applied and such
+  peers were never banned (GHSA-8hh2-hrf2-cqf4)
+
 ## [Zebra 6.2.3](https://github.com/ZcashFoundation/zebra/releases/tag/v6.2.3) - 2026-07-27
 
 This is an optional release with network hardenings for operators that experience issues with their nodes peer set connectivity or otherwise want to be proactive about avoiding such issues.
```

### zebrad/src/components/inbound.rs
```diff
@@ -335,13 +335,29 @@ impl Service<zn::Request> for Inbound {
                         continue;
                     };
 
-                    let Ok(err) = err.downcast::<VerifyBlockError>() else {
+                    // # Security
+                    //
+                    // The gossiped block verifier is a `BlockVerifierRouter`, so a failed
+                    // verification is boxed as a `RouterError`. `Box<dyn Error>::downcast`
+                    // is an exact type match, so downcasting to `VerifyBlockError` alone
+                    // never matched, and misbehaving peers were never scored.
+                    // (`VerifyBlockError` only appears nested inside `RouterError::Block`.)
+                    //
+                    // `VerifyBlockError` is still handled, so scoring keeps working if the
+                    // verifier stack is ever rewired to skip the router.
+                    //
+                    // Any other error (a tower `Elapsed` timeout, a transport failure) is a
+                    // local problem rather than peer misbehavior, so it stays unscored.
+                    let score = if let Some(err) = err.downcast_ref::<RouterError>() {
+                        err.misbehavior_score()
+                    } else if let Some(err) = err.downcast_ref::<VerifyBlockError>() {
+                        err.misbehavior_score()
+                    } else {
                         continue;
                     };
 
-                    if err.misbehavior_score() != 0 {
-                        let _ =
-                            misbehavior_sender.try_send((advertiser_addr, err.misbehavior_score()));
+                    if score != 0 {
+                        let _ = misbehavior_sender.try_send((advertiser_addr, score));
                     }
                 }
 
```
