# [?] Fix a non-determinism bug in CUDA (#3451)

## Summary
Severity: Unknown
Chain: ZK
Component: risc0/risc0
Published: 2025-10-02
Source: https://github.com/risc0/risc0/commit/e04b7ae14e6b1152ace24da7fd31828e373a3283
Type: security-commit

## Details
Fix a non-determinism bug in CUDA (#3451)

## Patch
### risc0/circuit/rv32im-m3-sys/cxx/hal/cuda/hal.cpp
```diff
@@ -46,7 +46,7 @@ extern "C" bool cuda_zero_dev(void* buf, size_t size);
 // api.cu
 extern "C" SparkError sppark_poseidon2_fold(void* d_out, const void* d_in, size_t num_hashes);
 extern "C" SparkError sppark_poseidon2_rows(void* d_out, const void* d_in, uint32_t count, uint32_t col_size);
-extern "C" SparkError sppark_prefix_sum(void* d_inout, uint32_t count);
+extern "C" void prefix_sum(Fp* d_inout, uint32_t count);
 extern "C" SparkError supra_poly_divide(void* d_inout, size_t len, void* remainder, FpExt pow);
 
 // query.cu
@@ -290,10 +290,7 @@ class CudaHal : public IHal {
     size_t po2 = checkPo2(accum.rows());
     accum_witgen_cuda(toDevPtr(accum), toDevPtr(data), toDevPtr(globals), toDevPtr(accMix), risc0::ROU_FWD[po2], accum.rows());
     for (size_t i = 0; i < 4; i++) {
-      auto err = sppark_prefix_sum(toDevPtr(accum) + accum.rows() * i, accum.rows());
-      if (err.code != 0) {
-        throw std::runtime_error(std::string("Error during computeAccumWitness:") + err.message);
-      }
+      prefix_sum(toDevPtr(accum) + accum.rows() * i, accum.rows());
     }
   }
 
```

### risc0/circuit/rv32im-m3-sys/cxx/hal/cuda/kernels/api.cu
```diff
@@ -25,6 +25,9 @@
 #include "poseidon2.cuh"
 //#include "poseidon254.cuh"
 
+#include <thrust/execution_policy.h>
+#include <thrust/scan.h>
+
 extern "C" RustError::by_value
 sppark_poseidon2_fold(poseidon_out_t* d_out, const poseidon_in_t* d_in, size_t num_hashes) {
   const gpu_t& gpu = select_gpu();
@@ -153,18 +156,8 @@ sppark_poseidon254_rows(alt_bn128::fr_t* d_out, const fr_t* d_in, size_t count,
 
 #endif
 
-extern "C" RustError::by_value sppark_prefix_sum(fr_t d_inout[/*count*/], uint32_t count) {
-  const gpu_t& gpu = select_gpu();
-
-  try {
-    prefix_op<Add<fr_t>>(d_inout, count, gpu);
-    gpu.sync();
-  } catch (const cuda_error& e) {
-    gpu.sync();
-    return RustError{e.code(), e.what()};
-  }
-
-  return RustError{cudaSuccess};
+extern "C" void prefix_sum(fr_t* buf, uint32_t count) {
+  thrust::inclusive_scan(thrust::device, buf, buf + count, buf);
 }
 
 extern "C" RustError::by_value
```

### risc0/circuit/rv32im-m3-sys/cxx/rv32im/BUILD.bazel
```diff
@@ -6,5 +6,6 @@ cc_library(
     deps = [
         "//prove",
         "//verify",
+        "//hal/pick",
     ],
 )
```

### risc0/circuit/rv32im-m3-sys/cxx/rv32im/ffi.cpp
```diff
@@ -48,10 +48,13 @@ const char* risc0_circuit_rv32im_m3_prove(const uint8_t* elf_ptr, size_t elf_len
     verifyRv32im(readIop, po2);
     readIop.done();
   } catch (const std::exception& err) {
+    LOG(0, "ERROR: " << err.what());
     return strdup(err.what());
   } catch (...) {
+    LOG(0, "UNKNOWN ERROR");
     return strdup("Generic exception");
   }
+  LOG(0, "Completed successfuly");
   return nullptr;
 }
 
```

### risc0/circuit/rv32im-m3-sys/cxx/rv32im/test/BUILD.bazel
```diff
@@ -74,3 +74,10 @@ cc_test(
     ],
     deps = ["//rv32im/test:test_prove"],
 )
+
+cc_test(
+    name = "test_ffi",
+    srcs = ["test_ffi.cpp"],
+    data = ["//rv32im/rvtest:riscv_test_bins"],
+    deps = ["//rv32im"],
+)
```

### risc0/circuit/rv32im-m3-sys/cxx/rv32im/test/test_ffi.cpp
```diff
@@ -0,0 +1,34 @@
+// Copyright 2025 RISC Zero, Inc.
+//
+// Licensed under the Apache License, Version 2.0, <LICENSE-APACHE or
+// http://apache.org/licenses/LICENSE-2.0> or the MIT license <LICENSE-MIT or
+// http://opensource.org/licenses/MIT>, at your option. This file may not be
+// copied, modified, or distributed except according to those terms.
+//
+// Unless required by applicable law or agreed to in writing, software
+// distributed under the License is distributed on an "AS IS" BASIS,
+// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
+// See the License for the specific language governing permissions and
+// limitations under the License.
+//
+// SPDX-License-Identifier: Apache-2.0 OR MIT
+
+#include "core/log.h"
+#include "core/util.h"
+
+extern "C" const char* risc0_circuit_rv32im_m3_prove(const uint8_t* elf_ptr, size_t elf_len);
+
+void runTest(const std::string& name) {
+  auto fullname = "rv32im/rvtest/" + name;
+  auto elf = risc0::loadFile(fullname);
+  const char* err = risc0_circuit_rv32im_m3_prove(elf.data(), elf.size());
+  if (err != nullptr) {
+    throw std::runtime_error(err);
+  }
+}
+
+int main() {
+  LOG(0, "Hello world");
+  runTest("add");
+  runTest("addi");
+}
```
