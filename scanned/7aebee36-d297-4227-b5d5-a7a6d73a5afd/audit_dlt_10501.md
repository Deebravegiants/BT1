# [?] fix: Test expects a nondeterministic error condition.  (#9964)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2026-04-22
Source: https://github.com/dfinity/ic/commit/64a9695c34d073481e7bfc4a94a05aff72671775
Type: security-commit

## Details
fix: Test expects a nondeterministic error condition.  (#9964)

## Patch
### rs/state_manager/tests/state_manager.rs
```diff
@@ -9594,9 +9594,10 @@ fn commit_and_certify_reuses_certification() {
 }
 
 #[test]
-#[should_panic(expected = "failed to wait for hashing thread")]
+#[should_panic]
 // This test fails with the following panic message, but we can't inspect it because is happens in another thread:
 // Committed state @1 with hash CryptoHash(0x4e2d174de5daaeb4622d8f5e426ee09274f7ec4fb01d62fb9a3d36ae50961353) which is different from previously computed or delivered hash CryptoHash(0x2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a2a)
+// We don't expect a specific panic message because it is not deterministic (could happen when sending `Wait` or when awaiting it).
 fn commit_and_certify_panic_on_delivered_fake_certification() {
     state_manager_test(|metrics, sm| {
         // consensus delivers certification for a future height
```
