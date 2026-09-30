# [?] fix: overflow in randomUint (#8239)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2024-06-24
Source: https://github.com/foundry-rs/foundry/commit/abd8d55c36e4b717de844b43395b22150a813a9e
Type: security-commit

## Details
fix: overflow in randomUint (#8239)

## Patch
### crates/cheatcodes/src/utils.rs
```diff
@@ -158,11 +158,12 @@ impl Cheatcode for randomUint_0Call {
 
 impl Cheatcode for randomUint_1Call {
     fn apply(&self, _state: &mut Cheatcodes) -> Result {
-        let Self { min, max } = self;
+        let Self { min, max } = *self;
+        ensure!(min <= max, "min must be less than or equal to max");
         // Generate random between range min..=max
         let mut rng = rand::thread_rng();
-        let range = *max - *min + U256::from(1);
-        let random_number = rng.gen::<U256>() % range + *min;
+        let range = max - min + U256::from(1);
+        let random_number = rng.gen::<U256>() % range + min;
         Ok(random_number.abi_encode())
     }
 }
```

### testdata/default/cheats/RandomUint.t.sol
```diff
@@ -15,9 +15,7 @@ contract RandomUint is DSTest {
     }
 
     function testRandomUint(uint256 min, uint256 max) public {
-        if (min > max) {
-            (min, max) = (max, min);
-        }
+        vm.assume(max >= min);
         uint256 rand = vm.randomUint(min, max);
         assertTrue(rand >= min, "rand >= min");
         assertTrue(rand <= max, "rand <= max");
```
