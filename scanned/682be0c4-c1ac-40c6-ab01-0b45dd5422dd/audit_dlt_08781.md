# [?] Protect `MODEXP` line counting from integer overflows (#1813)

## Summary
Severity: Unknown
Chain: Linea
Component: LFDT-Lineth/lineth-monorepo
Published: 2025-02-14
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/3aa251b3a962d323b01b50a75e3d6d3714d80ac0
Type: security-commit

## Details
Protect `MODEXP` line counting from integer overflows (#1813)

## Patch
### tracer/arithmetization/src/main/java/net/consensys/linea/zktracer/container/stacked/CountOnlyOperation.java
```diff
@@ -37,7 +37,7 @@ public void popTransactionBundle() {
   }
 
   public void add(final int operationCount) {
-    Preconditions.checkArgument(operationCount >= 0, "operationCount must be positive");
+    Preconditions.checkArgument(operationCount >= 0, "operationCount must be non negative");
     countInTransactionBundle += operationCount;
   }
 
```

### tracer/arithmetization/src/main/java/net/consensys/linea/zktracer/module/limits/precompiles/ModexpEffectiveCall.java
```diff
@@ -15,9 +15,12 @@
 
 package net.consensys.linea.zktracer.module.limits.precompiles;
 
+import static java.lang.Integer.MAX_VALUE;
+
 import com.google.common.base.Preconditions;
 import lombok.Getter;
 import lombok.RequiredArgsConstructor;
+import lombok.Setter;
 import lombok.experimental.Accessors;
 import lombok.extern.slf4j.Slf4j;
 import net.consensys.linea.zktracer.container.module.CountingOnlyModule;
@@ -29,6 +32,7 @@
 @Accessors(fluent = true)
 public class ModexpEffectiveCall implements CountingOnlyModule {
   private final CountOnlyOperation counts = new CountOnlyOperation();
+  @Setter private boolean transactionBundleContainsIllegalOperation = false;
 
   @Override
   public String moduleKey() {
@@ -38,8 +42,25 @@ public String moduleKey() {
   @Override
   public void addPrecompileLimit(final int count) {
     Preconditions.checkArgument(
-        count == 1 || count == Integer.MAX_VALUE,
+        count == 1 || count == MAX_VALUE,
         "Either use 1 for one effective precompile call at a time or use Integer.MAX_VALUE");
+    if (count == MAX_VALUE) {
+      transactionBundleContainsIllegalOperation(true);
+      return;
+    }
     counts.add(count);
   }
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

### tracer/arithmetization/src/test/java/net/consensys/linea/zktracer/containers/ModexpIllegalOperationTests.java
```diff
@@ -0,0 +1,74 @@
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
+package net.consensys.linea.zktracer.containers;
+
+import static java.lang.Integer.MAX_VALUE;
+import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
+
+import net.consensys.linea.zktracer.ZkTracer;
+import net.consensys.linea.zktracer.module.limits.precompiles.ModexpEffectiveCall;
+import org.junit.jupiter.api.Test;
+
+public class ModexpIllegalOperationTests {
+  @Test
+  void legalThenTwoIllegals() {
+    final ZkTracer state = new ZkTracer();
+    final ModexpEffectiveCall countingOnlyModule = state.getHub().modexpEffectiveCall();
+
+    countingOnlyModule.addPrecompileLimit(1);
+
+    countingOnlyModule.addPrecompileLimit(MAX_VALUE);
+    assertThat(countingOnlyModule.lineCount()).isEqualTo(MAX_VALUE);
+
+    countingOnlyModule.addPrecompileLimit(MAX_VALUE);
+    assertThat(countingOnlyModule.lineCount()).isEqualTo(MAX_VALUE);
+
+    countingOnlyModule.popTransactionBundle();
+    assertThat(countingOnlyModule.lineCount()).isEqualTo(0);
+  }
+
+  @Test
+  void legalIllegalLegal() {
+    final ZkTracer state = new ZkTracer();
+    final ModexpEffectiveCall countingOnlyModule = state.getHub().modexpEffectiveCall();
+
+    countingOnlyModule.addPrecompileLimit(1);
+
+    countingOnlyModule.addPrecompileLimit(MAX_VALUE);
+    assertThat(countingOnlyModule.lineCount()).isEqualTo(MAX_VALUE);
+
+    countingOnlyModule.addPrecompileLimit(1);
+    assertThat(countingOnlyModule.lineCount()).isEqualTo(MAX_VALUE);
+
+    countingOnlyModule.popTransactionBundle();
+    assertThat(countingOnlyModule.lineCount()).isEqualTo(0);
+  }
+
+  @Test
+  void TwoIllegals() {
+    final ZkTracer state = new ZkTracer();
+    final ModexpEffectiveCall countingOnlyModule = state.getHub().modexpEffectiveCall();
+
+    countingOnlyModule.addPrecompileLimit(MAX_VALUE);
+    assertThat(countingOnlyModule.lineCount()).isEqualTo(MAX_VALUE);
+
+    countingOnlyModule.addPrecompileLimit(MAX_VALUE);
+    assertThat(countingOnlyModule.lineCount()).isEqualTo(MAX_VALUE);
+
+    countingOnlyModule.popTransactionBundle();
+    assertThat(countingOnlyModule.lineCount()).isEqualTo(0);
+  }
+}
```
