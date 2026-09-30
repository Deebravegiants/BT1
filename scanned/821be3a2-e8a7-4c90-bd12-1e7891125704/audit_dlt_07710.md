# [?] Fix to allow balance underflow when estimating gas (#9616)

## Summary
Severity: Unknown
Chain: Ethereum
Component: besu-eth/besu
Published: 2026-01-09
Source: https://github.com/besu-eth/besu/commit/507b1635b5891d1289465bd2c6da21f834c4148e
Type: security-commit

## Details
Fix to allow balance underflow when estimating gas (#9616)

Signed-off-by: Fabio Di Fabio <fabio.difabio@consensys.net>

## Patch
### ethereum/core/src/main/java/org/hyperledger/besu/ethereum/mainnet/MainnetTransactionProcessor.java
```diff
@@ -246,13 +246,21 @@ public TransactionProcessingResult processTransaction(
 
       final Wei upfrontGasCost =
           transaction.getUpfrontGasCost(transactionGasPrice, blobGasPrice, blobGas);
-      final Wei previousBalance = sender.decrementBalance(upfrontGasCost);
-      LOG.trace(
-          "Deducted sender {} upfront gas cost {} ({} -> {})",
-          senderAddress,
-          upfrontGasCost,
-          previousBalance,
-          sender.getBalance());
+      try {
+        final Wei previousBalance = sender.decrementBalance(upfrontGasCost);
+        LOG.trace(
+            "Deducted sender {} upfront gas cost {} ({} -> {})",
+            senderAddress,
+            upfrontGasCost,
+            previousBalance,
+            sender.getBalance());
+      } catch (final IllegalStateException ise) {
+        if (transactionValidationParams.allowUnderpriced()) {
+          LOG.trace("Allowing account balance underflow as requested");
+        } else {
+          throw ise;
+        }
+      }
 
       long codeDelegationRefund = 0L;
       if (transaction.getType().equals(TransactionType.DELEGATE_CODE)) {
```
