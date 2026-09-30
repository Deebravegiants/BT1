# [?] fix: overflow protection for BlakeRounds precompile limits count (#1817)

## Summary
Severity: Unknown
Chain: Linea
Component: LFDT-Lineth/lineth-monorepo
Published: 2025-02-17
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/1264ac1176f527eca74d44d06fd7ab969924aab3
Type: security-commit

## Details
fix: overflow protection for BlakeRounds precompile limits count (#1817)

## Patch
### tracer/arithmetization/src/main/java/net/consensys/linea/zktracer/module/blake2fmodexpdata/BlakeModexpData.java
```diff
@@ -63,7 +63,7 @@ public void callModexp(final ModexpMetadata modexpMetaData, final int operationI
   public void callBlake(final BlakeComponents blakeComponents, final int operationID) {
     operations.add(new BlakeModexpDataOperation(blakeComponents, operationID));
     blakeEffectiveCall.addPrecompileLimit(1);
-    blakeRounds.addPrecompileLimit(blakeComponents.r().toInt());
+    blakeRounds.addPrecompileLimit(blakeComponents.r());
     callWcpForIdCheck(operationID);
   }
 
```

### tracer/arithmetization/src/main/java/net/consensys/linea/zktracer/module/blake2fmodexpdata/BlakeModexpDataOperation.java
```diff
@@ -53,7 +53,8 @@ public class BlakeModexpDataOperation extends ModuleOperation {
           + (INDEX_MAX_MODEXP_RESULT + 1);
   private static final int BLAKE2f_COMPONENTS_LINE_COUNT =
       (INDEX_MAX_BLAKE_DATA + 1) + (INDEX_MAX_BLAKE_PARAMS + 1) + (INDEX_MAX_BLAKE_RESULT + 1);
-  public static final short BLAKE2f_HASH_INPUT_OFFSET = 4;
+  public static final short BLAKE2f_R_SIZE = 4;
+  public static final short BLAKE2f_HASH_INPUT_OFFSET = BLAKE2f_R_SIZE;
   public static final short BLAKE2f_HASH_INPUT_SIZE = LLARGE * (INDEX_MAX_BLAKE_DATA + 1);
   public static final short BLAKE2f_HASH_OUTPUT_SIZE = LLARGE * (INDEX_MAX_BLAKE_RESULT + 1);
 
```

### tracer/arithmetization/src/main/java/net/consensys/linea/zktracer/module/hub/section/call/precompileSubsection/BlakeSubsection.java
```diff
@@ -16,6 +16,7 @@
 package net.consensys.linea.zktracer.module.hub.section.call.precompileSubsection;
 
 import static com.google.common.base.Preconditions.checkArgument;
+import static net.consensys.linea.zktracer.module.blake2fmodexpdata.BlakeModexpDataOperation.BLAKE2f_R_SIZE;
 import static net.consensys.linea.zktracer.module.hub.fragment.scenario.PrecompileScenarioFragment.PrecompileScenario.PRC_FAILURE_KNOWN_TO_HUB;
 import static net.consensys.linea.zktracer.module.hub.fragment.scenario.PrecompileScenarioFragment.PrecompileScenario.PRC_FAILURE_KNOWN_TO_RAM;
 
@@ -110,10 +111,13 @@ public void resolveAtContextReEntry(Hub hub, CallFrame callFrame) {
     }
 
     // TODO: make it smarter
-    Bytes callData = getCallDataRange().extract();
+    final Bytes callData = getCallDataRange().extract();
     final BlakeComponents blake2f =
         new BlakeComponents(
-            callData, callData.slice(0, 4), callData.slice(212, 1), extractReturnData());
+            callData,
+            callData.slice(0, BLAKE2f_R_SIZE),
+            callData.slice(212, 1),
+            extractReturnData());
     hub.blakeModexpData().callBlake(blake2f, this.exoModuleOperationId());
   }
 
```

### tracer/arithmetization/src/main/java/net/consensys/linea/zktracer/module/limits/precompiles/BlakeRounds.java
```diff
@@ -15,18 +15,67 @@
 
 package net.consensys.linea.zktracer.module.limits.precompiles;
 
+import static java.lang.Integer.MAX_VALUE;
+import static net.consensys.linea.zktracer.module.blake2fmodexpdata.BlakeModexpDataOperation.BLAKE2f_R_SIZE;
+
+import java.math.BigInteger;
+
+import com.google.common.base.Preconditions;
 import lombok.Getter;
+import lombok.Setter;
 import lombok.experimental.Accessors;
 import net.consensys.linea.zktracer.container.module.CountingOnlyModule;
 import net.consensys.linea.zktracer.container.stacked.CountOnlyOperation;
+import org.apache.tuweni.bytes.Bytes;
 
 @Getter
 @Accessors(fluent = true)
 public final class BlakeRounds implements CountingOnlyModule {
   private final CountOnlyOperation counts = new CountOnlyOperation();
+  @Setter private boolean transactionBundleContainsIllegalOperation = false;
+
+  private static final BigInteger INTEGER_MAX_VALUE_BI = BigInteger.valueOf(MAX_VALUE);
 
   @Override
   public String moduleKey() {
     return "PRECOMPILE_BLAKE_ROUNDS";
   }
+
+  @Override
+  public void addPrecompileLimit(final int count) {
+    throw new UnsupportedOperationException("Not implemented");
+  }
+
+  public void addPrecompileLimit(final Bytes r) {
+    Preconditions.checkArgument(r.size() == BLAKE2f_R_SIZE, "r is 4 bytes long");
+    final BigInteger rBI = r.toUnsignedBigInteger();
+    // check if r is greater or equal to Integer.MAX_VALUE
+    if (rBI.compareTo(INTEGER_MAX_VALUE_BI) >= 0) {
+      transactionBundleContainsIllegalOperation(true);
+      return;
+    }
+
+    // check if the new lineCount would be greater or equal than Integer.MAX_VALUE
+    final BigInteger totalRoundsCount = BigInteger.valueOf(counts.lineCount());
+    if (rBI.add(totalRoundsCount).compareTo(INTEGER_MAX_VALUE_BI) >= 0) {
+      transactionBundleContainsIllegalOperation(true);
+      return;
+    }
+
+    // Then, as no overflow, add the count
+    counts.add(rBI.intValueExact());
+  }
+
+  @Override
+  public int lineCount() {
+    return transactionBundleContainsIllegalOperation
+        ? MAX_VALUE
+        : CountingOnlyModule.super.lineCount();
+  }
+
+  @Override
+  public void popTransactionBundle() {
+    CountingOnlyModule.super.popTransactionBundle();
+    transactionBundleContainsIllegalOperation(false);
+  }
 }
```

### tracer/arithmetization/src/test/java/net/consensys/linea/zktracer/module/precompileLimits/BlakeRoundsTests.java
```diff
@@ -0,0 +1,100 @@
+/*
+ * Copyright ConsenSys Inc.
+ *
+ * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
+ * the License. You may obtain a copy of the License at
+ *
+ * http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
+ * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
+ * specific language governing permissions and limitations under the License.
+ *
+ * SPDX-License-Identifier: Apache-2.0
+ */
+
+package net.consensys.linea.zktracer.module.precompileLimits;
+
+import static java.lang.Integer.MAX_VALUE;
+import static net.consensys.linea.zktracer.module.blake2fmodexpdata.BlakeModexpDataOperation.BLAKE2f_R_SIZE;
+import static net.consensys.linea.zktracer.types.Utils.leftPadTo;
+import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
+
+import net.consensys.linea.zktracer.ZkTracer;
+import net.consensys.linea.zktracer.module.limits.precompiles.BlakeRounds;
+import org.apache.tuweni.bytes.Bytes;
+import org.junit.jupiter.api.Test;
+
+public class BlakeRoundsTests {
+
+  private static final Bytes ONE = leftPadTo(Bytes.minimalBytes(1), BLAKE2f_R_SIZE);
+  private static final Bytes ZERO = leftPadTo(Bytes.minimalBytes(0), BLAKE2f_R_SIZE);
+  private static final Bytes MAX_INTEGER = leftPadTo(Bytes.minimalBytes(MAX_VALUE), BLAKE2f_R_SIZE);
+  private static final Bytes MAX_INTEGER_MO =
+      leftPadTo(Bytes.minimalBytes(MAX_VALUE - 1), BLAKE2f_R_SIZE);
+  private static final Bytes MAX_INTEGER_PO =
+      leftPadTo(Bytes.minimalBytes((long) MAX_VALUE + 1), BLAKE2f_R_SIZE);
+
+  @Test
+  void checkWoCommit() {
+    final ZkTracer state = new ZkTracer();
+    final BlakeRounds blakeRounds = state.getHub().blakeModexpData().blakeRounds();
+
+    blakeRounds.addPrecompileLimit(ONE);
+    assertThat(blakeRounds.lineCount()).isEqualTo(1);
+
+    blakeRounds.addPrecompileLimit(ZERO);
+    assertThat(blakeRounds.lineCount()).isEqualTo(1);
+
+    blakeRounds.addPrecompileLimit(MAX_INTEGER);
+    assertThat(blakeRounds.lineCount()).isEqualTo(MAX_VALUE);
+
+    blakeRounds.addPrecompileLimit(MAX_INTEGER_MO);
+    assertThat(blakeRounds.lineCount()).isEqualTo(MAX_VALUE);
+
+    blakeRounds.popTransactionBundle();
+    assertThat(blakeRounds.lineCount()).isEqualTo(0);
+
+    blakeRounds.addPrecompileLimit(MAX_INTEGER_MO);
+    assertThat(blakeRounds.lineCount()).isEqualTo(MAX_INTEGER_MO.toInt());
+
+    blakeRounds.popTransactionBundle();
+    assertThat(blakeRounds.lineCount()).isEqualTo(0);
+
+    blakeRounds.addPrecompileLimit(MAX_INTEGER_PO);
+    assertThat(blakeRounds.lineCount()).isEqualTo(MAX_VALUE);
+  }
+
+  @Test
+  void checkWithCommit() {
+    final ZkTracer state = new ZkTracer();
+    final BlakeRounds blakeRounds = state.getHub().blakeModexpData().blakeRounds();
+
+    blakeRounds.addPrecompileLimit(ONE);
+    assertThat(blakeRounds.lineCount()).isEqualTo(1);
+
+    blakeRounds.commitTransactionBundle();
+    assertThat(blakeRounds.lineCount()).isEqualTo(1);
+
+    blakeRounds.addPrecompileLimit(MAX_INTEGER);
+    assertThat(blakeRounds.lineCount()).isEqualTo(MAX_VALUE);
+    blakeRounds.popTransactionBundle();
+    assertThat(blakeRounds.lineCount()).isEqualTo(1);
+
+    blakeRounds.addPrecompileLimit(MAX_INTEGER_MO);
+    assertThat(blakeRounds.lineCount()).isEqualTo(MAX_VALUE);
+    blakeRounds.popTransactionBundle();
+    assertThat(blakeRounds.lineCount()).isEqualTo(1);
+
+    blakeRounds.addPrecompileLimit(MAX_INTEGER_PO);
+    assertThat(blakeRounds.lineCount()).isEqualTo(MAX_VALUE);
+    blakeRounds.popTransactionBundle();
+    assertThat(blakeRounds.lineCount()).isEqualTo(1);
+
+    blakeRounds.addPrecompileLimit(ONE);
+    assertThat(blakeRounds.lineCount()).isEqualTo(2);
+
+    blakeRounds.commitTransactionBundle();
+    assertThat(blakeRounds.lineCount()).isEqualTo(2);
+  }
+}
```

### tracer/arithmetization/src/test/java/net/consensys/linea/zktracer/module/precompileLimits/ModexpIllegalOperationTests.java
```diff
@@ -13,7 +13,7 @@
  * SPDX-License-Identifier: Apache-2.0
  */
 
-package net.consensys.linea.zktracer.containers;
+package net.consensys.linea.zktracer.module.precompileLimits;
 
 import static java.lang.Integer.MAX_VALUE;
 import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
```
