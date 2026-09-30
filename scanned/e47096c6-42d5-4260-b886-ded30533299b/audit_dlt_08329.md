# [?] [compiler] Fix constant folding for unsigned shift overflow wrap. (#19893)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-05-27
Source: https://github.com/aptos-labs/aptos-core/commit/6b4d87cb1d5862ed28d8f307696241294e9e1f07
Type: security-commit

## Details
[compiler] Fix constant folding for unsigned shift overflow wrap. (#19893)

## Patch
### third_party/move/move-compiler-v2/transactional-tests/tests/operators/round-trip/shift_operators.decompiled
```diff
@@ -51,29 +51,14 @@ script {
 //# run
 script {
     fun main() {
-        assert!(7u8 << 7u8 == 128u8, 5000);
-        assert!(7 << 62u8 == 13835058055282163712, 5001);
-        assert!(2u128 << 127u8 == 0u128, 5002);
-        assert!(7u16 << 15u8 == 32768u16, 5003);
-        assert!(17u32 << 30u8 == 1073741824u32, 5004);
-        assert!(7u256 << 254u8 == 86844066927987146567678238756515930889952488499230423029593188005934847229952u256, 5005);
+        ()
     }
 }
 
 
 //# run
 script {
     fun main() {
-        assert!(54u8 << 3u8 == 176u8, 6000);
-        assert!(124u8 << 5u8 == 128u8, 6002);
-        assert!(345325745376476456 << 47u8 == 2203386117691015168, 6102);
-        assert!(8629035907847368941279654523567912314u128 << 77u8 == 317056859699765342273530379836650946560u128, 6201);
-        assert!(295429678238907658936718926478967892769u128 << 83u8 == 78660438169199498567214234129963941888u128, 6203);
-        assert!(1234u16 << 12u8 == 8192u16, 6301);
-        assert!(6553u16 << 15u8 == 32768u16, 6302);
-        assert!(1234567u32 << 12u8 == 761819136u32, 6400);
-        assert!(1234567u32 << 17u8 == 2903375872u32, 6401);
-        assert!(12345671u32 << 27u8 == 939524096u32, 6402);
-        assert!(1234536789093546757803786604381691994985672142341299639418u256 << 202u8 == 33658913632735705985908889087832028406806276615240336691180752852867975479296u256, 6504);
+        ()
     }
 }
```

### third_party/move/move-compiler-v2/transactional-tests/tests/operators/round-trip/shift_operators.decompiled.baseline.exp
```diff
@@ -19,5 +19,5 @@ task 2 lines 19-24:  run [script {]
 task 3 lines 27-32:  run [script {]
 task 4 lines 35-40:  run [script {]
 task 5 lines 43-48:  run [script {]
-task 6 lines 51-61:  run [script {]
-task 7 lines 64-79:  run [script {]
+task 6 lines 51-56:  run [script {]
+task 7 lines 59-64:  run [script {]
```

### third_party/move/move-compiler-v2/transactional-tests/tests/simplifier/round-trip/shift_overflow_wrap.decompiled
```diff
@@ -0,0 +1,137 @@
+//**** Cross-compiled for `move` syntax from `tests/simplifier/shift_overflow_wrap.move`
+
+//# publish
+module 0xff::shift_max {
+    public fun u128_max(): u128 {
+        MAX_U128
+    }
+    public fun u128_max_shl1(): u128 {
+        u128_max() << 1u8
+    }
+    public fun u16_max(): u16 {
+        MAX_U16
+    }
+    public fun u16_max_shl1(): u16 {
+        u16_max() << 1u8
+    }
+    public fun u256_max(): u256 {
+        MAX_U256
+    }
+    public fun u256_max_shl1(): u256 {
+        u256_max() << 1u8
+    }
+    public fun u32_max(): u32 {
+        MAX_U32
+    }
+    public fun u32_max_shl1(): u32 {
+        u32_max() << 1u8
+    }
+    public fun u64_max(): u64 {
+        MAX_U64
+    }
+    public fun u64_max_shl1(): u64 {
+        u64_max() << 1u8
+    }
+    public fun u8_max(): u8 {
+        MAX_U8
+    }
+    public fun u8_max_shl1(): u8 {
+        u8_max() << 1u8
+    }
+}
+
+
+//# run --verbose
+script {
+    fun main() {
+        ()
+    }
+}
+
+
+//# run --verbose
+script {
+    fun main() {
+        ()
+    }
+}
+
+
+//# run --verbose
+script {
+    fun main() {
+        ()
+    }
+}
+
+
+//# run --verbose
+script {
+    fun main() {
+        ()
+    }
+}
+
+
+//# run --verbose
+script {
+    fun main() {
+        ()
+    }
+}
+
+
+//# run --verbose
+script {
+    fun main() {
+        ()
+    }
+}
+
+
+//# run 0xff::shift_max::u8_max_shl1 --verbose
+
+//# run 0xff::shift_max::u16_max_shl1 --verbose
+
+//# run 0xff::shift_max::u32_max_shl1 --verbose
+
+//# run 0xff::shift_max::u64_max_shl1 --verbose
+
+//# run 0xff::shift_max::u128_max_shl1 --verbose
+
+//# run 0xff::shift_max::u256_max_shl1 --verbose
+
+//# publish
+module 0xff::const_shift_max {
+    public fun c_u128(): u128 {
+        340282366920938463463374607431768211454u128
+    }
+    public fun c_u16(): u16 {
+        65534u16
+    }
+    public fun c_u256(): u256 {
+        115792089237316195423570985008687907853269984665640564039457584007913129639934u256
+    }
+    public fun c_u32(): u32 {
+        4294967294u32
+    }
+    public fun c_u64(): u64 {
+        18446744073709551614
+    }
+    public fun c_u8(): u8 {
+        254u8
+    }
+}
+
+
+//# run 0xff::const_shift_max::c_u8 --verbose
+
+//# run 0xff::const_shift_max::c_u16 --verbose
+
+//# run 0xff::const_shift_max::c_u32 --verbose
+
+//# run 0xff::const_shift_max::c_u64 --verbose
+
+//# run 0xff::const_shift_max::c_u128 --verbose
+
+//# run 0xff::const_shift_max::c_u256 --verbose
\ No newline at end of file
```

### third_party/move/move-compiler-v2/transactional-tests/tests/simplifier/round-trip/shift_overflow_wrap.decompiled.baseline.exp
```diff
@@ -0,0 +1,33 @@
+processed 20 tasks
+task 0 lines 3-41:  publish [module 0xff::shift_max {]
+task 1 lines 44-49:  run --verbose [script {]
+task 2 lines 52-57:  run --verbose [script {]
+task 3 lines 60-65:  run --verbose [script {]
+task 4 lines 68-73:  run --verbose [script {]
+task 5 lines 76-81:  run --verbose [script {]
+task 6 lines 84-89:  run --verbose [script {]
+task 7 lines 92-92:  run 0xff::shift_max::u8_max_shl1 --verbose
+return values: 254
+task 8 lines 94-94:  run 0xff::shift_max::u16_max_shl1 --verbose
+return values: 65534
+task 9 lines 96-96:  run 0xff::shift_max::u32_max_shl1 --verbose
+return values: 4294967294
+task 10 lines 98-98:  run 0xff::shift_max::u64_max_shl1 --verbose
+return values: 18446744073709551614
+task 11 lines 100-100:  run 0xff::shift_max::u128_max_shl1 --verbose
+return values: 340282366920938463463374607431768211454
+task 12 lines 102-102:  run 0xff::shift_max::u256_max_shl1 --verbose
+return values: 115792089237316195423570985008687907853269984665640564039457584007913129639934
+task 13 lines 104-124:  publish [module 0xff::const_shift_max {]
+task 14 lines 127-127:  run 0xff::const_shift_max::c_u8 --verbose
+return values: 254
+task 15 lines 129-129:  run 0xff::const_shift_max::c_u16 --verbose
+return values: 65534
+task 16 lines 131-131:  run 0xff::const_shift_max::c_u32 --verbose
+return values: 4294967294
+task 17 lines 133-133:  run 0xff::const_shift_max::c_u64 --verbose
+return values: 18446744073709551614
+task 18 lines 135-135:  run 0xff::const_shift_max::c_u128 --verbose
+return values: 340282366920938463463374607431768211454
+task 19 lines 137-137:  run 0xff::const_shift_max::c_u256 --verbose
+return values: 115792089237316195423570985008687907853269984665640564039457584007913129639934
```

### third_party/move/move-compiler-v2/transactional-tests/tests/simplifier/shift_overflow_wrap.exp
```diff
@@ -0,0 +1,33 @@
+processed 20 tasks
+task 0 lines 1-18:  publish [module 0xff::shift_max {]
+task 1 lines 20-25:  run --verbose [script {]
+task 2 lines 27-32:  run --verbose [script {]
+task 3 lines 34-39:  run --verbose [script {]
+task 4 lines 41-46:  run --verbose [script {]
+task 5 lines 48-57:  run --verbose [script {]
+task 6 lines 59-68:  run --verbose [script {]
+task 7 lines 70-70:  run 0xff::shift_max::u8_max_shl1 --verbose
+return values: 254
+task 8 lines 72-72:  run 0xff::shift_max::u16_max_shl1 --verbose
+return values: 65534
+task 9 lines 74-74:  run 0xff::shift_max::u32_max_shl1 --verbose
+return values: 4294967294
+task 10 lines 76-76:  run 0xff::shift_max::u64_max_shl1 --verbose
+return values: 18446744073709551614
+task 11 lines 78-78:  run 0xff::shift_max::u128_max_shl1 --verbose
+return values: 340282366920938463463374607431768211454
+task 12 lines 80-80:  run 0xff::shift_max::u256_max_shl1 --verbose
+return values: 115792089237316195423570985008687907853269984665640564039457584007913129639934
+task 13 lines 82-99:  publish [module 0xff::const_shift_max {]
+task 14 lines 101-101:  run 0xff::const_shift_max::c_u8 --verbose
+return values: 254
+task 15 lines 103-103:  run 0xff::const_shift_max::c_u16 --verbose
+return values: 65534
+task 16 lines 105-105:  run 0xff::const_shift_max::c_u32 --verbose
+return values: 4294967294
+task 17 lines 107-107:  run 0xff::const_shift_max::c_u64 --verbose
+return values: 18446744073709551614
+task 18 lines 109-109:  run 0xff::const_shift_max::c_u128 --verbose
+return values: 340282366920938463463374607431768211454
+task 19 lines 111-111:  run 0xff::const_shift_max::c_u256 --verbose
+return values: 115792089237316195423570985008687907853269984665640564039457584007913129639934
```

### third_party/move/move-compiler-v2/transactional-tests/tests/simplifier/shift_overflow_wrap.move
```diff
@@ -0,0 +1,111 @@
+//# publish
+module 0xff::shift_max {
+    public fun u8_max():   u8   { 255u8 }
+    public fun u16_max():  u16  { 65535u16 }
+    public fun u32_max():  u32  { 4294967295u32 }
+    public fun u64_max():  u64  { 18446744073709551615u64 }
+    public fun u128_max(): u128 { 340282366920938463463374607431768211455u128 }
+    public fun u256_max(): u256 {
+        115792089237316195423570985008687907853269984665640564039457584007913129639935u256
+    }
+
+    public fun u8_max_shl1():   u8   { u8_max()   << 1u8 }
+    public fun u16_max_shl1():  u16  { u16_max()  << 1u8 }
+    public fun u32_max_shl1():  u32  { u32_max()  << 1u8 }
+    public fun u64_max_shl1():  u64  { u64_max()  << 1u8 }
+    public fun u128_max_shl1(): u128 { u128_max() << 1u8 }
+    public fun u256_max_shl1(): u256 { u256_max() << 1u8 }
+}
+
+//# run --verbose
+script {
+    fun main() {
+        assert!(255u8 << 1u8 == 254u8, 100);
+    }
+}
+
+//# run --verbose
+script {
+    fun main() {
+        assert!(65535u16 << 1u8 == 65534u16, 200);
+    }
+}
+
+//# run --verbose
+script {
+    fun main() {
+        assert!(4294967295u32 << 1u8 == 4294967294u32, 300);
+    }
+}
+
+//# run --verbose
+script {
+    fun main() {
+        assert!(18446744073709551615u64 << 1u8 == 18446744073709551614u64, 400);
+    }
+}
+
+//# run --verbose
+script {
+    fun main() {
+        assert!(
+            340282366920938463463374607431768211455u128 << 1u8
+                == 340282366920938463463374607431768211454u128,
+            500,
+        );
+    }
+}
+
+//# run --verbose
+script {
+    fun main() {
+        assert!(
+            115792089237316195423570985008687907853269984665640564039457584007913129639935u256 << 1u8
+                == 115792089237316195423570985008687907853269984665640564039457584007913129639934u256,
+            600,
+        );
+    }
+}
+
+//# run 0xff::shift_max::u8_max_shl1 --verbose
+
+//# run 0xff::shift_max::u16_max_shl1 --verbose
+
+//# run 0xff::shift_max::u32_max_shl1 --verbose
+
+//# run 0xff::shift_max::u64_max_shl1 --verbose
+
+//# run 0xff::shift_max::u128_max_shl1 --verbose
+
+//# run 0xff::shift_max::u256_max_shl1 --verbose
+
+//# publish
+module 0xff::const_shift_max {
+    const C_U8:   u8   = 255u8 << 1u8;
+    const C_U16:  u16  = 65535u16 << 1u8;
+    const C_U32:  u32  = 4294967295u32 << 1u8;
+    const C_U64:  u64  = 18446744073709551615u64 << 1u8;
+    const C_U128: u128 =
+        340282366920938463463374607431768211455u128 << 1u8;
+    const C_U256: u256 =
+        115792089237316195423570985008687907853269984665640564039457584007913129639935u256 << 1u8;
+
+    public fun c_u8():   u8   { C_U8 }
+    public fun c_u16():  u16  { C_U16 }
+    public fun c_u32():  u32  { C_U32 }
+    public fun c_u64():  u64  { C_U64 }
+    public fun c_u128(): u128 { C_U128 }
+    public fun c_u256(): u256 { C_U256 }
+}
+
+//# run 0xff::const_shift_max::c_u8 --verbose
+
+//# run 0xff::const_shift_max::c_u16 --verbose
+
+//# run 0xff::const_shift_max::c_u32 --verbose
+
+//# run 0xff::const_shift_max::c_u64 --verbose
+
+//# run 0xff::const_shift_max::c_u128 --verbose
+
+//# run 0xff::const_shift_max::c_u256 --verbose
```

### third_party/move/move-model/src/constant_folder.rs
```diff
@@ -242,10 +242,6 @@ impl<'env> ConstantFolder<'env> {
         }
     }
 
-    fn checked_shl(a: &BigInt, b: &BigInt) -> Option<BigInt> {
-        b.to_u16().map(|b| a.shl(b))
-    }
-
     fn checked_shr(a: &BigInt, b: &BigInt) -> Option<BigInt> {
         b.to_u16().map(|b| a.shr(b))
     }
@@ -319,18 +315,23 @@ impl<'env> ConstantFolder<'env> {
                         }
                     },
                     O::Shl => {
-                        // result_pty should be same size as arg0
-                        let arg0_size = Self::ptype_num_bits_bigint(result_pty);
-                        self.shift_rhs_check(val1, &arg0_size, id, name())
-                            .and_then(|_| {
-                                self.binop_num(
-                                    name(),
-                                    Self::checked_shl,
-                                    id,
-                                    result_pty,
-                                    val0,
-                                    val1,
-                                )
+                        let Some(bits) = result_pty.get_num_bits() else {
+                            // Refuse to fold for spec-language `Num` (unbounded);
+                            // the prover's translation differs from runtime wrap.
+                            return None;
+                        };
+                        // Typing only admits unsigned `Shl` operands; the
+                        // modular wrap below assumes that.
+                        debug_assert!(!result_pty.is_signed());
+                        // Wrap modulo 2^N to match the runtime's wrapping `<<`.
+                        let num_bits = BigInt::from(bits);
+                        self.shift_rhs_check(val1, &num_bits, id, name())
+                            .and_then(|_| val1.to_u32())
+                            .map(|rhs| {
+                                let raw = val0.shl(rhs);
+                                let modulus = BigInt::from(1).shl(bits as u32);
+                                let wrapped = raw.rem(&modulus);
+                                ExpData::Value(id, Value::Number(wrapped)).into_exp()
                             })
                     },
                     O::Shr => {
```
