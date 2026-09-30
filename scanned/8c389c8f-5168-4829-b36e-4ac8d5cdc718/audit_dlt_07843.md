# [?] Fix deadlock and another bug in TaskQueue (#9846)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys-Incorporated/teku
Published: 2025-09-04
Source: https://github.com/Consensys-Incorporated/teku/commit/7569ff25f4facc4b6a434bc9ea4877c55cebc6ee
Type: security-commit

## Details
Fix deadlock and another bug in TaskQueue (#9846)

* fix deadlock

* fix compile

## Patch
### infrastructure/async/src/main/java/tech/pegasys/teku/infrastructure/async/LimitedTaskQueue.java
```diff
@@ -13,6 +13,7 @@
 
 package tech.pegasys.teku.infrastructure.async;
 
+import com.google.common.annotations.VisibleForTesting;
 import java.util.concurrent.RejectedExecutionException;
 import java.util.function.Supplier;
 import org.hyperledger.besu.plugin.services.MetricsSystem;
@@ -61,21 +62,24 @@ private LimitedTaskQueue(final TaskQueue delegate, final int maximumQueueSize) {
   }
 
   @Override
-  public synchronized <T> SafeFuture<T> queueTask(final Supplier<SafeFuture<T>> request) {
-    if (delegate.getQueuedTasksCount() >= maximumQueueSize) {
-      rejectedTaskCount++;
-      return SafeFuture.failedFuture(new QueueIsFullException());
+  public <T> SafeFuture<T> queueTask(final Supplier<SafeFuture<T>> request) {
+    synchronized (delegate) {
+      if (delegate.getQueuedTasksCount() >= maximumQueueSize) {
+        rejectedTaskCount++;
+        return SafeFuture.failedFuture(new QueueIsFullException());
+      }
+      return delegate.queueTask(request);
     }
-    return delegate.queueTask(request);
   }
 
   @Override
-  public synchronized int getQueuedTasksCount() {
+  public int getQueuedTasksCount() {
     return delegate.getQueuedTasksCount();
   }
 
+  @VisibleForTesting
   @Override
-  public synchronized int getInflightTaskCount() {
+  public int getInflightTaskCount() {
     return delegate.getInflightTaskCount();
   }
 }
```

### infrastructure/async/src/main/java/tech/pegasys/teku/infrastructure/async/TaskQueue.java
```diff
@@ -21,6 +21,7 @@ public interface TaskQueue {
 
   int getQueuedTasksCount();
 
+  /** This must only be used for testing to verify that throttling is working as expected. */
   @VisibleForTesting
   int getInflightTaskCount();
 }
```

### infrastructure/async/src/main/java/tech/pegasys/teku/infrastructure/async/ThrottlingTaskQueue.java
```diff
@@ -62,7 +62,14 @@ public <T> SafeFuture<T> queueTask(final Supplier<SafeFuture<T>> request) {
   protected <T> Runnable getTaskToQueue(
       final Supplier<SafeFuture<T>> request, final SafeFuture<T> target) {
     return () -> {
-      final SafeFuture<T> requestFuture = request.get();
+      final SafeFuture<T> requestFuture;
+      try {
+        requestFuture = request.get();
+      } catch (final Exception e) {
+        target.completeExceptionally(e);
+        taskComplete();
+        return;
+      }
       requestFuture.propagateTo(target);
       requestFuture.always(this::taskComplete);
     };
@@ -86,7 +93,7 @@ public int getQueuedTasksCount() {
 
   @VisibleForTesting
   @Override
-  public int getInflightTaskCount() {
+  public synchronized int getInflightTaskCount() {
     return inflightTaskCount;
   }
 
```

### infrastructure/async/src/test/java/tech/pegasys/teku/infrastructure/async/ThrottlingTaskQueueTest.java
```diff
@@ -14,6 +14,7 @@
 package tech.pegasys.teku.infrastructure.async;
 
 import static org.assertj.core.api.Assertions.assertThat;
+import static tech.pegasys.teku.infrastructure.async.SafeFutureAssert.assertThatSafeFuture;
 
 import java.util.List;
 import java.util.concurrent.CompletableFuture;
@@ -78,6 +79,22 @@ public void throttlesRequests() {
     checkQueueProgress(requests, 0, 0, 10);
   }
 
+  @Test
+  public void shouldFailTaskIfSupplierThrows() {
+    taskQueue = createThrottlingTaskQueue();
+
+    final RuntimeException error = new RuntimeException("Test exception");
+
+    final SafeFuture<Void> request =
+        taskQueue.queueTask(
+            () -> {
+              throw error;
+            });
+
+    assertThatSafeFuture(request).isCompletedExceptionallyWith(error);
+    checkQueueProgress(List.of(request), 0, 0, 1);
+  }
+
   protected void checkQueueProgress(
       final List<SafeFuture<Void>> requests,
       final int queueSize,
```
