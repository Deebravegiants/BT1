# [?] Added extra constraints to disallow out of bounds memory reads/write (#32).

## Summary
Severity: Unknown
Chain: ZK
Component: risc0/risc0
Published: 2022-03-30
Source: https://github.com/risc0/risc0/commit/6d2c29019bc1d7ea071afe1d7f17e6264c682a67
Type: security-commit

## Details
Added extra constraints to disallow out of bounds memory reads/write (#32).

Previously upper bits of the address were ignored for memory access.  For correct code this doesn't cause problems, but it's allowing undefined behavior.  It seems that earlier termination is probably preferable.

## Patch
### risc0/r0vm/circuit/compute_cycle.cpp
```diff
@@ -121,6 +121,7 @@ void ComputeCycle::set(StepState& state, int highID) {
       Value cycle = state.code.cycle.get();                                                        \
       if (doLoad) {                                                                                \
         state.data.memIO.doRead(cycle, x1.getPart(2, kMemBits));                                   \
+        equate(x1.getPart(2 + kMemBits, 32 - kMemBits - 2), 0);                                    \
       } else {                                                                                     \
         state.data.memIO.doRead(cycle, 0);                                                         \
       }                                                                                            \
```

### risc0/r0vm/circuit/final_cycle.cpp
```diff
@@ -28,6 +28,7 @@ void FinalCycle::set(StepState& state) {
   BYZ_IF(resultInfo.doStore.get()) {
     Value isWOM = compute.x1.get(kMemBits + 1);
     Value memAddr = compute.x1.getPart(2, kMemBits);
+    equate(compute.x1.getPart(2 + kMemBits, 32 - kMemBits - 2), 0);
     state.data.memIO.doWrite(cycle, memAddr, result, isWOM);
   }
   BYZ_IF(1 - resultInfo.doStore.get()) { state.data.memIO.doRead(cycle); }
```

### risc0/r0vm/prove/test/BUILD.bazel
```diff
@@ -7,12 +7,19 @@ cc_gtest(
         "hw.cpp",
     ],
     data = [
+        ":test_invalid_addr",
         ":test_wom_diff",
         ":test_wom_same",
     ],
     deps = ["//risc0/r0vm/prove"],
 )
 
+risc0_cc_binary(
+    name = "test_invalid_addr",
+    srcs = ["test_invalid_addr.cpp"],
+    deps = ["//risc0/r0vm/cpp/device"],
+)
+
 risc0_cc_binary(
     name = "test_wom_diff",
     srcs = ["test_wom_diff.cpp"],
@@ -24,3 +31,4 @@ risc0_cc_binary(
     srcs = ["test_wom_same.cpp"],
     deps = ["//risc0/r0vm/cpp/device"],
 )
+
```

### risc0/r0vm/prove/test/hw.cpp
```diff
@@ -44,6 +44,8 @@ TEST(Step, HW) {
   run("test_wom_same");
   // Verify writes to WOM with different values fail
   ASSERT_THROW(run("test_wom_diff"), std::runtime_error);
+  // Verify out of bound accesses fail
+  ASSERT_THROW(run("test_invalid_addr"), std::runtime_error);
 }
 
 } // namespace risc0
```

### risc0/r0vm/prove/test/test_invalid_addr.cpp
```diff
@@ -0,0 +1,22 @@
+// Copyright 2022 Risc0, Inc.
+//
+// Licensed under the Apache License, Version 2.0 (the "License");
+// you may not use this file except in compliance with the License.
+// You may obtain a copy of the License at
+//
+//     http://www.apache.org/licenses/LICENSE-2.0
+//
+// Unless required by applicable law or agreed to in writing, software
+// distributed under the License is distributed on an "AS IS" BASIS,
+// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
+// See the License for the specific language governing permissions and
+// limitations under the License.
+
+#include "risc0/r0vm/cpp/device/risc0.h"
+
+using namespace risc0;
+
+extern "C" void risc0_main(Env* env) {
+  volatile uint32_t* addr = reinterpret_cast<uint32_t*>(0xffff0000);
+  *addr = 0;
+}
```
