# [?] fix: 25225 Fix race condition in EntityIdUniquenessValidator  (#25226)

## Summary
Severity: Unknown
Chain: Hedera
Component: hiero-ledger/hiero-consensus-node
Published: 2026-05-04
Source: https://github.com/hiero-ledger/hiero-consensus-node/commit/2f6501d061ec3ccc2cf8e3ec0f2941d32f0a04ce
Type: security-commit

## Details
fix: 25225 Fix race condition in EntityIdUniquenessValidator  (#25226)

Signed-off-by: Ivan Malygin <ivan@swirldslabs.com>

## Patch
### hedera-state-validator/src/main/java/com/hedera/statevalidation/validator/EntityIdUniquenessValidator.java
```diff
@@ -35,6 +35,7 @@
 import edu.umd.cs.findbugs.annotations.NonNull;
 import java.util.Objects;
 import java.util.concurrent.atomic.AtomicLong;
+import java.util.concurrent.locks.ReentrantReadWriteLock;
 import org.apache.logging.log4j.LogManager;
 import org.apache.logging.log4j.Logger;
 
@@ -59,6 +60,8 @@ public class EntityIdUniquenessValidator implements LeafBytesValidator {
     private final AtomicLong idCounter = new AtomicLong(0);
     private final AtomicLong issuesFound = new AtomicLong(0);
 
+    private final ReentrantReadWriteLock cacheLock = new ReentrantReadWriteLock();
+
     /**
      * {@inheritDoc}
      */
@@ -152,69 +155,78 @@ public void validate() {
     private void checkEntityUniqueness(long entityId) {
         // From time to time we need to reset cache to prevent OOM errors
         if (idCounter.incrementAndGet() % 100_000 == 0) {
-            StateUtils.resetStateCache();
-        }
-
-        int counter = 0;
-        final Token token = tokensState.get(new TokenID(0, 0, entityId));
-        if (token != null) {
-            counter++;
-        }
-
-        final Account account =
-                accountState.get(AccountID.newBuilder().accountNum(entityId).build());
-        if (account != null) {
-            counter++;
+            cacheLock.writeLock().lock();
+            try {
+                StateUtils.resetStateCache();
+            } finally {
+                cacheLock.writeLock().unlock();
+            }
         }
+        cacheLock.readLock().lock();
+        try {
+            int counter = 0;
+            final Token token = tokensState.get(new TokenID(0, 0, entityId));
+            if (token != null) {
+                counter++;
+            }
 
-        final Bytecode contract = smartContractState.get(
-                ContractID.newBuilder().contractNum(entityId).build());
+            final Account account =
+                    accountState.get(AccountID.newBuilder().accountNum(entityId).build());
+            if (account != null) {
+                counter++;
+            }
 
-        if (contract != null) {
-            counter++;
-        }
+            final Bytecode contract = smartContractState.get(
+                    ContractID.newBuilder().contractNum(entityId).build());
 
-        final Topic topic =
-                topicState.get(TopicID.newBuilder().topicNum(entityId).build());
+            if (contract != null) {
+                counter++;
+            }
 
-        if (topic != null) {
-            counter++;
-        }
+            final Topic topic =
+                    topicState.get(TopicID.newBuilder().topicNum(entityId).build());
 
-        final File file = fileState.get(FileID.newBuilder().fileNum(entityId).build());
-        if (file != null) {
-            counter++;
-        }
+            if (topic != null) {
+                counter++;
+            }
 
-        final Schedule schedule = scheduleState.get(new ScheduleID(0, 0, entityId));
-        if (schedule != null) {
-            counter++;
-        }
+            final File file =
+                    fileState.get(FileID.newBuilder().fileNum(entityId).build());
+            if (file != null) {
+                counter++;
+            }
 
-        if (counter == 0) {
-            final String errorMessage = String.format("No entity found for Entity ID %d", entityId);
-            log.error(errorMessage);
-            issuesFound.incrementAndGet();
-        }
-        if (counter > 1) {
-            if ((account != null) && (contract != null) && (counter == 2)) {
-                // if it's a smart contract account, we expect it to have a contract with matching id
-                return;
+            final Schedule schedule = scheduleState.get(new ScheduleID(0, 0, entityId));
+            if (schedule != null) {
+                counter++;
+            }
+            if (counter == 0) {
+                final String errorMessage = String.format("No entity found for Entity ID %d", entityId);
+                log.error(errorMessage);
+                issuesFound.incrementAndGet();
             }
+            if (counter > 1) {
+                if ((account != null) && (contract != null) && (counter == 2)) {
+                    // if it's a smart contract account, we expect it to have a contract with matching id
+                    return;
+                }
 
-            final String errorMessage =
-                    String.format("""
-            Entity ID %d is not unique, found %d entities.\s
-             Token = %s, \
-            \s
-             Account = %s,\s
-             Contract = %s, \s
-             Topic = %s,\s
-             File = %s,\s
-             Schedule = %s
-            """, entityId, counter, token, account, contract, topic, file, schedule);
-            log.error(errorMessage);
-            issuesFound.incrementAndGet();
+                final String errorMessage =
+                        String.format("""
+                                      Entity ID %d is not unique, found %d entities.\s
+                                       Token = %s, \
+                                      \s
+                                       Account = %s,\s
+                                       Contract = %s, \s
+                                       Topic = %s,\s
+                                       File = %s,\s
+                                       Schedule = %s
+                          """, entityId, counter, token, account, contract, topic, file, schedule);
+                log.error(errorMessage);
+                issuesFound.incrementAndGet();
+            }
+        } finally {
+            cacheLock.readLock().unlock();
         }
     }
 }
```
