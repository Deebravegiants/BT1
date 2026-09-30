# [?] [AUD-7] Fix heap-pointer overflow in sys_alloc_aligned (#2778)

## Summary
Severity: Unknown
Chain: ZK
Component: risc0/risc0
Published: 2025-01-30
Source: https://github.com/risc0/risc0/commit/5a7fa0389b974479b9bfc2355265d61527ed9f25
Type: security-commit

## Details
[AUD-7] Fix heap-pointer overflow in sys_alloc_aligned (#2778)

## Patch
### risc0/build/src/docker.rs
```diff
@@ -263,7 +263,7 @@ mod test {
         compare_image_id(
             &guest_list,
             "hello_commit",
-            "bb799ba590eb97503daee9e0389258b8d3c87e3ffb742f4c3748cfe1e4b18ee8",
+            "6f52b77974aeef81fa57bd91926cdaebc11a0288506a68dcb73444b563e702b4",
         );
     }
 }
```

### risc0/zkvm/methods/guest/src/bin/heap_limits.rs
```diff
@@ -0,0 +1,67 @@
+// Copyright 2025 RISC Zero, Inc.
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
+#![no_std]
+#![no_main]
+
+extern crate alloc;
+
+use alloc::{
+    alloc::{alloc, Layout},
+    string::String,
+};
+
+use risc0_zkvm::guest::env;
+
+risc0_zkvm::entry!(main);
+
+/// Show that we crash if we try to allocate too much memory instead of something else like re-use
+/// old addresses or some other potentially bad behavior.
+fn heap_overflow_via_alloc() {
+    let ptr = unsafe {
+        alloc(Layout::from_size_align(isize::MAX as usize, 1).unwrap())
+    };
+
+    // Use the pointer in some way to defeat optimizer
+    core::hint::black_box(ptr);
+
+    unreachable!("expected a crash in the memory allocator")
+}
+
+extern "C" {
+    fn sys_alloc_aligned(bytes: usize, align: usize) -> *mut u8;
+}
+
+/// Show that we crash if we try to allocate too much memory instead of something else like re-use
+/// old addresses or some other potentially bad behavior.
+fn heap_overflow_via_sys_alloc_aligned() {
+    for size in [10usize, usize::MAX] {
+        let ptr = unsafe {
+            sys_alloc_aligned(size, 1)
+        };
+
+        // Use the pointer in some way to defeat optimizer
+        core::hint::black_box(ptr);
+    }
+
+    unreachable!("expected a crash in the memory allocator")
+}
+
+fn main() {
+    match &env::read::<String>()[..] {
+        "heap_overflow_via_alloc" => heap_overflow_via_alloc(),
+        "heap_overflow_via_sys_alloc_aligned" => heap_overflow_via_sys_alloc_aligned(),
+        unknown => panic!("unknown test {unknown}"),
+    }
+}
```

### risc0/zkvm/platform/src/heap/bump.rs
```diff
@@ -80,21 +80,22 @@ pub(crate) unsafe fn alloc_aligned(bytes: usize, align: usize) -> *mut u8 {
         heap_pos += align - offset;
     }
 
-    let ptr = heap_pos as *mut u8;
-    heap_pos += bytes;
-
     // Check to make sure heap doesn't collide with SYSTEM memory.
-    if GUEST_MAX_MEM < heap_pos {
-        const MSG: &[u8] = "Out of memory! You have been using the default bump allocator which \
-            does not reclaim memory. Enable the `heap-embedded-alloc` feature to \
-            reclaim memory. This will result in extra cycle cost."
-            .as_bytes();
-        unsafe { sys_panic(MSG.as_ptr(), MSG.len()) };
+    match heap_pos.checked_add(bytes) {
+        Some(new_heap_pos) if new_heap_pos <= GUEST_MAX_MEM => {
+            // SAFETY: Single threaded, and non-premptive so modification is safe.
+            unsafe { HEAP_POS = new_heap_pos };
+        }
+        _ => {
+            const MSG: &[u8] = "Out of memory! You have been using the default bump allocator \
+                which does not reclaim memory. Enable the `heap-embedded-alloc` feature to \
+                reclaim memory. This will result in extra cycle cost."
+                .as_bytes();
+            unsafe { sys_panic(MSG.as_ptr(), MSG.len()) };
+        }
     }
 
-    // SAFETY: Single threaded, and non-premptive so modification is safe.
-    unsafe { HEAP_POS = heap_pos };
-    ptr
+    heap_pos as *mut u8
 }
 
 /// Initialize the bump allocator with the memory allocations defined in the [memory][crate::memory] module.
```

### risc0/zkvm/tests/heap.rs
```diff
@@ -0,0 +1,48 @@
+// Copyright 2025 RISC Zero, Inc.
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
+#![cfg(feature = "prove")]
+
+use risc0_zkvm::{get_prover_server, ExecutorEnv, ProverOpts};
+use risc0_zkvm_methods::HEAP_LIMITS_ELF;
+
+fn test_it(name: &str) -> anyhow::Error {
+    let env = ExecutorEnv::builder()
+        .write(&name)
+        .unwrap()
+        .build()
+        .unwrap();
+
+    let prover = get_prover_server(&ProverOpts::fast()).unwrap();
+
+    prover.prove(env, HEAP_LIMITS_ELF).map(|_| ()).unwrap_err()
+}
+
+#[test]
+fn heap_overflow_via_alloc() {
+    let error = test_it("heap_overflow_via_alloc");
+    assert!(
+        error.to_string().contains("Guest panicked: Out of memory!"),
+        "{error}"
+    );
+}
+
+#[test]
+fn heap_overflow_via_sys_alloc_aligned() {
+    let error = test_it("heap_overflow_via_sys_alloc_aligned");
+    assert!(
+        error.to_string().contains("Guest panicked: Out of memory!"),
+        "{error}"
+    );
+}
```
