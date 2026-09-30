# [?] fix: 11507 Temporary disabled test to prevent non-deterministic failures. (#11929)

## Summary
Severity: Unknown
Chain: Hedera
Component: hiero-ledger/hiero-consensus-node
Published: 2024-03-06
Source: https://github.com/hiero-ledger/hiero-consensus-node/commit/a8e1470997879eb1c394ba56b04fb4ea3645a2cf
Type: security-commit

## Details
fix: 11507 Temporary disabled test to prevent non-deterministic failures. (#11929)

Signed-off-by: Ivan Malygin <ivan@swirldslabs.com>

## Patch
### platform-sdk/swirlds-merkle/src/test/java/com/swirlds/virtual/merkle/reconnect/VirtualMapLargeReconnectTest.java
```diff
@@ -62,6 +62,8 @@ void largeTeacherLargerLearnerPermutations(int teacherStart, int teacherEnd, int
     @Tags({@Tag("VirtualMerkle"), @Tag("Reconnect"), @Tag("VMAP-005"), @Tag("VMAP-006")})
     @Tag(TIME_CONSUMING)
     @DisplayName("Reconnect aborts 3 times before success")
+    // FUTURE WORK: https://github.com/hashgraph/hedera-services/issues/11507
+    @Disabled
     void multipleAbortedReconnectsCanSucceed(int teacherStart, int teacherEnd, int learnerStart, int learnerEnd) {
         for (int i = teacherStart; i < teacherEnd; i++) {
             teacherMap.put(new TestKey(i), new TestValue(i));
```
