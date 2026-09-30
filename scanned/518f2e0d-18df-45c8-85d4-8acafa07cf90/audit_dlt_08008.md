# [?] fix: guard intermediate overflow in throttle LCM capacity check (#26711)

## Summary
Severity: Unknown
Chain: Hedera
Component: hiero-ledger/hiero-consensus-node
Published: 2026-08-06
Source: https://github.com/hiero-ledger/hiero-consensus-node/commit/931b636f3324edcaabb902265e03441b986f41a3
Type: security-commit

## Details
fix: guard intermediate overflow in throttle LCM capacity check (#26711)

Signed-off-by: Alex Kehayov <aleks.kehayov@limechain.tech>

## Patch
### hedera-node/hedera-app/src/main/java/com/hedera/node/app/throttle/ThrottleParser.java
```diff
@@ -138,7 +138,8 @@ private void validateLeastCommonMultipleDoesNotOverflow(ThrottleDefinitions thro
         try {
             for (var bucket : throttleDefinitions.throttleBuckets()) {
                 var lcm = leastCommonMultiple(bucket.throttleGroups());
-                final var unscaledCapacity = lcm * NTPS_PER_MTPS * CAPACITY_UNITS_PER_NANO_TXN / 1_000;
+                final var unscaledCapacity =
+                        Math.multiplyExact(Math.multiplyExact(lcm, NTPS_PER_MTPS), CAPACITY_UNITS_PER_NANO_TXN) / 1_000;
                 if (productWouldOverflow(unscaledCapacity, bucket.burstPeriodMs())) {
                     throw new ArithmeticException();
                 }
```

### hedera-node/hedera-app/src/test/java/com/hedera/node/app/throttle/ThrottleParserTest.java
```diff
@@ -147,4 +147,29 @@ void parseWithLcmOverflow_throwsThrottleGroupLcmOverflow() {
                 .isInstanceOf(HandleException.class)
                 .has(responseCode(THROTTLE_GROUP_LCM_OVERFLOW));
     }
+
+    @Test
+    void parseWithScaledCapacityOverflow_throwsThrottleGroupLcmOverflow() {
+        // Coprime rates whose LCM (~1e12) fits in a long, so the pairwise LCM guard passes; but the
+        // scaled capacity (lcm * NTPS_PER_MTPS * CAPACITY_UNITS_PER_NANO_TXN) overflows a long.
+        final var group1 = ThrottleGroup.newBuilder()
+                .operations(List.of(HederaFunctionality.CRYPTO_CREATE))
+                .milliOpsPerSec(1_000_000)
+                .build();
+        final var group2 = ThrottleGroup.newBuilder()
+                .operations(List.of(HederaFunctionality.CRYPTO_TRANSFER))
+                .milliOpsPerSec(1_000_001)
+                .build();
+        final var bucket = ThrottleBucket.newBuilder()
+                .name("bucket")
+                .burstPeriodMs(100L)
+                .throttleGroups(group1, group2)
+                .build();
+        final var bytes = ThrottleDefinitions.PROTOBUF.toBytes(
+                ThrottleDefinitions.newBuilder().throttleBuckets(bucket).build());
+
+        assertThatThrownBy(() -> subject.parse(bytes))
+                .isInstanceOf(HandleException.class)
+                .has(responseCode(THROTTLE_GROUP_LCM_OVERFLOW));
+    }
 }
```
