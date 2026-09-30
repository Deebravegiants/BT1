# [?] fix(brillig): Protect against memory address overflows (#11864)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-03-13
Source: https://github.com/noir-lang/noir/commit/3a5091b66870360469277eaf440a34e56dd8453a
Type: security-commit

## Details
fix(brillig): Protect against memory address overflows (#11864)

## Patch
### acvm-repo/brillig/src/opcodes.rs
```diff
@@ -80,7 +80,7 @@ impl MemoryAddress {
     pub fn offset(&self, amount: u32) -> Self {
         // We disallow offsetting relatively addresses as this is not expected to be meaningful.
         let address = self.unwrap_direct();
-        MemoryAddress::direct(address + amount)
+        MemoryAddress::direct(address.checked_add(amount).expect("memory offset overflow"))
     }
 }
 
@@ -653,6 +653,8 @@ impl std::fmt::Display for BinaryIntOp {
 
 #[cfg(test)]
 mod tests {
+    use crate::MemoryAddress;
+
     use super::{BitSize, IntegerBitSize};
     use acir_field::FieldElement;
 
@@ -774,6 +776,13 @@ mod tests {
         assert!(BitSize::try_from_u32::<FieldElement>(0).is_err());
         assert!(BitSize::try_from_u32::<FieldElement>(256).is_err());
     }
+
+    #[test]
+    #[should_panic = "memory offset overflow"]
+    fn memory_offset_overflow() {
+        let addr = MemoryAddress::direct(u32::MAX);
+        let _ = addr.offset(1);
+    }
 }
 
 #[cfg(feature = "arb")]
```

### acvm-repo/brillig_vm/src/memory.rs
```diff
@@ -405,7 +405,9 @@ impl<F: AcirField> Memory<F> {
     fn resolve(&self, address: MemoryAddress) -> u32 {
         match address {
             MemoryAddress::Direct(address) => address,
-            MemoryAddress::Relative(offset) => self.get_stack_pointer() + offset,
+            MemoryAddress::Relative(offset) => {
+                self.get_stack_pointer().checked_add(offset).expect("stack pointer offset overflow")
+            }
         }
     }
 
@@ -648,4 +650,13 @@ mod tests {
     fn memory_value_new_integer_out_of_range(bit_size: IntegerBitSize, value: u128) {
         let _ = MemoryValue::<FieldElement>::new_integer(value, bit_size);
     }
+
+    #[test]
+    #[should_panic = "stack pointer offset overflow"]
+    fn memory_resolve_overflow() {
+        let mut memory = Memory::<FieldElement>::default();
+        memory.write(STACK_POINTER_ADDRESS, MemoryValue::from(u32::MAX - 10));
+        let addr = MemoryAddress::relative(20);
+        let _wrap = memory.resolve(addr);
+    }
 }
```
