# [?] Merge pull request #10045 from yyforyongyu/fix-panic

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2025-07-07
Source: https://github.com/lightningnetwork/lnd/commit/b815109b8117ee1874afa32f67ba80eff6967b9e
Type: security-commit

## Details
Merge pull request #10045 from yyforyongyu/fix-panic

contractcourt: only close quit in `Stop`

## Patch
### contractcourt/utxonursery.go
```diff
@@ -286,19 +286,18 @@ func (u *UtxoNursery) Start() error {
 	// 2. Restart spend ntfns for any preschool outputs, which are waiting
 	// for the force closed commitment txn to confirm, or any second-layer
 	// HTLC success transactions.
-	//
-	// NOTE: The next two steps *may* spawn go routines, thus from this
-	// point forward, we must close the nursery's quit channel if we detect
-	// any failures during startup to ensure they terminate.
+	// NOTE: The next two steps *may* spawn go routines.
 	if err := u.reloadPreschool(); err != nil {
-		close(u.quit)
+		utxnLog.Errorf("Failed to reload preschool: %v", err)
+
 		return err
 	}
 
 	// 3. Replay all crib and kindergarten outputs up to the current best
 	// height.
 	if err := u.reloadClasses(uint32(bestHeight)); err != nil {
-		close(u.quit)
+		utxnLog.Errorf("Failed to reload class: %v", err)
+
 		return err
 	}
 
@@ -309,7 +308,8 @@ func (u *UtxoNursery) Start() error {
 		Hash:   bestHash,
 	})
 	if err != nil {
-		close(u.quit)
+		utxnLog.Errorf("RegisterBlockEpochNtfn failed: %v", err)
+
 		return err
 	}
 
```

### docs/release-notes/release-notes-0.19.2.md
```diff
@@ -39,6 +39,9 @@
 
 - [Fixed](https://github.com/lightningnetwork/lnd/pull/10035) a deadlock (writer starvation) in the switch.
 
+- Fixed a [case](https://github.com/lightningnetwork/lnd/pull/10045) that a
+  panic may happen which prevents the node from starting up.
+
 # New Features
 
 ## Functional Enhancements
```
