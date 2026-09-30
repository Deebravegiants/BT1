# [?] fix: test_promise_results panic message (#10727)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2024-03-08
Source: https://github.com/near/nearcore/commit/dfda6d2e82285bd9a1b11da3ab54aeb4bc7e4810
Type: security-commit

## Details
fix: test_promise_results panic message (#10727)

The panic message for this assert doesn't match the behavior. See also:


https://github.com/near/nearcore/blob/8e0bdf35153bb830521788451a57585ca6263573/runtime/near-vm-runner/src/logic/logic.rs#L2225-L2249

## Patch
### runtime/near-vm-runner/src/logic/tests/promises.rs
```diff
@@ -25,7 +25,7 @@ fn test_promise_results() {
     assert_eq!(logic.promise_results_count(), Ok(3), "Total count of registers must be 3");
     assert_eq!(logic.promise_result(0, 0), Ok(1), "Must return code 1 on success");
     assert_eq!(logic.promise_result(1, 0), Ok(2), "Failed promise must return code 2");
-    assert_eq!(logic.promise_result(2, 0), Ok(0), "Pending promise must return 3");
+    assert_eq!(logic.promise_result(2, 0), Ok(0), "Pending promise must return 0");
 
     // Only promise with result should write data into register
     logic.assert_read_register(b"test", 0);
```
