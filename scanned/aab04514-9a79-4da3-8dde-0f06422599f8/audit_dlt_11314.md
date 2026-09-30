# [?] fix: disable underflow fix for fields (#8631)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-05-22
Source: https://github.com/noir-lang/noir/commit/2c2cf601adc744ef705e7ad5f5dd1f6f25e73534
Type: security-commit

## Details
fix: disable underflow fix for fields (#8631)

## Patch
### compiler/noirc_evaluator/src/acir/mod.rs
```diff
@@ -1165,10 +1165,17 @@ impl<'a> Context<'a> {
                 ) {
                     // Subtractions must first have the integer modulus added before truncation can be
                     // applied. This is done in order to prevent underflow.
-                    let integer_modulus = power_of_two::<FieldElement>(bit_size);
-                    let integer_modulus = self.acir_context.add_constant(integer_modulus);
-                    var = self.acir_context.add_var(var, integer_modulus)?;
-                    max_bit_size += 1;
+                    //
+                    // FieldElements have max bit size equals to max_num_bits so
+                    // we filter out this bit size because there is no underflow
+                    // for FieldElements. Furthermore, adding a power of two
+                    // would be incorrect for a FieldElement (cf. #8519).
+                    if max_bit_size < FieldElement::max_num_bits() {
+                        let integer_modulus = power_of_two::<FieldElement>(max_bit_size);
+                        let integer_modulus = self.acir_context.add_constant(integer_modulus);
+                        var = self.acir_context.add_var(var, integer_modulus)?;
+                        max_bit_size += 1;
+                    }
                 }
             }
             Value::Param { .. } => {
```

### test_programs/execution_success/regression_8519/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "regression_8519"
+type = "bin"
+authors = [""]
+
+[dependencies]
\ No newline at end of file
```

### test_programs/execution_success/regression_8519/Prover.toml
```diff
@@ -0,0 +1 @@
+a = "0x000000000000000000000000000000000000000000000000131640459367fd34"
\ No newline at end of file
```

### test_programs/execution_success/regression_8519/src/main.nr
```diff
@@ -0,0 +1,6 @@
+fn main(a: Field) -> pub u128 {
+    let c = -a;
+    let c = c as u128;
+    assert_eq(c, 53438638232309528388129535304893203149);
+    c
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/4_sub/execute__tests__force_brillig_false_inliner_-9223372036854775808.snap
```diff
@@ -47,12 +47,12 @@ expression: artifact
     "BLACKBOX::RANGE [(_0, 32)] []",
     "BLACKBOX::RANGE [(_1, 32)] []",
     "BLACKBOX::RANGE [(_2, 32)] []",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(0)), (-1, Witness(1))], q_c: 340282366920938463463374607436063178752 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(3)), Simple(Witness(4))]",
-    "BLACKBOX::RANGE [(_3, 223)] []",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(0)), (-1, Witness(1))], q_c: 340282366920938463463374607431768211456 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(3)), Simple(Witness(4))]",
+    "BLACKBOX::RANGE [(_3, 222)] []",
     "BLACKBOX::RANGE [(_4, 32)] []",
-    "EXPR [ (1, _0) (-1, _1) (-4294967296, _3) (-1, _4) 340282366920938463463374607436063178752 ]",
+    "EXPR [ (1, _0) (-1, _1) (-4294967296, _3) (-1, _4) 340282366920938463463374607431768211456 ]",
     "EXPR [ (-1, _3) (-1, _5) 5096253676302562286669017222071363378443840053029366383258766538131 ]",
-    "BLACKBOX::RANGE [(_5, 223)] []",
+    "BLACKBOX::RANGE [(_5, 222)] []",
     "BRILLIG CALL func 1: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(3))], q_c: 5096253676302562286669017222071363378443840053029366383258766538131 })], outputs: [Simple(Witness(6))]",
     "EXPR [ (-1, _3, _6) (5096253676302562286669017222071363378443840053029366383258766538131, _6) (1, _7) -1 ]",
     "EXPR [ (-1, _3, _7) (5096253676302562286669017222071363378443840053029366383258766538131, _7) 0 ]",
```

### tooling/nargo_cli/tests/snapshots/execution_success/4_sub/execute__tests__force_brillig_false_inliner_0.snap
```diff
@@ -47,12 +47,12 @@ expression: artifact
     "BLACKBOX::RANGE [(_0, 32)] []",
     "BLACKBOX::RANGE [(_1, 32)] []",
     "BLACKBOX::RANGE [(_2, 32)] []",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(0)), (-1, Witness(1))], q_c: 340282366920938463463374607436063178752 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(3)), Simple(Witness(4))]",
-    "BLACKBOX::RANGE [(_3, 223)] []",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(0)), (-1, Witness(1))], q_c: 340282366920938463463374607431768211456 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(3)), Simple(Witness(4))]",
+    "BLACKBOX::RANGE [(_3, 222)] []",
     "BLACKBOX::RANGE [(_4, 32)] []",
-    "EXPR [ (1, _0) (-1, _1) (-4294967296, _3) (-1, _4) 340282366920938463463374607436063178752 ]",
+    "EXPR [ (1, _0) (-1, _1) (-4294967296, _3) (-1, _4) 340282366920938463463374607431768211456 ]",
     "EXPR [ (-1, _3) (-1, _5) 5096253676302562286669017222071363378443840053029366383258766538131 ]",
-    "BLACKBOX::RANGE [(_5, 223)] []",
+    "BLACKBOX::RANGE [(_5, 222)] []",
     "BRILLIG CALL func 1: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(3))], q_c: 5096253676302562286669017222071363378443840053029366383258766538131 })], outputs: [Simple(Witness(6))]",
     "EXPR [ (-1, _3, _6) (5096253676302562286669017222071363378443840053029366383258766538131, _6) (1, _7) -1 ]",
     "EXPR [ (-1, _3, _7) (5096253676302562286669017222071363378443840053029366383258766538131, _7) 0 ]",
```

### tooling/nargo_cli/tests/snapshots/execution_success/4_sub/execute__tests__force_brillig_false_inliner_9223372036854775807.snap
```diff
@@ -47,12 +47,12 @@ expression: artifact
     "BLACKBOX::RANGE [(_0, 32)] []",
     "BLACKBOX::RANGE [(_1, 32)] []",
     "BLACKBOX::RANGE [(_2, 32)] []",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(0)), (-1, Witness(1))], q_c: 340282366920938463463374607436063178752 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(3)), Simple(Witness(4))]",
-    "BLACKBOX::RANGE [(_3, 223)] []",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(0)), (-1, Witness(1))], q_c: 340282366920938463463374607431768211456 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(3)), Simple(Witness(4))]",
+    "BLACKBOX::RANGE [(_3, 222)] []",
     "BLACKBOX::RANGE [(_4, 32)] []",
-    "EXPR [ (1, _0) (-1, _1) (-4294967296, _3) (-1, _4) 340282366920938463463374607436063178752 ]",
+    "EXPR [ (1, _0) (-1, _1) (-4294967296, _3) (-1, _4) 340282366920938463463374607431768211456 ]",
     "EXPR [ (-1, _3) (-1, _5) 5096253676302562286669017222071363378443840053029366383258766538131 ]",
-    "BLACKBOX::RANGE [(_5, 223)] []",
+    "BLACKBOX::RANGE [(_5, 222)] []",
     "BRILLIG CALL func 1: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(3))], q_c: 5096253676302562286669017222071363378443840053029366383258766538131 })], outputs: [Simple(Witness(6))]",
     "EXPR [ (-1, _3, _6) (5096253676302562286669017222071363378443840053029366383258766538131, _6) (1, _7) -1 ]",
     "EXPR [ (-1, _3, _7) (5096253676302562286669017222071363378443840053029366383258766538131, _7) 0 ]",
```

### tooling/nargo_cli/tests/snapshots/execution_success/6_array/execute__tests__force_brillig_false_inliner_-9223372036854775808.snap
```diff
@@ -154,12 +154,12 @@ expression: artifact
     "BLACKBOX::RANGE [(_46, 32)] []",
     "EXPR [ (1, _1, _6) (-1, _47) 0 ]",
     "BLACKBOX::RANGE [(_47, 32)] []",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(42)), (1, Witness(47))], q_c: 340282366920938463463374607436063178752 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(48)), Simple(Witness(49))]",
-    "BLACKBOX::RANGE [(_48, 223)] []",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(42)), (1, Witness(47))], q_c: 340282366920938463463374607431768211456 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(48)), Simple(Witness(49))]",
+    "BLACKBOX::RANGE [(_48, 222)] []",
     "BLACKBOX::RANGE [(_49, 32)] []",
-    "EXPR [ (-1, _42) (1, _47) (-4294967296, _48) (-1, _49) 340282366920938463463374607436063178752 ]",
+    "EXPR [ (-1, _42) (1, _47) (-4294967296, _48) (-1, _49) 340282366920938463463374607431768211456 ]",
     "EXPR [ (-1, _48) (-1, _50) 5096253676302562286669017222071363378443840053029366383258766538131 ]",
-    "BLACKBOX::RANGE [(_50, 223)] []",
+    "BLACKBOX::RANGE [(_50, 222)] []",
     "BRILLIG CALL func 1: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(48))], q_c: 5096253676302562286669017222071363378443840053029366383258766538131 })], outputs: [Simple(Witness(51))]",
     "EXPR [ (-1, _48, _51) (5096253676302562286669017222071363378443840053029366383258766538131, _51) (1, _52) -1 ]",
     "EXPR [ (-1, _48, _52) (5096253676302562286669017222071363378443840053029366383258766538131, _52) 0 ]",
@@ -200,12 +200,12 @@ expression: artifact
     "BLACKBOX::RANGE [(_71, 32)] []",
     "EXPR [ (1, _2, _7) (-1, _72) 0 ]",
     "BLACKBOX::RANGE [(_72, 32)] []",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(67)), (1, Witness(72))], q_c: 340282366920938463463374607436063178752 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(73)), Simple(Witness(74))]",
-    "BLACKBOX::RANGE [(_73, 223)] []",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(67)), (1, Witness(72))], q_c: 340282366920938463463374607431768211456 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(73)), Simple(Witness(74))]",
+    "BLACKBOX::RANGE [(_73, 222)] []",
     "BLACKBOX::RANGE [(_74, 32)] []",
-    "EXPR [ (-1, _67) (1, _72) (-4294967296, _73) (-1, _74) 340282366920938463463374607436063178752 ]",
+    "EXPR [ (-1, _67) (1, _72) (-4294967296, _73) (-1, _74) 340282366920938463463374607431768211456 ]",
     "EXPR [ (-1, _73) (-1, _75) 5096253676302562286669017222071363378443840053029366383258766538131 ]",
-    "BLACKBOX::RANGE [(_75, 223)] []",
+    "BLACKBOX::RANGE [(_75, 222)] []",
     "BRILLIG CALL func 1: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(73))], q_c: 5096253676302562286669017222071363378443840053029366383258766538131 })], outputs: [Simple(Witness(76))]",
     "EXPR [ (-1, _73, _76) (5096253676302562286669017222071363378443840053029366383258766538131, _76) (1, _77) -1 ]",
     "EXPR [ (-1, _73, _77) (5096253676302562286669017222071363378443840053029366383258766538131, _77) 0 ]",
@@ -246,12 +246,12 @@ expression: artifact
     "BLACKBOX::RANGE [(_96, 32)] []",
     "EXPR [ (1, _3, _8) (-1, _97) 0 ]",
     "BLACKBOX::RANGE [(_97, 32)] []",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(92)), (1, Witness(97))], q_c: 340282366920938463463374607436063178752 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(98)), Simple(Witness(99))]",
-    "BLACKBOX::RANGE [(_98, 223)] []",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(92)), (1, Witness(97))], q_c: 340282366920938463463374607431768211456 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(98)), Simple(Witness(99))]",
+    "BLACKBOX::RANGE [(_98, 222)] []",
     "BLACKBOX::RANGE [(_99, 32)] []",
-    "EXPR [ (-1, _92) (1, _97) (-4294967296, _98) (-1, _99) 340282366920938463463374607436063178752 ]",
+    "EXPR [ (-1, _92) (1, _97) (-4294967296, _98) (-1, _99) 340282366920938463463374607431768211456 ]",
     "EXPR [ (-1, _98) (-1, _100) 5096253676302562286669017222071363378443840053029366383258766538131 ]",
-    "BLACKBOX::RANGE [(_100, 223)] []",
+    "BLACKBOX::RANGE [(_100, 222)] []",
     "BRILLIG CALL func 1: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(98))], q_c: 5096253676302562286669017222071363378443840053029366383258766538131 })], outputs: [Simple(Witness(101))]",
     "EXPR [ (-1, _98, _101) (5096253676302562286669017222071363378443840053029366383258766538131, _101) (1, _102) -1 ]",
     "EXPR [ (-1, _98, _102) (5096253676302562286669017222071363378443840053029366383258766538131, _102) 0 ]",
@@ -292,12 +292,12 @@ expression: artifact
     "BLACKBOX::RANGE [(_121, 32)] []",
     "EXPR [ (1, _4, _9) (-1, _122) 0 ]",
     "BLACKBOX::RANGE [(_122, 32)] []",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(117)), (1, Witness(122))], q_c: 340282366920938463463374607436063178752 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(123)), Simple(Witness(124))]",
-    "BLACKBOX::RANGE [(_123, 223)] []",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(117)), (1, Witness(122))], q_c: 340282366920938463463374607431768211456 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(123)), Simple(Witness(124))]",
+    "BLACKBOX::RANGE [(_123, 222)] []",
     "BLACKBOX::RANGE [(_124, 32)] []",
-    "EXPR [ (-1, _117) (1, _122) (-4294967296, _123) (-1, _124) 340282366920938463463374607436063178752 ]",
+    "EXPR [ (-1, _117) (1, _122) (-4294967296, _123) (-1, _124) 340282366920938463463374607431768211456 ]",
     "EXPR [ (-1, _123) (-1, _125) 5096253676302562286669017222071363378443840053029366383258766538131 ]",
-    "BLACKBOX::RANGE [(_125, 223)] []",
+    "BLACKBOX::RANGE [(_125, 222)] []",
     "BRILLIG CALL func 1: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(123))], q_c: 5096253676302562286669017222071363378443840053029366383258766538131 })], outputs: [Simple(Witness(126))]",
     "EXPR [ (-1, _123, _126) (5096253676302562286669017222071363378443840053029366383258766538131, _126) (1, _127) -1 ]",
     "EXPR [ (-1, _123, _127) (5096253676302562286669017222071363378443840053029366383258766538131, _127) 0 ]",
```

### tooling/nargo_cli/tests/snapshots/execution_success/6_array/execute__tests__force_brillig_false_inliner_0.snap
```diff
@@ -154,12 +154,12 @@ expression: artifact
     "BLACKBOX::RANGE [(_46, 32)] []",
     "EXPR [ (1, _1, _6) (-1, _47) 0 ]",
     "BLACKBOX::RANGE [(_47, 32)] []",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(42)), (1, Witness(47))], q_c: 340282366920938463463374607436063178752 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(48)), Simple(Witness(49))]",
-    "BLACKBOX::RANGE [(_48, 223)] []",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(42)), (1, Witness(47))], q_c: 340282366920938463463374607431768211456 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(48)), Simple(Witness(49))]",
+    "BLACKBOX::RANGE [(_48, 222)] []",
     "BLACKBOX::RANGE [(_49, 32)] []",
-    "EXPR [ (-1, _42) (1, _47) (-4294967296, _48) (-1, _49) 340282366920938463463374607436063178752 ]",
+    "EXPR [ (-1, _42) (1, _47) (-4294967296, _48) (-1, _49) 340282366920938463463374607431768211456 ]",
     "EXPR [ (-1, _48) (-1, _50) 5096253676302562286669017222071363378443840053029366383258766538131 ]",
-    "BLACKBOX::RANGE [(_50, 223)] []",
+    "BLACKBOX::RANGE [(_50, 222)] []",
     "BRILLIG CALL func 1: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(48))], q_c: 5096253676302562286669017222071363378443840053029366383258766538131 })], outputs: [Simple(Witness(51))]",
     "EXPR [ (-1, _48, _51) (5096253676302562286669017222071363378443840053029366383258766538131, _51) (1, _52) -1 ]",
     "EXPR [ (-1, _48, _52) (5096253676302562286669017222071363378443840053029366383258766538131, _52) 0 ]",
@@ -200,12 +200,12 @@ expression: artifact
     "BLACKBOX::RANGE [(_71, 32)] []",
     "EXPR [ (1, _2, _7) (-1, _72) 0 ]",
     "BLACKBOX::RANGE [(_72, 32)] []",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(67)), (1, Witness(72))], q_c: 340282366920938463463374607436063178752 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(73)), Simple(Witness(74))]",
-    "BLACKBOX::RANGE [(_73, 223)] []",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(67)), (1, Witness(72))], q_c: 340282366920938463463374607431768211456 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(73)), Simple(Witness(74))]",
+    "BLACKBOX::RANGE [(_73, 222)] []",
     "BLACKBOX::RANGE [(_74, 32)] []",
-    "EXPR [ (-1, _67) (1, _72) (-4294967296, _73) (-1, _74) 340282366920938463463374607436063178752 ]",
+    "EXPR [ (-1, _67) (1, _72) (-4294967296, _73) (-1, _74) 340282366920938463463374607431768211456 ]",
     "EXPR [ (-1, _73) (-1, _75) 5096253676302562286669017222071363378443840053029366383258766538131 ]",
-    "BLACKBOX::RANGE [(_75, 223)] []",
+    "BLACKBOX::RANGE [(_75, 222)] []",
     "BRILLIG CALL func 1: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(73))], q_c: 5096253676302562286669017222071363378443840053029366383258766538131 })], outputs: [Simple(Witness(76))]",
     "EXPR [ (-1, _73, _76) (5096253676302562286669017222071363378443840053029366383258766538131, _76) (1, _77) -1 ]",
     "EXPR [ (-1, _73, _77) (5096253676302562286669017222071363378443840053029366383258766538131, _77) 0 ]",
@@ -246,12 +246,12 @@ expression: artifact
     "BLACKBOX::RANGE [(_96, 32)] []",
     "EXPR [ (1, _3, _8) (-1, _97) 0 ]",
     "BLACKBOX::RANGE [(_97, 32)] []",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(92)), (1, Witness(97))], q_c: 340282366920938463463374607436063178752 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(98)), Simple(Witness(99))]",
-    "BLACKBOX::RANGE [(_98, 223)] []",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(92)), (1, Witness(97))], q_c: 340282366920938463463374607431768211456 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(98)), Simple(Witness(99))]",
+    "BLACKBOX::RANGE [(_98, 222)] []",
     "BLACKBOX::RANGE [(_99, 32)] []",
-    "EXPR [ (-1, _92) (1, _97) (-4294967296, _98) (-1, _99) 340282366920938463463374607436063178752 ]",
+    "EXPR [ (-1, _92) (1, _97) (-4294967296, _98) (-1, _99) 340282366920938463463374607431768211456 ]",
     "EXPR [ (-1, _98) (-1, _100) 5096253676302562286669017222071363378443840053029366383258766538131 ]",
-    "BLACKBOX::RANGE [(_100, 223)] []",
+    "BLACKBOX::RANGE [(_100, 222)] []",
     "BRILLIG CALL func 1: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(98))], q_c: 5096253676302562286669017222071363378443840053029366383258766538131 })], outputs: [Simple(Witness(101))]",
     "EXPR [ (-1, _98, _101) (5096253676302562286669017222071363378443840053029366383258766538131, _101) (1, _102) -1 ]",
     "EXPR [ (-1, _98, _102) (5096253676302562286669017222071363378443840053029366383258766538131, _102) 0 ]",
@@ -292,12 +292,12 @@ expression: artifact
     "BLACKBOX::RANGE [(_121, 32)] []",
     "EXPR [ (1, _4, _9) (-1, _122) 0 ]",
     "BLACKBOX::RANGE [(_122, 32)] []",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(117)), (1, Witness(122))], q_c: 340282366920938463463374607436063178752 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(123)), Simple(Witness(124))]",
-    "BLACKBOX::RANGE [(_123, 223)] []",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(117)), (1, Witness(122))], q_c: 340282366920938463463374607431768211456 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(123)), Simple(Witness(124))]",
+    "BLACKBOX::RANGE [(_123, 222)] []",
     "BLACKBOX::RANGE [(_124, 32)] []",
-    "EXPR [ (-1, _117) (1, _122) (-4294967296, _123) (-1, _124) 340282366920938463463374607436063178752 ]",
+    "EXPR [ (-1, _117) (1, _122) (-4294967296, _123) (-1, _124) 340282366920938463463374607431768211456 ]",
     "EXPR [ (-1, _123) (-1, _125) 5096253676302562286669017222071363378443840053029366383258766538131 ]",
-    "BLACKBOX::RANGE [(_125, 223)] []",
+    "BLACKBOX::RANGE [(_125, 222)] []",
     "BRILLIG CALL func 1: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(123))], q_c: 5096253676302562286669017222071363378443840053029366383258766538131 })], outputs: [Simple(Witness(126))]",
     "EXPR [ (-1, _123, _126) (5096253676302562286669017222071363378443840053029366383258766538131, _126) (1, _127) -1 ]",
     "EXPR [ (-1, _123, _127) (5096253676302562286669017222071363378443840053029366383258766538131, _127) 0 ]",
```

### tooling/nargo_cli/tests/snapshots/execution_success/6_array/execute__tests__force_brillig_false_inliner_9223372036854775807.snap
```diff
@@ -154,12 +154,12 @@ expression: artifact
     "BLACKBOX::RANGE [(_46, 32)] []",
     "EXPR [ (1, _1, _6) (-1, _47) 0 ]",
     "BLACKBOX::RANGE [(_47, 32)] []",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(42)), (1, Witness(47))], q_c: 340282366920938463463374607436063178752 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(48)), Simple(Witness(49))]",
-    "BLACKBOX::RANGE [(_48, 223)] []",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(42)), (1, Witness(47))], q_c: 340282366920938463463374607431768211456 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(48)), Simple(Witness(49))]",
+    "BLACKBOX::RANGE [(_48, 222)] []",
     "BLACKBOX::RANGE [(_49, 32)] []",
-    "EXPR [ (-1, _42) (1, _47) (-4294967296, _48) (-1, _49) 340282366920938463463374607436063178752 ]",
+    "EXPR [ (-1, _42) (1, _47) (-4294967296, _48) (-1, _49) 340282366920938463463374607431768211456 ]",
     "EXPR [ (-1, _48) (-1, _50) 5096253676302562286669017222071363378443840053029366383258766538131 ]",
-    "BLACKBOX::RANGE [(_50, 223)] []",
+    "BLACKBOX::RANGE [(_50, 222)] []",
     "BRILLIG CALL func 1: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(48))], q_c: 5096253676302562286669017222071363378443840053029366383258766538131 })], outputs: [Simple(Witness(51))]",
     "EXPR [ (-1, _48, _51) (5096253676302562286669017222071363378443840053029366383258766538131, _51) (1, _52) -1 ]",
     "EXPR [ (-1, _48, _52) (5096253676302562286669017222071363378443840053029366383258766538131, _52) 0 ]",
@@ -200,12 +200,12 @@ expression: artifact
     "BLACKBOX::RANGE [(_71, 32)] []",
     "EXPR [ (1, _2, _7) (-1, _72) 0 ]",
     "BLACKBOX::RANGE [(_72, 32)] []",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(67)), (1, Witness(72))], q_c: 340282366920938463463374607436063178752 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(73)), Simple(Witness(74))]",
-    "BLACKBOX::RANGE [(_73, 223)] []",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(67)), (1, Witness(72))], q_c: 340282366920938463463374607431768211456 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(73)), Simple(Witness(74))]",
+    "BLACKBOX::RANGE [(_73, 222)] []",
     "BLACKBOX::RANGE [(_74, 32)] []",
-    "EXPR [ (-1, _67) (1, _72) (-4294967296, _73) (-1, _74) 340282366920938463463374607436063178752 ]",
+    "EXPR [ (-1, _67) (1, _72) (-4294967296, _73) (-1, _74) 340282366920938463463374607431768211456 ]",
     "EXPR [ (-1, _73) (-1, _75) 5096253676302562286669017222071363378443840053029366383258766538131 ]",
-    "BLACKBOX::RANGE [(_75, 223)] []",
+    "BLACKBOX::RANGE [(_75, 222)] []",
     "BRILLIG CALL func 1: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(73))], q_c: 5096253676302562286669017222071363378443840053029366383258766538131 })], outputs: [Simple(Witness(76))]",
     "EXPR [ (-1, _73, _76) (5096253676302562286669017222071363378443840053029366383258766538131, _76) (1, _77) -1 ]",
     "EXPR [ (-1, _73, _77) (5096253676302562286669017222071363378443840053029366383258766538131, _77) 0 ]",
@@ -246,12 +246,12 @@ expression: artifact
     "BLACKBOX::RANGE [(_96, 32)] []",
     "EXPR [ (1, _3, _8) (-1, _97) 0 ]",
     "BLACKBOX::RANGE [(_97, 32)] []",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(92)), (1, Witness(97))], q_c: 340282366920938463463374607436063178752 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(98)), Simple(Witness(99))]",
-    "BLACKBOX::RANGE [(_98, 223)] []",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(92)), (1, Witness(97))], q_c: 340282366920938463463374607431768211456 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(98)), Simple(Witness(99))]",
+    "BLACKBOX::RANGE [(_98, 222)] []",
     "BLACKBOX::RANGE [(_99, 32)] []",
-    "EXPR [ (-1, _92) (1, _97) (-4294967296, _98) (-1, _99) 340282366920938463463374607436063178752 ]",
+    "EXPR [ (-1, _92) (1, _97) (-4294967296, _98) (-1, _99) 340282366920938463463374607431768211456 ]",
     "EXPR [ (-1, _98) (-1, _100) 5096253676302562286669017222071363378443840053029366383258766538131 ]",
-    "BLACKBOX::RANGE [(_100, 223)] []",
+    "BLACKBOX::RANGE [(_100, 222)] []",
     "BRILLIG CALL func 1: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(98))], q_c: 5096253676302562286669017222071363378443840053029366383258766538131 })], outputs: [Simple(Witness(101))]",
     "EXPR [ (-1, _98, _101) (5096253676302562286669017222071363378443840053029366383258766538131, _101) (1, _102) -1 ]",
     "EXPR [ (-1, _98, _102) (5096253676302562286669017222071363378443840053029366383258766538131, _102) 0 ]",
@@ -292,12 +292,12 @@ expression: artifact
     "BLACKBOX::RANGE [(_121, 32)] []",
     "EXPR [ (1, _4, _9) (-1, _122) 0 ]",
     "BLACKBOX::RANGE [(_122, 32)] []",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(117)), (1, Witness(122))], q_c: 340282366920938463463374607436063178752 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(123)), Simple(Witness(124))]",
-    "BLACKBOX::RANGE [(_123, 223)] []",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(117)), (1, Witness(122))], q_c: 340282366920938463463374607431768211456 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 4294967296 })], outputs: [Simple(Witness(123)), Simple(Witness(124))]",
+    "BLACKBOX::RANGE [(_123, 222)] []",
     "BLACKBOX::RANGE [(_124, 32)] []",
-    "EXPR [ (-1, _117) (1, _122) (-4294967296, _123) (-1, _124) 340282366920938463463374607436063178752 ]",
+    "EXPR [ (-1, _117) (1, _122) (-4294967296, _123) (-1, _124) 340282366920938463463374607431768211456 ]",
     "EXPR [ (-1, _123) (-1, _125) 5096253676302562286669017222071363378443840053029366383258766538131 ]",
-    "BLACKBOX::RANGE [(_125, 223)] []",
+    "BLACKBOX::RANGE [(_125, 222)] []",
     "BRILLIG CALL func 1: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(123))], q_c: 5096253676302562286669017222071363378443840053029366383258766538131 })], outputs: [Simple(Witness(126))]",
     "EXPR [ (-1, _123, _126) (5096253676302562286669017222071363378443840053029366383258766538131, _126) (1, _127) -1 ]",
     "EXPR [ (-1, _123, _127) (5096253676302562286669017222071363378443840053029366383258766538131, _127) 0 ]",
```

### tooling/nargo_cli/tests/snapshots/execution_success/bit_shifts_runtime/execute__tests__force_brillig_false_inliner_-9223372036854775808.snap
```diff
@@ -228,10 +228,10 @@ expression: artifact
     "EXPR [ (1, _105, _114) 0 ]",
     "EXPR [ (-2, _99, _105) (18446744073709551616, _99) (1, _105) (-1, _115) 0 ]",
     "EXPR [ (-1, _114) (-1, _116) 1 ]",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(93), Witness(91)), (1, Witness(111), Witness(112))], linear_combinations: [(1, Witness(91)), (1, Witness(93))], q_c: 18446744073709551615 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 18446744073709551616 })], outputs: [Simple(Witness(117)), Simple(Witness(118))]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(93), Witness(91)), (1, Witness(111), Witness(112))], linear_combinations: [(1, Witness(91)), (1, Witness(93))], q_c: 36893488147419103231 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 18446744073709551616 })], outputs: [Simple(Witness(117)), Simple(Witness(118))]",
     "BLACKBOX::RANGE [(_117, 2)] []",
     "BLACKBOX::RANGE [(_118, 64)] []",
-    "EXPR [ (-2, _91, _93) (1, _111, _112) (1, _91) (1, _93) (-18446744073709551616, _117) (-1, _118) 18446744073709551615 ]",
+    "EXPR [ (-2, _91, _93) (1, _111, _112) (1, _91) (1, _93) (-18446744073709551616, _117) (-1, _118) 36893488147419103231 ]",
     "EXPR [ (-1, _61, _118) (1, _118) 0 ]",
     "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(60))], q_c: 240 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(119)), Simple(Witness(120))]",
     "BLACKBOX::RANGE [(_119, 1)] []",
@@ -311,10 +311,10 @@ expression: artifact
     "EXPR [ (1, _163, _172) 0 ]",
     "EXPR [ (-2, _157, _163) (65536, _157) (1, _163) (-1, _173) 0 ]",
     "EXPR [ (-1, _172) (-1, _174) 1 ]",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(151), Witness(149)), (1, Witness(169), Witness(170))], linear_combinations: [(1, Witness(149)), (1, Witness(151))], q_c: 65535 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 65536 })], outputs: [Simple(Witness(175)), Simple(Witness(176))]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(151), Witness(149)), (1, Witness(169), Witness(170))], linear_combinations: [(1, Witness(149)), (1, Witness(151))], q_c: 131071 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 65536 })], outputs: [Simple(Witness(175)), Simple(Witness(176))]",
     "BLACKBOX::RANGE [(_175, 2)] []",
     "BLACKBOX::RANGE [(_176, 16)] []",
-    "EXPR [ (-2, _149, _151) (1, _169, _170) (1, _149) (1, _151) (-65536, _175) (-1, _176) 65535 ]",
+    "EXPR [ (-2, _149, _151) (1, _169, _170) (1, _149) (1, _151) (-65536, _175) (-1, _176) 131071 ]",
     "EXPR [ (-1, _119, _176) (1, _176) 0 ]",
     "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(2, Witness(60))], q_c: 0 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(177)), Simple(Witness(178))]",
     "BLACKBOX::RANGE [(_177, 1)] []",
@@ -354,9 +354,9 @@ expression: artifact
     "EXPR [ (1, _190, _196) 0 ]",
     "EXPR [ (-2, _187, _190) (256, _187) (1, _190) (-1, _197) 0 ]",
     "EXPR [ (-1, _196) (-1, _198) 1 ]",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(183), Witness(181)), (1, Witness(193), Witness(194))], linear_combinations: [(1, Witness(181)), (1, Witness(183))], q_c: 255 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(199)), Simple(Witness(200))]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(183), Witness(181)), (1, Witness(193), Witness(194))], linear_combinations: [(1, Witness(181)), (1, Witness(183))], q_c: 511 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(199)), Simple(Witness(200))]",
     "BLACKBOX::RANGE [(_199, 2)] []",
-    "EXPR [ (-2, _181, _183) (1, _193, _194) (1, _181) (1, _183) (-256, _199) (-1, _200) 255 ]",
+    "EXPR [ (-2, _181, _183) (1, _193, _194) (1, _181) (1, _183) (-256, _199) (-1, _200) 511 ]",
     "EXPR [ (1, _200) -16 ]",
     "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(1))], q_c: 248 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(201)), Simple(Witness(202))]",
     "BLACKBOX::RANGE [(_202, 8)] []",
@@ -423,15 +423,15 @@ expression: artifact
     "EXPR [ (1, _239, _248) 0 ]",
     "EXPR [ (-2, _233, _239) (256, _233) (1, _239) (-1, _249) 0 ]",
     "EXPR [ (-1, _248) (-1, _250) 1 ]",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(183), Witness(181)), (1, Witness(245), Witness(246))], linear_combinations: [(1, Witness(181)), (1, Witness(183))], q_c: 255 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(251)), Simple(Witness(252))]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(183), Witness(181)), (1, Witness(245), Witness(246))], linear_combinations: [(1, Witness(181)), (1, Witness(183))], q_c: 511 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(251)), Simple(Witness(252))]",
     "BLACKBOX::RANGE [(_251, 2)] []",
     "BLACKBOX::RANGE [(_252, 8)] []",
-    "EXPR [ (-2, _181, _183) (1, _245, _246) (1, _181) (1, _183) (-256, _251) (-1, _252) 255 ]",
+    "EXPR [ (-2, _181, _183) (1, _245, _246) (1, _181) (1, _183) (-256, _251) (-1, _252) 511 ]",
     "EXPR [ (-1, _201, _252) (1, _252) -32 ]",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(1))], q_c: 256 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(253)), Simple(Witness(254))]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(1))], q_c: 512 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(253)), Simple(Witness(254))]",
     "BLACKBOX::RANGE [(_253, 2)] []",
     "BLACKBOX::RANGE [(_254, 8)] []",
-    "EXPR [ (-1, _1) (-256, _253) (-1, _254) 256 ]",
+    "EXPR [ (-1, _1) (-256, _253) (-1, _254) 512 ]",
     "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(1))], q_c: 128 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(255)), Simple(Witness(256))]",
     "BLACKBOX::RANGE [(_255, 1)] []",
     "BLACKBOX::RANGE [(_256, 8)] []",
@@ -494,9 +494,9 @@ expression: artifact
     "EXPR [ (1, _280, _286) 0 ]",
     "EXPR [ (-2, _277, _280) (65536, _277) (1, _280) (-1, _287) 0 ]",
     "EXPR [ (-1, _286) (-1, _288) 1 ]",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(151), Witness(149)), (1, Witness(283), Witness(284))], linear_combinations: [(1, Witness(149)), (1, Witness(151))], q_c: 65535 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 65536 })], outputs: [Simple(Witness(289)), Simple(Witness(290))]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(151), Witness(149)), (1, Witness(283), Witness(284))], linear_combinations: [(1, Witness(149)), (1, Witness(151))], q_c: 131071 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 65536 })], outputs: [Simple(Witness(289)), Simple(Witness(290))]",
     "BLACKBOX::RANGE [(_289, 2)] []",
-    "EXPR [ (-2, _149, _151) (1, _283, _284) (1, _149) (1, _151) (-65536, _289) (-1, _290) 65535 ]",
+    "EXPR [ (-2, _149, _151) (1, _283, _284) (1, _149) (1, _151) (-65536, _289) (-1, _290) 131071 ]",
     "EXPR [ (1, _290) -65439 ]",
     "unconstrained func 0",
     "[Const { destination: Direct(10), bit_size: Integer(U32), value: 2 }, Const { destination: Direct(11), bit_size: Integer(U32), value: 0 }, CalldataCopy { destination_address: Direct(0), size_address: Direct(10), offset_address: Direct(11) }, BinaryFieldOp { destination: Direct(2), op: IntegerDiv, lhs: Direct(0), rhs: Direct(1) }, BinaryFieldOp { destination: Direct(1), op: Mul, lhs: Direct(2), rhs: Direct(1) }, BinaryFieldOp { destination: Direct(1), op: Sub, lhs: Direct(0), rhs: Direct(1) }, Mov { destination: Direct(0), source: Direct(2) }, Stop { return_data: HeapVector { pointer: Direct(11), size: Direct(10) } }]",
```

### tooling/nargo_cli/tests/snapshots/execution_success/bit_shifts_runtime/execute__tests__force_brillig_false_inliner_0.snap
```diff
@@ -228,10 +228,10 @@ expression: artifact
     "EXPR [ (1, _105, _114) 0 ]",
     "EXPR [ (-2, _99, _105) (18446744073709551616, _99) (1, _105) (-1, _115) 0 ]",
     "EXPR [ (-1, _114) (-1, _116) 1 ]",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(93), Witness(91)), (1, Witness(111), Witness(112))], linear_combinations: [(1, Witness(91)), (1, Witness(93))], q_c: 18446744073709551615 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 18446744073709551616 })], outputs: [Simple(Witness(117)), Simple(Witness(118))]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(93), Witness(91)), (1, Witness(111), Witness(112))], linear_combinations: [(1, Witness(91)), (1, Witness(93))], q_c: 36893488147419103231 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 18446744073709551616 })], outputs: [Simple(Witness(117)), Simple(Witness(118))]",
     "BLACKBOX::RANGE [(_117, 2)] []",
     "BLACKBOX::RANGE [(_118, 64)] []",
-    "EXPR [ (-2, _91, _93) (1, _111, _112) (1, _91) (1, _93) (-18446744073709551616, _117) (-1, _118) 18446744073709551615 ]",
+    "EXPR [ (-2, _91, _93) (1, _111, _112) (1, _91) (1, _93) (-18446744073709551616, _117) (-1, _118) 36893488147419103231 ]",
     "EXPR [ (-1, _61, _118) (1, _118) 0 ]",
     "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(60))], q_c: 240 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(119)), Simple(Witness(120))]",
     "BLACKBOX::RANGE [(_119, 1)] []",
@@ -311,10 +311,10 @@ expression: artifact
     "EXPR [ (1, _163, _172) 0 ]",
     "EXPR [ (-2, _157, _163) (65536, _157) (1, _163) (-1, _173) 0 ]",
     "EXPR [ (-1, _172) (-1, _174) 1 ]",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(151), Witness(149)), (1, Witness(169), Witness(170))], linear_combinations: [(1, Witness(149)), (1, Witness(151))], q_c: 65535 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 65536 })], outputs: [Simple(Witness(175)), Simple(Witness(176))]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(151), Witness(149)), (1, Witness(169), Witness(170))], linear_combinations: [(1, Witness(149)), (1, Witness(151))], q_c: 131071 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 65536 })], outputs: [Simple(Witness(175)), Simple(Witness(176))]",
     "BLACKBOX::RANGE [(_175, 2)] []",
     "BLACKBOX::RANGE [(_176, 16)] []",
-    "EXPR [ (-2, _149, _151) (1, _169, _170) (1, _149) (1, _151) (-65536, _175) (-1, _176) 65535 ]",
+    "EXPR [ (-2, _149, _151) (1, _169, _170) (1, _149) (1, _151) (-65536, _175) (-1, _176) 131071 ]",
     "EXPR [ (-1, _119, _176) (1, _176) 0 ]",
     "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(2, Witness(60))], q_c: 0 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(177)), Simple(Witness(178))]",
     "BLACKBOX::RANGE [(_177, 1)] []",
@@ -354,9 +354,9 @@ expression: artifact
     "EXPR [ (1, _190, _196) 0 ]",
     "EXPR [ (-2, _187, _190) (256, _187) (1, _190) (-1, _197) 0 ]",
     "EXPR [ (-1, _196) (-1, _198) 1 ]",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(183), Witness(181)), (1, Witness(193), Witness(194))], linear_combinations: [(1, Witness(181)), (1, Witness(183))], q_c: 255 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(199)), Simple(Witness(200))]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(183), Witness(181)), (1, Witness(193), Witness(194))], linear_combinations: [(1, Witness(181)), (1, Witness(183))], q_c: 511 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(199)), Simple(Witness(200))]",
     "BLACKBOX::RANGE [(_199, 2)] []",
-    "EXPR [ (-2, _181, _183) (1, _193, _194) (1, _181) (1, _183) (-256, _199) (-1, _200) 255 ]",
+    "EXPR [ (-2, _181, _183) (1, _193, _194) (1, _181) (1, _183) (-256, _199) (-1, _200) 511 ]",
     "EXPR [ (1, _200) -16 ]",
     "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(1))], q_c: 248 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(201)), Simple(Witness(202))]",
     "BLACKBOX::RANGE [(_202, 8)] []",
@@ -423,15 +423,15 @@ expression: artifact
     "EXPR [ (1, _239, _248) 0 ]",
     "EXPR [ (-2, _233, _239) (256, _233) (1, _239) (-1, _249) 0 ]",
     "EXPR [ (-1, _248) (-1, _250) 1 ]",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(183), Witness(181)), (1, Witness(245), Witness(246))], linear_combinations: [(1, Witness(181)), (1, Witness(183))], q_c: 255 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(251)), Simple(Witness(252))]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(183), Witness(181)), (1, Witness(245), Witness(246))], linear_combinations: [(1, Witness(181)), (1, Witness(183))], q_c: 511 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(251)), Simple(Witness(252))]",
     "BLACKBOX::RANGE [(_251, 2)] []",
     "BLACKBOX::RANGE [(_252, 8)] []",
-    "EXPR [ (-2, _181, _183) (1, _245, _246) (1, _181) (1, _183) (-256, _251) (-1, _252) 255 ]",
+    "EXPR [ (-2, _181, _183) (1, _245, _246) (1, _181) (1, _183) (-256, _251) (-1, _252) 511 ]",
     "EXPR [ (-1, _201, _252) (1, _252) -32 ]",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(1))], q_c: 256 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(253)), Simple(Witness(254))]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(1))], q_c: 512 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(253)), Simple(Witness(254))]",
     "BLACKBOX::RANGE [(_253, 2)] []",
     "BLACKBOX::RANGE [(_254, 8)] []",
-    "EXPR [ (-1, _1) (-256, _253) (-1, _254) 256 ]",
+    "EXPR [ (-1, _1) (-256, _253) (-1, _254) 512 ]",
     "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(1))], q_c: 128 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(255)), Simple(Witness(256))]",
     "BLACKBOX::RANGE [(_255, 1)] []",
     "BLACKBOX::RANGE [(_256, 8)] []",
@@ -494,9 +494,9 @@ expression: artifact
     "EXPR [ (1, _280, _286) 0 ]",
     "EXPR [ (-2, _277, _280) (65536, _277) (1, _280) (-1, _287) 0 ]",
     "EXPR [ (-1, _286) (-1, _288) 1 ]",
-    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(151), Witness(149)), (1, Witness(283), Witness(284))], linear_combinations: [(1, Witness(149)), (1, Witness(151))], q_c: 65535 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 65536 })], outputs: [Simple(Witness(289)), Simple(Witness(290))]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(151), Witness(149)), (1, Witness(283), Witness(284))], linear_combinations: [(1, Witness(149)), (1, Witness(151))], q_c: 131071 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 65536 })], outputs: [Simple(Witness(289)), Simple(Witness(290))]",
     "BLACKBOX::RANGE [(_289, 2)] []",
-    "EXPR [ (-2, _149, _151) (1, _283, _284) (1, _149) (1, _151) (-65536, _289) (-1, _290) 65535 ]",
+    "EXPR [ (-2, _149, _151) (1, _283, _284) (1, _149) (1, _151) (-65536, _289) (-1, _290) 131071 ]",
     "EXPR [ (1, _290) -65439 ]",
     "unconstrained func 0",
     "[Const { destination: Direct(10), bit_size: Integer(U32), value: 2 }, Const { destination: Direct(11), bit_size: Integer(U32), value: 0 }, CalldataCopy { destination_address: Direct(0), size_address: Direct(10), offset_address: Direct(11) }, BinaryFieldOp { destination: Direct(2), op: IntegerDiv, lhs: Direct(0), rhs: Direct(1) }, BinaryFieldOp { destination: Direct(1), op: Mul, lhs: Direct(2), rhs: Direct(1) }, BinaryFieldOp { destination: Direct(1), op: Sub, lhs: Direct(0), rhs: Direct(1) }, Mov { destination: Direct(0), source: Direct(2) }, Stop { return_data: HeapVector { pointer: Direct(11), size: Direct(10) } }]",
```
