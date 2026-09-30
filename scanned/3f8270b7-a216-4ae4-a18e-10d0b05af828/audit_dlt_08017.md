# [?] fix: race condition in wiring unit test (#10525)

## Summary
Severity: Unknown
Chain: Hedera
Component: hiero-ledger/hiero-consensus-node
Published: 2023-12-15
Source: https://github.com/hiero-ledger/hiero-consensus-node/commit/44bba9cb3899f93e9e664a47f81c1edf9512eff2
Type: security-commit

## Details
fix: race condition in wiring unit test (#10525)

Signed-off-by: Cody Littley <cody@swirldslabs.com>

## Patch
### platform-sdk/swirlds-common/src/test/java/com/swirlds/common/wiring/schedulers/SequentialTaskSchedulerTests.java
```diff
@@ -1819,11 +1819,14 @@ void squelchNullValuesInWiresTest(final String typeString) {
             expectedCountD = hash32(expectedCountD, i);
         }
 
+        assertEventuallyEquals(
+                expectedCountA, countA::get, Duration.ofSeconds(1), "Wire sum did not match expected sum");
+        assertEventuallyEquals(
+                expectedCountB, countB::get, Duration.ofSeconds(1), "Wire sum did not match expected sum");
+        assertEventuallyEquals(
+                expectedCountC, countC::get, Duration.ofSeconds(1), "Wire sum did not match expected sum");
         assertEventuallyEquals(
                 expectedCountD, countD::get, Duration.ofSeconds(1), "Wire sum did not match expected sum");
-        assertEquals(expectedCountA, countA.get());
-        assertEquals(expectedCountB, countB.get());
-        assertEquals(expectedCountC, countC.get());
 
         model.stop();
     }
```
