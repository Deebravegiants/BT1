# [?] fix: do not overflow when reading logs payload

## Summary
Severity: Unknown
Chain: Linea
Component: LFDT-Lineth/lineth-monorepo
Published: 2024-02-29
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/2abbb2e9b826626ec2d7bab4a349f162b74cca13
Type: security-commit

## Details
fix: do not overflow when reading logs payload

## Patch
### tracer/arithmetization/src/main/java/net/consensys/linea/zktracer/module/hub/transients/OperationAncillaries.java
```diff
@@ -34,6 +34,21 @@
 public class OperationAncillaries {
   private final Hub hub;
 
+  private static Bytes maybeShadowReadMemory(final MemorySpan span, final MessageFrame frame) {
+    // Accesses to huge offset with 0-length are valid
+    if (span.isEmpty()) {
+      return Bytes.EMPTY;
+    }
+
+    // Besu is limited to i32 for memory offset/length
+    if (span.besuOverflow()) {
+      log.warn("Overflowing memory access: {}", span);
+      return Bytes.EMPTY;
+    }
+
+    return frame.shadowReadMemory(span.offset(), span.length());
+  }
+
   /**
    * Compute the gas allowance for the child context if in a CALL, throws otherwise.
    *
@@ -106,7 +121,7 @@ public MemorySpan callDataSegment() {
    */
   public Bytes callData() {
     final MemorySpan callDataSegment = callDataSegment();
-    return hub.messageFrame().shadowReadMemory(callDataSegment.offset(), callDataSegment.length());
+    return maybeShadowReadMemory(callDataSegment, hub.messageFrame());
   }
 
   /**
@@ -117,7 +132,7 @@ public Bytes callData() {
    */
   public static Bytes callData(final MessageFrame frame) {
     final MemorySpan callDataSegment = callDataSegment(frame);
-    return frame.shadowReadMemory(callDataSegment.offset(), callDataSegment.length());
+    return maybeShadowReadMemory(callDataSegment, frame);
   }
 
   /**
@@ -202,8 +217,7 @@ public Bytes returnData() {
       return Bytes.EMPTY;
     }
 
-    return hub.messageFrame()
-        .shadowReadMemory(returnDataSegment.offset(), returnDataSegment.length());
+    return maybeShadowReadMemory(returnDataSegment, hub.messageFrame());
   }
 
   /**
@@ -215,6 +229,24 @@ public Bytes returnData() {
    */
   public static Bytes returnData(final MessageFrame frame) {
     final MemorySpan returnDataSegment = returnDataSegment(frame);
-    return frame.shadowReadMemory(returnDataSegment.offset(), returnDataSegment.length());
+    return maybeShadowReadMemory(returnDataSegment, frame);
+  }
+
+  public static MemorySpan logDataSegment(final MessageFrame frame) {
+    long offset = Words.clampedToLong(frame.getStackItem(0));
+    long length = Words.clampedToLong(frame.getStackItem(1));
+    return MemorySpan.fromStartLength(offset, length);
+  }
+
+  public MemorySpan logDataSegment() {
+    return logDataSegment(this.hub.messageFrame());
+  }
+
+  public static Bytes logData(final MessageFrame frame) {
+    return maybeShadowReadMemory(logDataSegment(frame), frame);
+  }
+
+  public Bytes logData() {
+    return logData(this.hub.messageFrame());
   }
 }
```

### tracer/arithmetization/src/main/java/net/consensys/linea/zktracer/runtime/LogInvocation.java
```diff
@@ -22,7 +22,6 @@
 import net.consensys.linea.zktracer.module.hub.Hub;
 import net.consensys.linea.zktracer.runtime.callstack.CallStack;
 import org.apache.tuweni.bytes.Bytes;
-import org.hyperledger.besu.evm.internal.Words;
 
 @RequiredArgsConstructor
 public class LogInvocation {
@@ -33,9 +32,7 @@ public class LogInvocation {
 
   public static int forOpcode(final Hub hub) {
     final List<Bytes> topics = new ArrayList<>(4);
-    final long offset = Words.clampedToLong(hub.messageFrame().getStackItem(0));
-    final long size = Words.clampedToLong(hub.messageFrame().getStackItem(1));
-    final Bytes payload = hub.messageFrame().shadowReadMemory(offset, size);
+    final Bytes payload = hub.transients().op().logData();
     switch (hub.opCode()) {
       case LOG0 -> {}
       case LOG1 -> topics.add(hub.messageFrame().getStackItem(2));
```
