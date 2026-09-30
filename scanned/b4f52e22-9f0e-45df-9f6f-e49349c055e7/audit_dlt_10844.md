# [?] fix: underflow error in `calc-claimable-amount`

## Summary
Severity: Unknown
Chain: Stacks
Component: stacks-network/stacks-core
Published: 2025-07-16
Source: https://github.com/stacks-network/stacks-core/commit/d9e0d505a8f93ec01c14256a264ed99a2f5d4bbd
Type: security-commit

## Details
fix: underflow error in `calc-claimable-amount`

## Patch
### contrib/core-contract-tests/tests/sip-031/sip-031.test.ts
```diff
@@ -281,4 +281,10 @@ test('new recipient claims vested tranche plus extra deposit', () => {
   expect(evt.data.amount).toBe(expected.toString());
   expect(evt.data.recipient).toBe(accounts.wallet_1.address);
   expect(evt.data.sender).toBe(contract.identifier);
+});
+
+test('calculating claimable amount at invalid block height returns 0', () => {
+  mintInitial();
+  const deployBlockHeight = rov(contract.getDeployBlockHeight());
+  expect(rov(contract.calcClaimableAmount(deployBlockHeight - 1n))).toBe(0n);
 });
\ No newline at end of file
```

### stackslib/src/chainstate/stacks/boot/sip-031.clar
```diff
@@ -83,16 +83,18 @@
 
 ;; Returns the amount of STX that is claimable from the vested balance at `burn-height`
 (define-read-only (calc-claimable-amount (burn-height uint))
-    (let
-        (
-            (total-vested (calc-total-vested burn-height))
-            (reserved (- INITIAL_MINT_AMOUNT total-vested))
-            (balance (stx-get-balance (as-contract tx-sender)))
-            (claimable
-                (if (> balance reserved)
-                    (- balance reserved)
-                    u0))
+    (if (< burn-height deploy-block-height)
+        u0
+        (let
+            (
+                (reserved (- INITIAL_MINT_AMOUNT (calc-total-vested burn-height)))
+                (balance (stx-get-balance (as-contract tx-sender)))
+                (claimable
+                    (if (> balance reserved)
+                        (- balance reserved)
+                        u0))
+            )
+            claimable
         )
-        claimable
     )
 )
```
