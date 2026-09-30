# [?] fix: invalid signature state leak (#13868)

## Summary
Severity: Unknown
Chain: Hedera
Component: hiero-ledger/hiero-consensus-node
Published: 2024-06-17
Source: https://github.com/hiero-ledger/hiero-consensus-node/commit/857a356e434f220725dcea68d9e3d07a31b6261a
Type: security-commit

## Details
fix: invalid signature state leak (#13868)

Signed-off-by: Lazar Petrovic <lpetrovic05@gmail.com>

## Patch
### platform-sdk/swirlds-platform-core/src/main/java/com/swirlds/platform/reconnect/ReconnectLearner.java
```diff
@@ -152,15 +152,21 @@ private void resetSocketTimeout() throws ReconnectException {
     @NonNull
     public ReservedSignedState execute(@NonNull final SignedStateValidator validator) throws ReconnectException {
         increaseSocketTimeout();
+        ReservedSignedState reservedSignedState = null;
         try {
             receiveSignatures();
-            final ReservedSignedState reservedSignedState = reconnect();
+            reservedSignedState = reconnect();
             validator.validate(reservedSignedState.get(), addressBook, stateValidationData);
             ReconnectUtils.endReconnectHandshake(connection);
             return reservedSignedState;
         } catch (final IOException | SignedStateInvalidException e) {
+            if (reservedSignedState != null) {
+                // if the state was received, we need to release it or it will be leaked
+                reservedSignedState.close();
+            }
             throw new ReconnectException(e);
         } catch (final InterruptedException e) {
+            // an interrupt can only occur in the reconnect() method, so we don't need to close the reservedSignedState
             Thread.currentThread().interrupt();
             throw new ReconnectException("interrupted while attempting to reconnect", e);
         } finally {
```
