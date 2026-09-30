# [?] Fix txpool dump/restore race condition (#6665)

## Summary
Severity: Unknown
Chain: Ethereum
Component: besu-eth/besu
Published: 2024-03-13
Source: https://github.com/besu-eth/besu/commit/efd1bc7070228786f1e1b02657a5fe2fe9cca743
Type: security-commit

## Details
Fix txpool dump/restore race condition (#6665)

Signed-off-by: Fabio Di Fabio <fabio.difabio@consensys.net>

## Patch
### CHANGELOG.md
```diff
@@ -22,6 +22,7 @@
 - Transaction call object to accept both `input` and `data` field simultaneously if they are set to equal values [#6702](https://github.com/hyperledger/besu/pull/6702)
 
 ### Bug fixes
+- Fix txpool dump/restore race condition [#6665](https://github.com/hyperledger/besu/pull/6665)
 - Make block transaction selection max time aware of PoA transitions [#6676](https://github.com/hyperledger/besu/pull/6676)
 - Don't enable the BFT mining coordinator when running sub commands such as `blocks export` [#6675](https://github.com/hyperledger/besu/pull/6675)
 
```

### ethereum/eth/src/main/java/org/hyperledger/besu/ethereum/eth/transactions/TransactionPool.java
```diff
@@ -64,12 +64,11 @@
 import java.util.concurrent.CompletableFuture;
 import java.util.concurrent.ConcurrentHashMap;
 import java.util.concurrent.ExecutionException;
+import java.util.concurrent.Semaphore;
 import java.util.concurrent.TimeUnit;
 import java.util.concurrent.TimeoutException;
 import java.util.concurrent.atomic.AtomicBoolean;
 import java.util.concurrent.atomic.AtomicReference;
-import java.util.concurrent.locks.Lock;
-import java.util.concurrent.locks.ReentrantLock;
 import java.util.function.Supplier;
 import java.util.stream.Collectors;
 import java.util.stream.Stream;
@@ -664,7 +663,7 @@ private void onAdded(final Transaction transaction) {
   }
 
   class SaveRestoreManager {
-    private final Lock diskAccessLock = new ReentrantLock();
+    private final Semaphore diskAccessLock = new Semaphore(1, true);
     private final AtomicReference<CompletableFuture<Void>> writeInProgress =
         new AtomicReference<>(CompletableFuture.completedFuture(null));
     private final AtomicReference<CompletableFuture<Void>> readInProgress =
@@ -685,25 +684,20 @@ private CompletableFuture<Void> serializeAndDedupOperation(
         final AtomicReference<CompletableFuture<Void>> operationInProgress) {
       if (configuration.getEnableSaveRestore()) {
         try {
-          if (diskAccessLock.tryLock(1, TimeUnit.MINUTES)) {
-            try {
-              if (!operationInProgress.get().isDone()) {
-                isCancelled.set(true);
-                try {
-                  operationInProgress.get().get();
-                } catch (ExecutionException ee) {
-                  // nothing to do
-                }
+          if (diskAccessLock.tryAcquire(1, TimeUnit.MINUTES)) {
+            if (!operationInProgress.get().isDone()) {
+              isCancelled.set(true);
+              try {
+                operationInProgress.get().get();
+              } catch (ExecutionException ee) {
+                // nothing to do
               }
-
-              isCancelled.set(false);
-              operationInProgress.set(CompletableFuture.runAsync(operation));
-              return operationInProgress.get();
-            } catch (InterruptedException ie) {
-              isCancelled.set(false);
-            } finally {
-              diskAccessLock.unlock();
             }
+
+            isCancelled.set(false);
+            operationInProgress.set(
+                CompletableFuture.runAsync(operation).thenRun(diskAccessLock::release));
+            return operationInProgress.get();
           } else {
             CompletableFuture.failedFuture(
                 new TimeoutException("Timeout waiting for disk access lock"));
```
