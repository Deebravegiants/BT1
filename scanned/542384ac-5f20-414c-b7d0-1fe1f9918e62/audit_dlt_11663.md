# [?] Merge rust-bitcoin/rust-bitcoin#3392: fix: script number overflow check for push_int

## Summary
Severity: Unknown
Chain: Bitcoin
Component: rust-bitcoin/rust-bitcoin
Published: 2024-09-25
Source: https://github.com/rust-bitcoin/rust-bitcoin/commit/3bbad771723ce80848fd0f79d5476822850b4ec8
Type: security-commit

## Details
Merge rust-bitcoin/rust-bitcoin#3392: fix: script number overflow check for push_int

33edaf935d71167bb1bb92bc671272217852005a fix: check overflow for push_int with push_int_unchecked (Chris Hyunhum Cho)
876146154b4e480d85196461ee36cf3e8734d2b4 refactor: use push_lock_time instead of push_int (Chris Hyunhum Cho)

Pull request description:

  Fix the issue https://github.com/rust-bitcoin/rust-bitcoin/issues/1530. In the discussion of https://github.com/rust-bitcoin/rust-bitcoin/issues/1530, the suggested solution is to implement `ScriptInt` type to embrace the various type of integer(`i32, u32, i64, u64, i128, u128, isize, usize...`) to support both script number and locktime number.

  However, as `push_locktime` and `push_sequence` implemented, there’s no need to support `u32` of lock time for `push_int` anymore. Therefore, I’ve just changed the type of parameter to `i32`, and only check if it’s `i32::MIN`(which overflows 4 bytes sign-magnitude integer).

  ~I also added push_uint method to use internally for `push_locktime` and `push_sequence`, which have a dependency on `push_int` method.~

  UPDATE: also add `push_int_unchecked` for those who want to push the integer out of range(and helper for `push_locktime` and `push_sequence`, which has the same functionality of former `push_int`.

ACKs for top commit:
  tcharding:
    ACK 33edaf935d71167bb1bb92bc671272217852005a

Tree-SHA512: 89b02bd3faf1e0a1ed530b7210250f0db33886d2acd553d07761f4aef0bb6388b22ddc06a88de05acfe465305db4cf34822fb6547576aae2aa224b4d0045fa07

## Patch
### bitcoin/examples/taproot-psbt.rs
```diff
@@ -370,7 +370,7 @@ impl BenefactorWallet {
         beneficiary_key: XOnlyPublicKey,
     ) -> ScriptBuf {
         script::Builder::new()
-            .push_int(locktime.to_consensus_u32() as i64)
+            .push_lock_time(locktime)
             .push_opcode(OP_CLTV)
             .push_opcode(OP_DROP)
             .push_x_only_key(beneficiary_key)
```

### bitcoin/src/address/mod.rs
```diff
@@ -430,7 +430,7 @@ impl Address {
     ///
     /// This is a segwit address type that looks familiar (as p2sh) to legacy clients.
     pub fn p2shwpkh(pk: CompressedPublicKey, network: impl Into<NetworkKind>) -> Address {
-        let builder = script::Builder::new().push_int(0).push_slice(pk.wpubkey_hash());
+        let builder = script::Builder::new().push_int_unchecked(0).push_slice(pk.wpubkey_hash());
         let script_hash = builder.as_script().script_hash().expect("script is less than 520 bytes");
         Address::p2sh_from_hash(script_hash, network)
     }
@@ -458,7 +458,7 @@ impl Address {
         network: impl Into<NetworkKind>,
     ) -> Result<Address, WitnessScriptSizeError> {
         let hash = witness_script.wscript_hash()?;
-        let builder = script::Builder::new().push_int(0).push_slice(&hash);
+        let builder = script::Builder::new().push_int_unchecked(0).push_slice(&hash);
         let script_hash = builder.as_script().script_hash().expect("script is less than 520 bytes");
         Ok(Address::p2sh_from_hash(script_hash, network))
     }
```

### bitcoin/src/blockdata/constants.rs
```diff
@@ -84,7 +84,7 @@ fn bitcoin_genesis_tx() -> Transaction {
 
     // Inputs
     let in_script = script::Builder::new()
-        .push_int(486604799)
+        .push_int_unchecked(486604799)
         .push_int_non_minimal(4)
         .push_slice(b"The Times 03/Jan/2009 Chancellor on brink of second bailout for banks")
         .into_script();
```

### bitcoin/src/blockdata/script/builder.rs
```diff
@@ -2,7 +2,7 @@
 
 use core::fmt;
 
-use super::{opcode_to_verify, write_scriptint, PushBytes, Script, ScriptBuf};
+use super::{opcode_to_verify, write_scriptint, Error, PushBytes, Script, ScriptBuf};
 use crate::locktime::absolute;
 use crate::opcodes::all::*;
 use crate::opcodes::{self, Opcode};
@@ -29,19 +29,37 @@ impl Builder {
     ///
     /// Integers are encoded as little-endian signed-magnitude numbers, but there are dedicated
     /// opcodes to push some small integers.
-    pub fn push_int(self, data: i64) -> Builder {
+    ///
+    /// # Errors
+    ///
+    /// Only errors if `data == i32::MIN` (CScriptNum cannot have value -2^31).
+    pub fn push_int(self, n: i32) -> Result<Builder, Error> {
+        if n == i32::MIN {
+            // ref: https://github.com/bitcoin/bitcoin/blob/cac846c2fbf6fc69bfc288fd387aa3f68d84d584/src/script/script.h#L230
+            Err(Error::NumericOverflow)
+        } else {
+            Ok(self.push_int_unchecked(n.into()))
+        }
+    }
+
+    /// Adds instructions to push an unchecked integer onto the stack.
+    ///
+    /// Integers are encoded as little-endian signed-magnitude numbers, but there are dedicated
+    /// opcodes to push some small integers.
+    /// It doesn't check whether the integer in the range of [-2^31 +1...2^31 -1].
+    pub fn push_int_unchecked(self, n: i64) -> Builder {
         // We can special-case -1, 1-16
-        if data == -1 || (1..=16).contains(&data) {
-            let opcode = Opcode::from((data - 1 + opcodes::OP_TRUE.to_u8() as i64) as u8);
+        if n == -1 || (1..=16).contains(&n) {
+            let opcode = Opcode::from((n - 1 + opcodes::OP_TRUE.to_u8() as i64) as u8);
             self.push_opcode(opcode)
         }
         // We can also special-case zero
-        else if data == 0 {
+        else if n == 0 {
             self.push_opcode(opcodes::OP_0)
         }
         // Otherwise encode it as data
         else {
-            self.push_int_non_minimal(data)
+            self.push_int_non_minimal(n)
         }
     }
 
@@ -91,12 +109,12 @@ impl Builder {
 
     /// Adds instructions to push an absolute lock time onto the stack.
     pub fn push_lock_time(self, lock_time: absolute::LockTime) -> Builder {
-        self.push_int(lock_time.to_consensus_u32().into())
+        self.push_int_unchecked(lock_time.to_consensus_u32().into())
     }
 
     /// Adds instructions to push a sequence number onto the stack.
     pub fn push_sequence(self, sequence: Sequence) -> Builder {
-        self.push_int(sequence.to_consensus_u32().into())
+        self.push_int_unchecked(sequence.to_consensus_u32().into())
     }
 
     /// Converts the `Builder` into `ScriptBuf`.
```

### bitcoin/src/blockdata/script/tests.rs
```diff
@@ -18,18 +18,18 @@ fn script() {
     assert_eq!(script.as_bytes(), &comp[..]);
 
     // small ints
-    script = script.push_int(1);  comp.push(81u8); assert_eq!(script.as_bytes(), &comp[..]);
-    script = script.push_int(0);  comp.push(0u8);  assert_eq!(script.as_bytes(), &comp[..]);
-    script = script.push_int(4);  comp.push(84u8); assert_eq!(script.as_bytes(), &comp[..]);
-    script = script.push_int(-1); comp.push(79u8); assert_eq!(script.as_bytes(), &comp[..]);
+    script = script.push_int_unchecked(1);  comp.push(81u8); assert_eq!(script.as_bytes(), &comp[..]);
+    script = script.push_int_unchecked(0);  comp.push(0u8);  assert_eq!(script.as_bytes(), &comp[..]);
+    script = script.push_int_unchecked(4);  comp.push(84u8); assert_eq!(script.as_bytes(), &comp[..]);
+    script = script.push_int_unchecked(-1); comp.push(79u8); assert_eq!(script.as_bytes(), &comp[..]);
     // forced scriptint
     script = script.push_int_non_minimal(4); comp.extend([1u8, 4].iter().cloned()); assert_eq!(script.as_bytes(), &comp[..]);
     // big ints
-    script = script.push_int(17); comp.extend([1u8, 17].iter().cloned()); assert_eq!(script.as_bytes(), &comp[..]);
-    script = script.push_int(10000); comp.extend([2u8, 16, 39].iter().cloned()); assert_eq!(script.as_bytes(), &comp[..]);
+    script = script.push_int_unchecked(17); comp.extend([1u8, 17].iter().cloned()); assert_eq!(script.as_bytes(), &comp[..]);
+    script = script.push_int_unchecked(10000); comp.extend([2u8, 16, 39].iter().cloned()); assert_eq!(script.as_bytes(), &comp[..]);
     // notice the sign bit set here, hence the extra zero/128 at the end
-    script = script.push_int(10000000); comp.extend([4u8, 128, 150, 152, 0].iter().cloned()); assert_eq!(script.as_bytes(), &comp[..]);
-    script = script.push_int(-10000000); comp.extend([4u8, 128, 150, 152, 128].iter().cloned()); assert_eq!(script.as_bytes(), &comp[..]);
+    script = script.push_int_unchecked(10000000); comp.extend([4u8, 128, 150, 152, 0].iter().cloned()); assert_eq!(script.as_bytes(), &comp[..]);
+    script = script.push_int_unchecked(-10000000); comp.extend([4u8, 128, 150, 152, 128].iter().cloned()); assert_eq!(script.as_bytes(), &comp[..]);
 
     // data
     script = script.push_slice(b"NRA4VR"); comp.extend([6u8, 78, 82, 65, 52, 86, 82].iter().cloned()); assert_eq!(script.as_bytes(), &comp[..]);
@@ -652,8 +652,8 @@ fn test_iterator() {
 #[test]
 fn script_ord() {
     let script_1 = Builder::new().push_slice([1, 2, 3, 4]).into_script();
-    let script_2 = Builder::new().push_int(10).into_script();
-    let script_3 = Builder::new().push_int(15).into_script();
+    let script_2 = Builder::new().push_int_unchecked(10).into_script();
+    let script_3 = Builder::new().push_int_unchecked(15).into_script();
     let script_4 = Builder::new().push_opcode(OP_RETURN).into_script();
 
     assert!(script_1 < script_2);
@@ -684,7 +684,7 @@ fn test_bitcoinconsensus() {
 fn defult_dust_value_tests() {
     // Check that our dust_value() calculator correctly calculates the dust limit on common
     // well-known scriptPubKey types.
-    let script_p2wpkh = Builder::new().push_int(0).push_slice([42; 20]).into_script();
+    let script_p2wpkh = Builder::new().push_int_unchecked(0).push_slice([42; 20]).into_script();
     assert!(script_p2wpkh.is_p2wpkh());
     assert_eq!(script_p2wpkh.minimal_non_dust(), crate::Amount::from_sat(294));
     assert_eq!(
```

### fuzz/fuzz_targets/bitcoin/deserialize_script.rs
```diff
@@ -24,7 +24,7 @@ fn do_test(data: &[u8]) {
                     // others it'll just reserialize them as pushes.)
                     if bytes.len() == 1 && bytes[0] != 0x80 && bytes[0] != 0x00 {
                         if let Ok(num) = bytes.read_scriptint() {
-                            b = b.push_int(num);
+                            b = b.push_int_unchecked(num);
                         } else {
                             b = b.push_slice(bytes);
                         }
```
