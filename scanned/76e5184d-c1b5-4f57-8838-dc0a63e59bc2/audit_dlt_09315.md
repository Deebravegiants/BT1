# [?] fix(cheatcodes): overflow in randomNumber w/range (#8361)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2024-07-04
Source: https://github.com/foundry-rs/foundry/commit/56dbd20c7179570c53b6c17ff34daa7273a4ddae
Type: security-commit

## Details
fix(cheatcodes): overflow in randomNumber w/range (#8361)

## Patch
### crates/cheatcodes/src/utils.rs
```diff
@@ -162,8 +162,13 @@ impl Cheatcode for randomUint_1Call {
         ensure!(min <= max, "min must be less than or equal to max");
         // Generate random between range min..=max
         let mut rng = rand::thread_rng();
-        let range = max - min + U256::from(1);
-        let random_number = rng.gen::<U256>() % range + min;
+        let exclusive_modulo = max - min;
+        let mut random_number = rng.gen::<U256>();
+        if exclusive_modulo != U256::MAX {
+            let inclusive_modulo = exclusive_modulo + U256::from(1);
+            random_number %= inclusive_modulo;
+        }
+        random_number += min;
         Ok(random_number.abi_encode())
     }
 }
```

### testdata/default/cheats/RandomUint.t.sol
```diff
@@ -7,27 +7,27 @@ import "cheats/Vm.sol";
 contract RandomUint is DSTest {
     Vm constant vm = Vm(HEVM_ADDRESS);
 
-    // All tests use `>=` and `<=` to verify that ranges are inclusive and that
-    // a value of zero may be generated.
     function testRandomUint() public {
-        uint256 rand = vm.randomUint();
-        assertTrue(rand >= 0);
+        vm.randomUint();
     }
 
-    function testRandomUint(uint256 min, uint256 max) public {
-        vm.assume(max >= min);
-        uint256 rand = vm.randomUint(min, max);
-        assertTrue(rand >= min, "rand >= min");
-        assertTrue(rand <= max, "rand <= max");
+    function testRandomUintRangeOverflow() public {
+        vm.randomUint(0, uint256(int256(-1)));
     }
 
-    function testRandomUint(uint256 val) public {
+    function testRandomUintSame(uint256 val) public {
         uint256 rand = vm.randomUint(val, val);
         assertTrue(rand == val);
     }
 
+    function testRandomUintRange(uint256 min, uint256 max) public {
+        vm.assume(max >= min);
+        uint256 rand = vm.randomUint(min, max);
+        assertTrue(rand >= min, "rand >= min");
+        assertTrue(rand <= max, "rand <= max");
+    }
+
     function testRandomAddress() public {
-        address rand = vm.randomAddress();
-        assertTrue(rand >= address(0));
+        vm.randomAddress();
     }
 }
```
