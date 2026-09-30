# [?] fix(forge): avoid panic on internal decoding of linked tests (#10333)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2025-04-18
Source: https://github.com/foundry-rs/foundry/commit/f76309dad7dddc0917755d3f3d17e1ad9d02c6b8
Type: security-commit

## Details
fix(forge): avoid panic on internal decoding of linked tests (#10333)

Failing tests related to etherscan sepolia migration

## Patch
### crates/evm/traces/src/debug/mod.rs
```diff
@@ -200,6 +200,13 @@ impl<'a> DebugStepsWalker<'a> {
 fn parse_function_from_loc(source: &SourceData, loc: &SourceElement) -> Option<String> {
     let start = loc.offset() as usize;
     let end = start + loc.length() as usize;
+    let src_len = source.source.len();
+
+    // Handle special case of preprocessed test sources.
+    if start > src_len || end > src_len {
+        return None;
+    }
+
     let source_part = &source.source[start..end];
     if !source_part.starts_with("function") {
         return None;
```

### crates/forge/tests/cli/test_optimizer.rs
```diff
@@ -1345,3 +1345,69 @@ Compiling 20 files with [..]
 
 "#]]);
 });
+
+// Test preprocessed contracts with decode internal fns.
+forgetest_init!(preprocess_contract_with_decode_internal, |prj, cmd| {
+    prj.update_config(|config| {
+        config.dynamic_test_linking = true;
+    });
+
+    prj.add_test(
+        "Counter.t.sol",
+        r#"
+import {Test} from "forge-std/Test.sol";
+import {Counter} from "../src/Counter.sol";
+
+contract CounterTest is Test {
+    Counter public counter;
+
+    function setUp() public {
+        create_counter(0);
+    }
+
+    function test_Increment() public {
+        create_counter(0);
+        counter.increment();
+        assertEq(counter.number(), 1);
+    }
+
+    function create_counter(uint256 number) internal {
+        counter = new Counter();
+        counter.setNumber(number);
+    }
+}
+    "#,
+    )
+    .unwrap();
+
+    cmd.args(["test", "--decode-internal", "-vvvv"]).assert_success().stdout_eq(str![[r#"
+[COMPILING_FILES] with [SOLC_VERSION]
+[SOLC_VERSION] [ELAPSED]
+Compiler run successful!
+
+Ran 1 test for test/Counter.t.sol:CounterTest
+[PASS] test_Increment() ([GAS])
+Traces:
+  [..] CounterTest::test_Increment()
+    ├─ [0] VM::deployCode("src/Counter.sol:Counter")
+    │   ├─ [96345] → new Counter@0x2e234DAe75C793f67A35089C9d99245E1C58470b
+    │   │   └─ ← [Return] 481 bytes of code
+    │   └─ ← [Return] Counter: [0x2e234DAe75C793f67A35089C9d99245E1C58470b]
+    ├─ [..] Counter::setNumber(0)
+    │   └─ ← [Stop]
+    ├─ [..] Counter::increment()
+    │   └─ ← [Stop]
+    ├─ [..] Counter::number() [staticcall]
+    │   └─ ← [Return] 1
+    ├─ [..] StdAssertions::assertEq(1, 1)
+    │   ├─ [0] VM::assertEq(1, 1) [staticcall]
+    │   │   └─ ← [Return]
+    │   └─ ← 
+    └─ ← [Stop]
+
+Suite result: ok. 1 passed; 0 failed; 0 skipped; [ELAPSED]
+
+Ran 1 test suite [ELAPSED]: 1 tests passed, 0 failed, 0 skipped (1 total tests)
+
+"#]]);
+});
```
