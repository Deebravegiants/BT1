# [?] Fix `handleError` and `handleSuccess` race condition (#7160)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys-Incorporated/teku
Published: 2023-05-19
Source: https://github.com/Consensys-Incorporated/teku/commit/d44d64f24b2b7ca42a228daaedba0bed41dd3e42
Type: security-commit

## Details
Fix `handleError` and `handleSuccess` race condition (#7160)

## Patch
### CHANGELOG.md
```diff
@@ -24,3 +24,5 @@ For information on changes in released versions of Teku, see the [releases page]
 - Add support for Chiado (Gnosis testnet): `--network=chiado`
 
 ### Bug Fixes
+
+- Fix a race condition on EL api result handling which may lead to beacon node remain syncing forever
\ No newline at end of file
```

### ethereum/executionclient/src/main/java/tech/pegasys/teku/ethereum/executionclient/web3j/Web3JClient.java
```diff
@@ -20,7 +20,6 @@
 import java.util.Collection;
 import java.util.HashSet;
 import java.util.concurrent.TimeoutException;
-import java.util.concurrent.atomic.AtomicLong;
 import org.web3j.protocol.Web3j;
 import org.web3j.protocol.Web3jService;
 import org.web3j.protocol.core.Request;
@@ -49,7 +48,7 @@ public abstract class Web3JClient {
 
   // Default to the provider having a previous failure at startup so we log when it is first
   // available but uses a very old value to make sure we log if the first request fails
-  private final AtomicLong lastError = new AtomicLong(STARTUP_LAST_ERROR_TIME);
+  private long lastErrorTime = STARTUP_LAST_ERROR_TIME;
   private boolean initialized = false;
 
   protected Web3JClient(
@@ -112,24 +111,24 @@ protected void handleError(final Throwable error, final boolean couldBeAuthError
     handleError(true, error, couldBeAuthError);
   }
 
-  protected void handleError(
+  protected synchronized void handleError(
       final boolean isCritical, final Throwable error, final boolean couldBeAuthError) {
     if (isCritical && shouldReportError()) {
       logExecutionClientError(error, couldBeAuthError);
       executionClientEventsPublisher.onAvailabilityUpdated(false);
     }
   }
 
-  protected void handleSuccess(final boolean isCriticalRequest) {
+  protected synchronized void handleSuccess(final boolean isCriticalRequest) {
     if (isCriticalRequest) {
-      final long lastErrorTime = lastError.getAndUpdate(x -> NO_ERROR_TIME);
       if (lastErrorTime == STARTUP_LAST_ERROR_TIME) {
         eventLog.executionClientIsOnline();
         executionClientEventsPublisher.onAvailabilityUpdated(true);
       } else if (lastErrorTime != NO_ERROR_TIME) {
         eventLog.executionClientRecovered();
         executionClientEventsPublisher.onAvailabilityUpdated(true);
       }
+      lastErrorTime = NO_ERROR_TIME;
     }
   }
 
@@ -157,17 +156,11 @@ private boolean isAuthenticationException(final Throwable exception) {
 
   private boolean shouldReportError() {
     final long timeNow = timeProvider.getTimeInMillis().longValue();
-    final long maybeUpdatedTime =
-        lastError.accumulateAndGet(
-            timeNow,
-            (lastErrorTime, givenErrorTimeUpdate) -> {
-              if (lastErrorTime == NO_ERROR_TIME
-                  || givenErrorTimeUpdate - lastErrorTime > ERROR_REPEAT_DELAY_MILLIS) {
-                return givenErrorTimeUpdate;
-              }
-              return lastErrorTime;
-            });
-    return maybeUpdatedTime == timeNow;
+    if (lastErrorTime == NO_ERROR_TIME || timeNow - lastErrorTime > ERROR_REPEAT_DELAY_MILLIS) {
+      lastErrorTime = timeNow;
+      return true;
+    }
+    return false;
   }
 
   private void logExecutionClientError(final Throwable error, final boolean couldBeAuthError) {
```
