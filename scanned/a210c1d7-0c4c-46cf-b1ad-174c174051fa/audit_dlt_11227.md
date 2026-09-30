# [?] fix(ssa): bail out of Brillig array offset when shifted index overflows addressing bits (#13122)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-06-30
Source: https://github.com/noir-lang/noir/commit/7e0734312173017c7a33053ffb77a08330ad770a
Type: security-commit

## Details
fix(ssa): bail out of Brillig array offset when shifted index overflows addressing bits (#13122)

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### acvm-repo/brillig/src/opcodes.rs
```diff
@@ -266,9 +266,9 @@ pub enum IntegerBitSize {
     U128,
 }
 
-impl From<IntegerBitSize> for u32 {
-    fn from(bit_size: IntegerBitSize) -> u32 {
-        match bit_size {
+impl IntegerBitSize {
+    pub const fn to_u32(self) -> u32 {
+        match self {
             IntegerBitSize::U1 => 1,
             IntegerBitSize::U8 => 8,
             IntegerBitSize::U16 => 16,
@@ -279,6 +279,12 @@ impl From<IntegerBitSize> for u32 {
     }
 }
 
+impl From<IntegerBitSize> for u32 {
+    fn from(bit_size: IntegerBitSize) -> u32 {
+        bit_size.to_u32()
+    }
+}
+
 impl TryFrom<u32> for IntegerBitSize {
     type Error = &'static str;
 
```

### acvm-repo/brillig_vm/src/lib.rs
```diff
@@ -33,7 +33,7 @@ use black_box::evaluate_black_box;
 pub use acir::brillig;
 use memory::MemoryTypeError;
 pub use memory::{
-    FREE_MEMORY_POINTER_ADDRESS, MEMORY_ADDRESSING_BIT_SIZE, Memory, MemoryValue,
+    FREE_MEMORY_POINTER_ADDRESS, MAX_MEMORY_SIZE, MEMORY_ADDRESSING_BIT_SIZE, Memory, MemoryValue,
     STACK_POINTER_ADDRESS, offsets,
 };
 
```

### acvm-repo/brillig_vm/src/memory.rs
```diff
@@ -23,6 +23,16 @@ use crate::assert_usize;
 /// All memory pointers are interpreted as `u32` values, meaning the VM can directly address up to 2^32 memory slots.
 pub const MEMORY_ADDRESSING_BIT_SIZE: IntegerBitSize = IntegerBitSize::U32;
 
+/// Maximum number of memory slots that can be allocated.
+///
+/// This limit is set to `i32::MAX` to ensure deterministic behavior across all architectures.
+/// On 32-bit systems, Rust's allocator limits allocations to `isize::MAX` bytes, which would
+/// restrict us to fewer elements anyway. By using `i32::MAX`, we ensure the same behavior
+/// on both 32-bit and 64-bit systems.
+///
+/// See: <https://github.com/rust-lang/rust/pull/95295> and <https://doc.rust-lang.org/1.81.0/src/core/alloc/layout.rs.html>
+pub const MAX_MEMORY_SIZE: usize = i32::MAX as usize;
+
 /// The current stack pointer is always in slot 0.
 ///
 /// It gets manipulated by opcodes laid down for calls by codegen.
@@ -486,26 +496,15 @@ impl<F: AcirField> Memory<F> {
         }
     }
 
-    /// Maximum number of memory slots that can be allocated.
-    ///
-    /// This limit is set to `i32::MAX` to ensure deterministic behavior across all architectures.
-    /// On 32-bit systems, Rust's allocator limits allocations to `isize::MAX` bytes, which would
-    /// restrict us to fewer elements anyway. By using `i32::MAX`, we ensure the same behavior
-    /// on both 32-bit and 64-bit systems.
-    ///
-    /// See: <https://github.com/rust-lang/rust/pull/95295> and <https://doc.rust-lang.org/1.81.0/src/core/alloc/layout.rs.html>
-    const MAX_MEMORY_SIZE: usize = i32::MAX as usize;
-
     /// Increase the size of memory fit `size` elements, or the current length, whichever is bigger.
     ///
     /// # Panics
     ///
-    /// Panics if `size` exceeds [`Self::MAX_MEMORY_SIZE`].
+    /// Panics if `size` exceeds [`MAX_MEMORY_SIZE`].
     fn resize_to_fit(&mut self, size: usize) {
         assert!(
-            size <= Self::MAX_MEMORY_SIZE,
-            "Memory address space exceeded: requested {size} slots, maximum is {} (i32::MAX)",
-            Self::MAX_MEMORY_SIZE
+            size <= MAX_MEMORY_SIZE,
+            "Memory address space exceeded: requested {size} slots, maximum is {MAX_MEMORY_SIZE} (i32::MAX)"
         );
         // Calculate new memory size
         let new_size = std::cmp::max(self.inner.len(), size);
@@ -683,7 +682,7 @@ mod tests {
     fn resize_to_fit_panics_when_exceeding_max_memory_size() {
         let mut memory = Memory::<FieldElement>::default();
         // Attempting to resize beyond i32::MAX should panic
-        memory.resize_to_fit(Memory::<FieldElement>::MAX_MEMORY_SIZE + 1);
+        memory.resize_to_fit(MAX_MEMORY_SIZE + 1);
     }
 
     #[test_case(IntegerBitSize::U1, 2)]
```

### compiler/noirc_evaluator/src/brillig/brillig_ir.rs
```diff
@@ -26,6 +26,7 @@ mod instructions;
 
 use std::{cell::RefCell, rc::Rc};
 
+use acvm::brillig_vm::MEMORY_ADDRESSING_BIT_SIZE;
 use artifact::Label;
 use brillig_variable::SingleAddrVariable;
 pub(crate) use instructions::BrilligBinaryOp;
@@ -52,7 +53,7 @@ use super::{BrilligOptions, FunctionId, GlobalSpace, ProcedureId};
 /// The Brillig VM does not apply a limit to the memory address space,
 /// As a convention, we take use 32 bits. This means that we assume that
 /// memory has 2^32 memory slots.
-pub(crate) const BRILLIG_MEMORY_ADDRESSING_BIT_SIZE: u32 = 32;
+pub(crate) const BRILLIG_MEMORY_ADDRESSING_BIT_SIZE: u32 = MEMORY_ADDRESSING_BIT_SIZE.to_u32();
 
 /// Registers reserved in runtime for special purposes.
 pub(crate) struct ReservedRegisters;
```

### compiler/noirc_evaluator/src/ssa/opt/brillig_array_get_and_set.rs
```diff
@@ -55,6 +55,8 @@
 //! deduplicated across instructions. Doing this during Brillig codegen would be too late, as at
 //! that time we have a read-only DFG and we would be forced to generate more Brillig opcodes.
 
+use acvm::{AcirField, brillig_vm::MAX_MEMORY_SIZE};
+
 use crate::{
     brillig::brillig_ir::BRILLIG_MEMORY_ADDRESSING_BIT_SIZE,
     ssa::{
@@ -123,10 +125,21 @@ fn compute_offset_index(
 ) -> Option<ValueId> {
     let constant_index = context.dfg.get_numeric_constant(index)?;
     let offset = context.dfg.array_offset(array_or_vector, index);
-    let index = context.dfg.make_constant(
-        constant_index + offset.to_u32().into(),
-        NumericType::unsigned(BRILLIG_MEMORY_ADDRESSING_BIT_SIZE),
-    );
+    let shifted_index = constant_index + offset.to_u32().into();
+
+    // A shifted index that doesn't fit the u32 addressing type, or that lands outside the
+    // addressable Brillig memory range, can never be a valid address. Leave the access
+    // unshifted and let the normal runtime out-of-bounds path handle it instead of
+    // producing a constant the backend would reject.
+    let fits_in_memory =
+        shifted_index.try_to_u32().is_some_and(|index| index as usize <= MAX_MEMORY_SIZE);
+    if !fits_in_memory {
+        return None;
+    }
+
+    let index = context
+        .dfg
+        .make_constant(shifted_index, NumericType::unsigned(BRILLIG_MEMORY_ADDRESSING_BIT_SIZE));
     Some(index)
 }
 
@@ -306,6 +319,61 @@ mod tests {
         );
     }
 
+    #[test]
+    fn do_not_offset_vector_when_shifted_index_overflows_addressing_bits() {
+        // The vector offset is 3, so shifting u32::MAX would produce 4294967298,
+        // which does not fit in the 32-bit Brillig addressing type. The pass must
+        // leave the stored index unshifted so it is handled by the normal runtime
+        // out-of-bounds path instead of producing a constant Brillig codegen rejects.
+        // The cosmetic " minus 3" is added by the printer once arrays are offset, but
+        // the printed value stays at 4294967295 rather than the overflowing 4294967298.
+        let src = "
+        brillig(inline) fn main f0 {
+          b0(v0: [Field]):
+            v2 = array_get v0, index u32 4294967295 -> Field
+            return v2
+        }
+        ";
+
+        let ssa = Ssa::from_str(src).unwrap();
+        let ssa = ssa.brillig_array_get_and_set();
+
+        assert_ssa_snapshot!(ssa, @r"
+        brillig(inline) fn main f0 {
+          b0(v0: [Field]):
+            v2 = array_get v0, index u32 4294967295 minus 3 -> Field
+            return v2
+        }
+        ");
+    }
+
+    #[test]
+    fn do_not_offset_vector_when_shifted_index_exceeds_max_memory_size() {
+        // 2147483647 (i32::MAX) fits the 32-bit addressing type, but shifting it by
+        // the vector offset lands above the maximum addressable memory slot
+        // (MAX_MEMORY_SIZE == i32::MAX), so it can never be a valid address. The pass
+        // must leave it unshifted for the runtime out-of-bounds path. The printed value
+        // stays at 2147483647 rather than the unaddressable 2147483650.
+        let src = "
+        brillig(inline) fn main f0 {
+          b0(v0: [Field]):
+            v2 = array_get v0, index u32 2147483647 -> Field
+            return v2
+        }
+        ";
+
+        let ssa = Ssa::from_str(src).unwrap();
+        let ssa = ssa.brillig_array_get_and_set();
+
+        assert_ssa_snapshot!(ssa, @r"
+        brillig(inline) fn main f0 {
+          b0(v0: [Field]):
+            v2 = array_get v0, index u32 2147483647 minus 3 -> Field
+            return v2
+        }
+        ");
+    }
+
     #[test]
     #[should_panic(expected = "offset at most once")]
     fn only_executes_once() {
```

### test_programs/execution_failure/brillig_vector_index_offset_overflow/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "brillig_vector_index_offset_overflow"
+type = "bin"
+authors = [""]
+
+[dependencies]
```

### test_programs/execution_failure/brillig_vector_index_offset_overflow/src/main.nr
```diff
@@ -0,0 +1,19 @@
+// Regression test for https://github.com/noir-lang/noir-claude/issues/1133
+// A constant vector index near `u32::MAX` is shifted by the Brillig vector
+// memory-layout offset (3) during the `brillig_array_get_and_set` pass. The
+// shifted value must not overflow the 32-bit Brillig addressing type: the
+// access should surface as a runtime out-of-bounds error rather than panicking
+// in Brillig codegen.
+//
+// `get` is a separate unconstrained function taking an opaque vector, so its
+// length is not known at the indexing site and the access is not folded into a
+// compile-time out-of-bounds error before reaching the offset pass.
+unconstrained fn get(v: [Field]) -> Field {
+    v[4294967295]
+}
+
+fn main() -> pub Field {
+    let v: [Field] = [1, 2, 3].as_vector();
+    // Safety: testing an out-of-bounds vector access
+    unsafe { get(v) }
+}
```

### tooling/nargo_cli/tests/snapshots/execution_failure/brillig_vector_index_offset_overflow/execute__tests__acir_stderr.snap
```diff
@@ -0,0 +1,27 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+bug: Brillig function call isn't properly covered by a manual constraint
+   ┌─ src/main.nr:18:14
+   │
+18 │     unsafe { get(v) }
+   │              ------ This Brillig call's inputs and its return values haven't been sufficiently constrained. This should be done to prevent potential soundness vulnerabilities
+   │
+   = Call stack:
+     1: main
+             at src/main.nr:18:14
+
+error: Assertion failed: Index out of bounds
+   ┌─ src/main.nr:12:5
+   │
+12 │     v[4294967295]
+   │     -------------
+   │
+   = Call stack:
+     1: main
+             at src/main.nr:18:14
+     2: get
+             at src/main.nr:12:5
+
+Failed assertion
```

### tooling/nargo_cli/tests/snapshots/execution_failure/brillig_vector_index_offset_overflow/execute__tests__brillig_stderr.snap
```diff
@@ -0,0 +1,17 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Assertion failed: Index out of bounds
+   ┌─ src/main.nr:12:5
+   │
+12 │     v[4294967295]
+   │     -------------
+   │
+   = Call stack:
+     1: main
+             at src/main.nr:18:14
+     2: get
+             at src/main.nr:12:5
+
+Failed assertion
```

### tooling/nargo_cli/tests/snapshots/execution_failure/brillig_vector_index_offset_overflow/execute__tests__comptime_stderr.snap
```diff
@@ -0,0 +1,12 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Index out of bounds: 4294967295 is out of bounds for the array of length 3
+   ┌─ src/main.nr:12:5
+   │
+12 │     v[4294967295]
+   │     -------------
+   │
+
+Error interpreting main function
```
