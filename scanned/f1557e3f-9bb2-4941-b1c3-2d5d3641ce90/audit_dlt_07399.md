# [?] fix(symbolic): normalize constant mul-div overflow guards (#16932)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-09-21
Source: https://github.com/foundry-rs/foundry/commit/c9282ee9a0dce1cc350733a8e124f18b6252fd6b
Type: security-commit

## Details
fix(symbolic): normalize constant mul-div overflow guards (#16932)

* fix(symbolic): normalize constant mul-div overflow guards

For a constant k > 0, `(x * k mod 2^256) / k == x` holds iff `x <= MAX / k`. Rewrite that guard, and its negation, into the exact bound instead of asking SMT to solve the overflow check. This lets the OUSD-style opt-out round trip prove without an explicit balance bound, while unchecked wrapping products still produce counterexamples.

Add a full-width opt-out fixture with a concrete witness at the credit limit and an unchecked constant-product regression.

* test(symbolic): cover mul-div guard exclusions and solver path

Add matcher-exclusion cases for the constant mul-div guard rewrite: zero factor, signed division, mismatched divisor, mismatched expected value, and symbolic factor. Each shape must keep its original semantics and must not become the overflow bound.

Exercise the solver and its sat cache on both the guard and its negation, with and without the matching bound, and check that every branch is decided without an SMT query.

* test(symbolic): drop vacuous zero-factor exclusion case

`SymExpr::binop` folds `value * 0` and `0 / 0` to a constant before the matcher runs, so the zero-factor case never exercised the rewrite. Remove it and document the non-zero filter as a defensive guard against `MAX / 0`.

## Patch
### crates/evm/symbolic/src/runtime/solver/normalize/mod.rs
```diff
@@ -405,6 +405,19 @@ fn normalize_cmp_for_solver(
     right: SymExpr,
 ) -> SymBoolExpr {
     if op == SymCmpOp::Eq {
+        for (quotient, expected) in [(&left, &right), (&right, &left)] {
+            if let Some((denominator, value)) =
+                ConstraintContext::mul_div_identity_operands(quotient, expected)
+                && let Some(factor) = denominator.as_const().filter(|value| !value.is_zero())
+            {
+                // For constant k > 0, (x * k mod 2^256) / k == x iff x <= MAX / k.
+                // The quotient cannot exceed MAX / k; conversely this bound prevents wrapping.
+                // Retain that exact bound instead of asking SMT to solve the overflow check.
+                // `SymExpr::binop` folds a zero factor away, so the non-zero filter is only a
+                // defensive guard against `MAX / 0` should that folding ever change.
+                return SymBoolExpr::cmp_word_const(cx, SymCmpOp::Ule, value, U256::MAX / factor);
+            }
+        }
         if right.as_const().is_some_and(|value| value.is_zero())
             && let SymExprKind::BinOp(SymBinOp::Sub, minuend, subtrahend) = left.kind()
         {
```

### crates/evm/symbolic/src/runtime/solver/normalize/tests.rs
```diff
@@ -512,6 +512,94 @@ fn quotient_bounds_do_not_require_bounded_numerators() {
     assert!(context.interval(&quotient).is_none());
 }
 
+#[test]
+fn constant_mul_div_guard_becomes_exact_overflow_bound() {
+    let mut cx = SymCx::new();
+    let value = SymExpr::var(&mut cx, "value");
+    for factor in
+        [U256::from(10), U256::from(3), U256::from(1_000_000_000_000_000_000u64), U256::MAX]
+    {
+        let scale = SymExpr::constant(&mut cx, factor);
+        let product = SymExpr::binop(&mut cx, SymBinOp::Mul, value.clone(), scale.clone());
+        let quotient = SymExpr::binop(&mut cx, SymBinOp::UDiv, product, scale);
+        let guard = SymBoolExpr::eq(&mut cx, quotient, value.clone());
+        let expected =
+            SymBoolExpr::cmp_word_const(&mut cx, SymCmpOp::Ule, &value, U256::MAX / factor);
+        for (original, expected) in
+            [(guard.clone(), expected.clone()), (guard.not(&mut cx), expected.not(&mut cx))]
+        {
+            let normalized = normalize_bool_for_solver(&mut cx, original.clone());
+            assert_eq!(normalized, expected, "factor={factor}");
+            for input in [
+                U256::ZERO,
+                U256::ONE,
+                U256::from(2),
+                U256::MAX / factor,
+                U256::MAX / factor + U256::ONE,
+                U256::ONE << 255,
+                U256::MAX,
+            ] {
+                let mut model = SymbolicModel::default();
+                assert!(value.assign_model_value(&mut model, input));
+                assert_eq!(
+                    original.eval_model(&model).unwrap(),
+                    normalized.eval_model(&model).unwrap(),
+                    "factor={factor}, input={input}",
+                );
+            }
+        }
+    }
+}
+
+#[test]
+fn constant_mul_div_guard_rewrite_excludes_unsound_shapes() {
+    let mut cx = SymCx::new();
+    let value = SymExpr::var(&mut cx, "value");
+    let other = SymExpr::var(&mut cx, "other");
+    let three = SymExpr::constant(&mut cx, U256::from(3));
+    let ten_value = U256::from(10);
+    let ten = SymExpr::constant(&mut cx, ten_value);
+    let rewritten =
+        SymBoolExpr::cmp_word_const(&mut cx, SymCmpOp::Ule, &value, U256::MAX / ten_value);
+
+    // (name, factor, division, divisor, expected side of the equality)
+    let cases = [
+        ("signed division", ten.clone(), SymBinOp::SDiv, ten.clone(), value.clone()),
+        ("mismatched divisor", ten.clone(), SymBinOp::UDiv, three, value.clone()),
+        ("mismatched expected value", ten.clone(), SymBinOp::UDiv, ten, other.clone()),
+        ("symbolic factor", other.clone(), SymBinOp::UDiv, other.clone(), value.clone()),
+    ];
+    for (name, factor, division, divisor, expected) in cases {
+        let product = SymExpr::binop(&mut cx, SymBinOp::Mul, value.clone(), factor);
+        let quotient = SymExpr::binop(&mut cx, division, product, divisor);
+        let guard = SymBoolExpr::eq(&mut cx, quotient, expected);
+        for original in [guard.clone(), guard.not(&mut cx)] {
+            let normalized = normalize_bool_for_solver(&mut cx, original.clone());
+            assert_ne!(normalized, rewritten, "{name}");
+            assert_ne!(normalized, rewritten.clone().not(&mut cx), "{name}");
+            for value_input in [
+                U256::ZERO,
+                U256::ONE,
+                U256::MAX / ten_value,
+                U256::MAX / ten_value + U256::ONE,
+                U256::ONE << 255,
+                U256::MAX,
+            ] {
+                for other_input in [U256::ZERO, U256::ONE, U256::from(3), U256::MAX] {
+                    let mut model = SymbolicModel::default();
+                    assert!(value.assign_model_value(&mut model, value_input));
+                    assert!(other.assign_model_value(&mut model, other_input));
+                    assert_eq!(
+                        original.eval_model(&model).unwrap(),
+                        normalized.eval_model(&model).unwrap(),
+                        "{name}: value={value_input}, other={other_input}",
+                    );
+                }
+            }
+        }
+    }
+}
+
 #[test]
 fn scaled_zero_branch_proves_full_width_round_trip() {
     let mut cx = SymCx::new();
```

### crates/evm/symbolic/src/tests.rs
```diff
@@ -4301,18 +4301,68 @@ fn solver_normalizes_mul_div_at_exact_no_wrap_boundary() {
 }
 
 #[test]
-fn solver_does_not_normalize_wrapping_mul_div_identity() {
+fn solver_preserves_wrapping_mul_div_counterexamples() {
     let mut cx = SymCx::new();
     let value = SymExpr::var(&mut cx, "value");
-    let factor = SymExpr::constant(&mut cx, U256::from(58));
+    let factor_value = U256::from(58);
+    let factor = SymExpr::constant(&mut cx, factor_value);
     let product = SymExpr::binop(&mut cx, SymBinOp::Mul, value.clone(), factor.clone());
     let quotient = SymExpr::binop(&mut cx, SymBinOp::UDiv, product, factor);
-    let identity = SymBoolExpr::eq(&mut cx, quotient, value);
+    let identity = SymBoolExpr::eq(&mut cx, quotient, value.clone());
+    let normalized = normalize_constraints_for_solver(&mut cx, std::slice::from_ref(&identity));
+    let expected =
+        SymBoolExpr::cmp_word_const(&mut cx, SymCmpOp::Ule, &value, U256::MAX / factor_value);
+    assert_eq!(normalized, vec![expected]);
 
-    assert_eq!(
-        normalize_constraints_for_solver(&mut cx, std::slice::from_ref(&identity)),
-        vec![identity]
-    );
+    let failure = identity.clone().not(&mut cx);
+    let normalized_failure =
+        normalize_constraints_for_solver(&mut cx, std::slice::from_ref(&failure));
+    for input in [U256::MAX / factor_value + U256::ONE, U256::MAX] {
+        let model = symbolic_model(&mut cx, [("value", input)]);
+        assert!(!identity.eval_model(&model).unwrap());
+        assert!(normalized.iter().any(|constraint| !constraint.eval_model(&model).unwrap()));
+        assert!(failure.eval_model(&model).unwrap());
+        assert!(normalized_failure.iter().all(|constraint| constraint.eval_model(&model).unwrap()));
+    }
+}
+
+#[test]
+fn constant_mul_div_guard_branches_are_decided_locally_and_cached() {
+    let mut cx = SymCx::new();
+    let value = SymExpr::var(&mut cx, "value");
+    let scale_value = U256::from(1_000_000_000_000_000_000u64);
+    let scale = SymExpr::constant(&mut cx, scale_value);
+    let product = SymExpr::binop(&mut cx, SymBinOp::Mul, value.clone(), scale.clone());
+    let quotient = SymExpr::binop(&mut cx, SymBinOp::UDiv, product, scale);
+    let guard = SymBoolExpr::eq(&mut cx, quotient, value.clone());
+    let failure = guard.clone().not(&mut cx);
+    let fits = SymBoolExpr::cmp_word_const(&mut cx, SymCmpOp::Ule, &value, U256::MAX / scale_value);
+    let wraps = fits.clone().not(&mut cx);
+
+    // No SMT backend is configured: every branch below must be decided by the rewrite.
+    let mut solver = SmtLibSubprocessSolver::new(Ok(Vec::new()), None, 16, false);
+    for (constraints, feasible) in [
+        (vec![guard.clone()], true),
+        (vec![failure.clone()], true),
+        (vec![fits.clone(), guard.clone()], true),
+        (vec![wraps.clone(), failure.clone()], true),
+        (vec![fits, failure], false),
+        (vec![wraps, guard], false),
+    ] {
+        assert_eq!(
+            solver.is_sat_branch(&mut cx, &constraints).unwrap(),
+            feasible,
+            "{constraints:?}"
+        );
+        let cache_hits = solver.stats().sat_cache_hits;
+        assert_eq!(
+            solver.is_sat_branch(&mut cx, &constraints).unwrap(),
+            feasible,
+            "{constraints:?}"
+        );
+        assert_eq!(solver.stats().sat_cache_hits, cache_hits + 1, "{constraints:?}");
+    }
+    assert_eq!(solver.stats().smt_queries, 0);
 }
 
 #[test]
```

### crates/forge/tests/cli/test_cmd/symbolic.rs
```diff
@@ -6484,6 +6484,20 @@ contract OptInTarget {
         return uint256(value);
     }
 
+    function optOut() external {
+        require(fixedCpt[msg.sender] == 0);
+        require(state[msg.sender] == 0 || state[msg.sender] == 2);
+        uint256 oldCredits = credits[msg.sender];
+        uint256 balance = balanceOf(msg.sender);
+        credits[msg.sender] = balance;
+        fixedCpt[msg.sender] = 1e18;
+        state[msg.sender] = 1;
+        int256 creditDiff = -toInt(oldCredits);
+        int256 supplyDiff = toInt(balance);
+        if (creditDiff != 0) rebasingCredits = toUint(toInt(rebasingCredits) + creditDiff);
+        if (supplyDiff != 0) nonRebasingSupply = toUint(toInt(nonRebasingSupply) + supplyDiff);
+    }
+
     function optIn() external {
         uint256 balance = balanceOf(msg.sender);
         require(fixedCpt[msg.sender] > 0 || credits[msg.sender] == 0);
@@ -6526,6 +6540,33 @@ contract FixedPointRoundTripTest {
         assert(target.state(account) == 2);
     }
 
+    function checkFullWidthOptOut(address account) external {
+        vm.assume(target.cpt() >= 1e18);
+        uint256 balance = target.balanceOf(account);
+        vm.prank(account);
+        target.optOut();
+        assert(target.balanceOf(account) == balance);
+        assert(target.fixedCpt(account) == 1e18);
+        assert(target.state(account) == 1);
+    }
+
+    function testOptOutConcreteWitnessAtCreditLimit() external {
+        address account = address(0xB0B);
+        uint256 credits = type(uint256).max / 1e18;
+        uint256 rate = 1e18 + 1;
+        uint256 balance = credits * 1e18 / rate;
+        vm.store(address(target), bytes32(uint256(0)), bytes32(rate));
+        vm.store(address(target), bytes32(uint256(1)), bytes32(credits));
+        vm.store(address(target), bytes32(uint256(2)), bytes32(uint256(0)));
+        vm.store(address(target), keccak256(abi.encode(account, uint256(3))), bytes32(credits));
+        vm.store(address(target), keccak256(abi.encode(account, uint256(4))), bytes32(uint256(0)));
+        vm.store(address(target), keccak256(abi.encode(account, uint256(5))), bytes32(uint256(2)));
+        this.checkFullWidthOptOut(account);
+        assert(target.credits(account) == balance);
+        assert(target.rebasingCredits() == 0);
+        assert(target.nonRebasingSupply() == balance);
+    }
+
     function testOptInConcreteWitnessAboveUint128() external {
         address account = address(0xB0B);
         uint256 balance = uint256(type(uint128).max) + 1;
@@ -6569,6 +6610,12 @@ contract FixedPointRoundTripTest {
         assert(credits * 2 / 1 == balance);
     }
 
+    function checkUncheckedConstantProduct(uint256 value) external pure {
+        unchecked {
+            assert(value * 1e18 / 1e18 == value);
+        }
+    }
+
     function checkWrapping(uint256 balance) external pure {
         require(balance >= 1 << 255);
         unchecked {
@@ -6582,6 +6629,7 @@ contract FixedPointRoundTripTest {
     for (test, signature) in [
         ("checkFullWidthRoundTrip", "checkFullWidthRoundTrip(uint256,uint256)"),
         ("checkFullWidthOptIn", "checkFullWidthOptIn(address)"),
+        ("checkFullWidthOptOut", "checkFullWidthOptOut(address)"),
     ] {
         let output = cmd
             .forge_fuse()
@@ -6603,13 +6651,14 @@ contract FixedPointRoundTripTest {
         assert_eq!(result["symbolic"]["status"], "pass");
     }
     cmd.forge_fuse()
-        .args(["test", "--optimize", "--match-test", "testOptInConcreteWitness"])
+        .args(["test", "--optimize", "--match-test", "testOpt(In|Out)ConcreteWitness"])
         .assert_success();
 
     for (test, signature) in [
         ("checkLowRate", "checkLowRate(uint128)"),
         ("checkWrapping", "checkWrapping(uint256)"),
         ("checkUncheckedRounding", "checkUncheckedRounding(uint256)"),
+        ("checkUncheckedConstantProduct", "checkUncheckedConstantProduct(uint256)"),
     ] {
         let output = cmd
             .forge_fuse()
```
