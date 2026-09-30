# [?] fix(invariant): call override strategy panic (#7469)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2024-03-22
Source: https://github.com/foundry-rs/foundry/commit/9d2125b013cbcb61dce2546379a79a4d99ba2f78
Type: security-commit

## Details
fix(invariant): call override strategy panic (#7469)

* fix(invariant): override call strat panic

* Add test

## Patch
### crates/evm/fuzz/src/strategies/invariants.rs
```diff
@@ -25,7 +25,17 @@ pub fn override_call_strat(
     .prop_flat_map(move |target_address| {
         let fuzz_state = fuzz_state.clone();
         let calldata_fuzz_config = calldata_fuzz_config.clone();
-        let (_, abi, functions) = &contracts.lock()[&target_address];
+
+        let contracts = &contracts.lock();
+        let (_, abi, functions) = contracts.get(&target_address).unwrap_or({
+            // Choose a random contract if target selected by lazy strategy is not in fuzz run
+            // identified contracts. This can happen when contract is created in `setUp` call
+            // but is not included in targetContracts.
+            let rand_index = rand::thread_rng().gen_range(0..contracts.iter().len());
+            let (_, contract_specs) = contracts.iter().nth(rand_index).unwrap();
+            contract_specs
+        });
+
         let func = select_random_function(abi, functions);
         func.prop_flat_map(move |func| {
             fuzz_contract_with_calldata(&fuzz_state, &calldata_fuzz_config, target_address, func)
```

### crates/forge/tests/it/invariant.rs
```diff
@@ -153,6 +153,7 @@ async fn test_invariant() {
 async fn test_invariant_override() {
     let filter = Filter::new(".*", ".*", ".*fuzz/invariant/common/InvariantReentrancy.t.sol");
     let mut runner = TEST_DATA_DEFAULT.runner();
+    runner.test_options.invariant.fail_on_revert = false;
     runner.test_options.invariant.call_override = true;
     let results = runner.test_collect(&filter);
 
```

### testdata/default/fuzz/invariant/common/InvariantReentrancy.t.sol
```diff
@@ -5,7 +5,9 @@ import "ds-test/test.sol";
 
 contract Malicious {
     function world() public {
-        // Does not matter, since it will get overridden.
+        // add code so contract is accounted as valid sender
+        // see https://github.com/foundry-rs/foundry/issues/4245
+        payable(msg.sender).transfer(1);
     }
 }
 
@@ -39,6 +41,14 @@ contract InvariantReentrancy is DSTest {
         vuln = new Vulnerable(address(mal));
     }
 
+    // do not include `mal` in identified contracts
+    // see https://github.com/foundry-rs/foundry/issues/4245
+    function targetContracts() public view returns (address[] memory) {
+        address[] memory targets = new address[](1);
+        targets[0] = address(vuln);
+        return targets;
+    }
+
     function invariantNotStolen() public {
         require(vuln.stolen() == false, "stolen");
     }
```
