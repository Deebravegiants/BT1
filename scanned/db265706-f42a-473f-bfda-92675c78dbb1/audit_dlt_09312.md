# [?] fix(`forge`): avoid panic when empty fuzz selectors in invariants (#9076)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2024-10-09
Source: https://github.com/foundry-rs/foundry/commit/d847e0f09a95ef6ff8463521b98136e74dac37da
Type: security-commit

## Details
fix(`forge`): avoid panic when empty fuzz selectors in invariants (#9076)

## Patch
### crates/evm/evm/src/executors/invariant/mod.rs
```diff
@@ -742,9 +742,6 @@ impl<'a> InvariantExecutor<'a> {
     ) -> Result<()> {
         for (address, (identifier, _)) in self.setup_contracts.iter() {
             if let Some(selectors) = self.artifact_filters.targeted.get(identifier) {
-                if selectors.is_empty() {
-                    continue;
-                }
                 self.add_address_with_functions(*address, selectors, false, targeted_contracts)?;
             }
         }
@@ -774,6 +771,11 @@ impl<'a> InvariantExecutor<'a> {
         should_exclude: bool,
         targeted_contracts: &mut TargetedContracts,
     ) -> eyre::Result<()> {
+        // Do not add address in target contracts if no function selected.
+        if selectors.is_empty() {
+            return Ok(())
+        }
+
         let contract = match targeted_contracts.entry(address) {
             Entry::Occupied(entry) => entry.into_mut(),
             Entry::Vacant(entry) => {
```

### crates/forge/tests/it/invariant.rs
```diff
@@ -823,3 +823,35 @@ contract BalanceAssumeTest is Test {
 ...
 "#]]);
 });
+
+// Test proper message displayed if `targetSelector`/`excludeSelector` called with empty selectors.
+// <https://github.com/foundry-rs/foundry/issues/9066>
+forgetest_init!(should_not_panic_if_no_selectors, |prj, cmd| {
+    prj.add_test(
+        "NoSelectorTest.t.sol",
+        r#"
+import {Test} from "forge-std/Test.sol";
+
+contract TestHandler is Test {}
+
+contract NoSelectorTest is Test {
+    bytes4[] selectors;
+
+    function setUp() public {
+        TestHandler handler = new TestHandler();
+        targetSelector(FuzzSelector({addr: address(handler), selectors: selectors}));
+        excludeSelector(FuzzSelector({addr: address(handler), selectors: selectors}));
+    }
+
+    function invariant_panic() public {}
+}
+     "#,
+    )
+    .unwrap();
+
+    cmd.args(["test", "--mt", "invariant_panic"]).assert_failure().stdout_eq(str![[r#"
+...
+[FAIL: failed to set up invariant testing environment: No contracts to fuzz.] invariant_panic() (runs: 0, calls: 0, reverts: 0)
+...
+"#]]);
+});
```
