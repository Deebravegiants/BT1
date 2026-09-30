# [?] fix: guard exchange-rate fee conversion against non-positive centEquiv and overflow (#27167)

## Summary
Severity: Unknown
Chain: Hedera
Component: hiero-ledger/hiero-consensus-node
Published: 2026-09-10
Source: https://github.com/hiero-ledger/hiero-consensus-node/commit/9bcd758823b36a801c97d0fbb46cc37e9bee0a38
Type: security-commit

## Details
fix: guard exchange-rate fee conversion against non-positive centEquiv and overflow (#27167)

Signed-off-by: Ruslan Velkov <ruslan.velkov@limechain.tech>
Signed-off-by: joshmarinacci <joshua@marinacci.org>
Signed-off-by: Josh Marinacci <joshua@marinacci.org>
Co-authored-by: ruslanvelkov-beep <ruslan.velkov@limechain.tech>

## Patch
### hedera-node/hapi-utils/src/main/java/com/hedera/node/app/hapi/utils/fee/FeeConstants.java
```diff
@@ -129,24 +129,37 @@ public static long getTinybarsFromTinyCents(final ExchangeRate exchangeRate, fin
      * Convert tinycents to tinybars, falling back to BigInteger math when the product would overflow.
      *
      * @param amount the amount in tinycents
-     * @param rate the exchange rate
+     * @param rate   the exchange rate
      * @return the amount in tinybars
      */
     public static long tinycentsToTinybars(final long amount, final ExchangeRate rate) {
         final var hbarEquiv = rate.getHbarEquiv();
+        final var centEquiv = rate.getCentEquiv();
+        // A non-positive centEquiv would divide by zero, and a non-positive hbarEquiv would make the fee
+        // free or negative; saturate to Long.MAX_VALUE instead of throwing, so a degenerate rate yields an
+        // unpayable fee rather than halting fee conversion identically on every node.
+        if (centEquiv <= 0 || hbarEquiv <= 0) {
+            return Long.MAX_VALUE;
+        }
         if (CommonUtils.productWouldOverflow(amount, hbarEquiv)) {
             return getTinybarsFromTinyCents(rate, amount);
         }
-        return amount * hbarEquiv / rate.getCentEquiv();
+        return amount * hbarEquiv / centEquiv;
     }
 
+    private static final BigInteger LONG_MAX = BigInteger.valueOf(Long.MAX_VALUE);
+
     private static long getAFromB(final long bAmount, final int aEquiv, final int bEquiv) {
-        final var aMultiplier = BigInteger.valueOf(aEquiv);
-        final var bDivisor = BigInteger.valueOf(bEquiv);
-        return BigInteger.valueOf(bAmount)
-                .multiply(aMultiplier)
-                .divide(bDivisor)
-                .longValueExact();
+        // A degenerate exchange rate would either divide by zero (non-positive divisor) or make the result
+        // free/negative (non-positive multiplier); saturate to Long.MAX_VALUE instead so a malformed rate
+        // yields an unpayable fee and cannot halt fee conversion network-wide.
+        if (aEquiv <= 0 || bEquiv <= 0) {
+            return Long.MAX_VALUE;
+        }
+        final var result =
+                BigInteger.valueOf(bAmount).multiply(BigInteger.valueOf(aEquiv)).divide(BigInteger.valueOf(bEquiv));
+        // longValueExact() throws when the result exceeds the long range; saturate to the maximum instead.
+        return result.compareTo(LONG_MAX) >= 0 ? Long.MAX_VALUE : result.longValue();
     }
 
     /**
```

### hedera-node/hapi-utils/src/test/java/com/hedera/node/app/hapi/utils/fee/FeeConstantsTest.java
```diff
@@ -44,6 +44,49 @@ void tinycentsToTinybarsFallsBackToBigIntegerMathOnOverflow() {
         assertEquals(2_500_000_000_000_000_000L, FeeConstants.tinycentsToTinybars(amount, exchangeRate));
     }
 
+    @Test
+    void getTinybarsFromTinyCentsSaturatesOnNonPositiveCentEquiv() {
+        // A zero centEquiv would divide by zero -> saturate to Long.MAX_VALUE instead of throwing.
+        final var zeroCentRate =
+                ExchangeRate.newBuilder().setHbarEquiv(1).setCentEquiv(0).build();
+        assertEquals(Long.MAX_VALUE, FeeConstants.getTinybarsFromTinyCents(zeroCentRate, 100L));
+        final var negativeCentRate =
+                ExchangeRate.newBuilder().setHbarEquiv(1).setCentEquiv(-100).build();
+        assertEquals(Long.MAX_VALUE, FeeConstants.getTinybarsFromTinyCents(negativeCentRate, 100L));
+    }
+
+    @Test
+    void getTinybarsFromTinyCentsSaturatesOnNonPositiveHbarEquiv() {
+        // A non-positive hbarEquiv would make the fee free or negative; saturate instead.
+        final var zeroHbarRate =
+                ExchangeRate.newBuilder().setHbarEquiv(0).setCentEquiv(100).build();
+        assertEquals(Long.MAX_VALUE, FeeConstants.getTinybarsFromTinyCents(zeroHbarRate, 100L));
+        final var negativeHbarRate =
+                ExchangeRate.newBuilder().setHbarEquiv(-5).setCentEquiv(100).build();
+        assertEquals(Long.MAX_VALUE, FeeConstants.getTinybarsFromTinyCents(negativeHbarRate, 100L));
+    }
+
+    @Test
+    void getTinybarsFromTinyCentsSaturatesInsteadOfOverflowing() {
+        // A valid but extremely skewed rate can exceed the long range; saturate rather than throw.
+        final var skewedRate = ExchangeRate.newBuilder()
+                .setHbarEquiv(Integer.MAX_VALUE)
+                .setCentEquiv(1)
+                .build();
+        assertEquals(Long.MAX_VALUE, FeeConstants.getTinybarsFromTinyCents(skewedRate, Long.MAX_VALUE / 2));
+    }
+
+    @Test
+    void tinycentsToTinybarsSaturatesOnDegenerateRate() {
+        // The same guarantee on the path used by the fee context.
+        final var zeroCentRate =
+                ExchangeRate.newBuilder().setHbarEquiv(1).setCentEquiv(0).build();
+        assertEquals(Long.MAX_VALUE, FeeConstants.tinycentsToTinybars(100L, zeroCentRate));
+        final var zeroHbarRate =
+                ExchangeRate.newBuilder().setHbarEquiv(0).setCentEquiv(100).build();
+        assertEquals(Long.MAX_VALUE, FeeConstants.tinycentsToTinybars(100L, zeroHbarRate));
+    }
+
     @Test
     void getContractFunctionSizeSumsComponents() {
         final var result = ContractFunctionResult.newBuilder()
```

### hedera-node/hedera-app-spi/src/main/java/com/hedera/node/app/spi/fees/Fees.java
```diff
@@ -1,6 +1,7 @@
 // SPDX-License-Identifier: Apache-2.0
 package com.hedera.node.app.spi.fees;
 
+import static com.hedera.node.app.hapi.utils.CommonUtils.clampedAdd;
 import static java.util.Objects.requireNonNull;
 import static org.hiero.hapi.fees.HighVolumePricingCalculator.DEFAULT_HIGH_VOLUME_MULTIPLIER;
 
@@ -97,9 +98,10 @@ public Fees onlyServiceComponent() {
      * @return the total fee. Will be non-negative.
      */
     public long totalFee() {
-        // Safely add the three components together, such that an overflow is detected. In practice this should never
-        // happen, since the maximum number of tinybars is less than Long.MAX_VALUE.
-        return Math.addExact(totalWithoutServiceFee(), serviceFee);
+        // Saturate rather than throw on overflow. In practice a legitimate total is well under Long.MAX_VALUE,
+        // but a saturated component (from a degenerate exchange rate) must clamp the total to Long.MAX_VALUE so
+        // the operation reaches the insufficient-balance outcome instead of raising an ArithmeticException.
+        return clampedAdd(totalWithoutServiceFee(), serviceFee);
     }
 
     /**
@@ -108,7 +110,7 @@ public long totalFee() {
      * @return the total without service fees. Will be non-negative.
      */
     public long totalWithoutServiceFee() {
-        return Math.addExact(nodeFee, networkFee);
+        return clampedAdd(nodeFee, networkFee);
     }
 
     /**
@@ -117,7 +119,7 @@ public long totalWithoutServiceFee() {
      * @return the total without node fees. Will be non-negative.
      */
     public long totalWithoutNodeFee() {
-        return Math.addExact(networkFee, serviceFee);
+        return clampedAdd(networkFee, serviceFee);
     }
 
     /**
```

### hedera-node/hedera-app-spi/src/main/java/com/hedera/node/app/spi/fees/util/FeeUtils.java
```diff
@@ -36,9 +36,16 @@ public static Fees feeResultToFees(FeeResult feeResult, ExchangeRate rate) {
 
     public static long tinycentsToTinybars(final long amount, final ExchangeRate rate) {
         final var hbarEquiv = rate.getHbarEquiv();
+        final var centEquiv = rate.getCentEquiv();
+        // A non-positive centEquiv would divide by zero, and a non-positive hbarEquiv would make the fee
+        // free or negative; saturate to Long.MAX_VALUE instead of throwing, so a degenerate rate yields an
+        // unpayable fee rather than halting fee conversion identically on every node.
+        if (centEquiv <= 0 || hbarEquiv <= 0) {
+            return Long.MAX_VALUE;
+        }
         if (productWouldOverflow(amount, hbarEquiv)) {
             return FeeConstants.getTinybarsFromTinyCents(rate, amount);
         }
-        return amount * hbarEquiv / rate.getCentEquiv();
+        return amount * hbarEquiv / centEquiv;
     }
 }
```

### hedera-node/hedera-app-spi/src/test/java/com/hedera/node/app/spi/fees/FeesTest.java
```diff
@@ -0,0 +1,34 @@
+// SPDX-License-Identifier: Apache-2.0
+package com.hedera.node.app.spi.fees;
+
+import static org.junit.jupiter.api.Assertions.assertEquals;
+
+import org.junit.jupiter.api.Test;
+
+class FeesTest {
+    @Test
+    void totalsAddNormally() {
+        final var fees = new Fees(1, 2, 3);
+        assertEquals(6, fees.totalFee());
+        assertEquals(3, fees.totalWithoutServiceFee());
+        assertEquals(5, fees.totalWithoutNodeFee());
+    }
+
+    @Test
+    void totalFeeSaturatesInsteadOfThrowing() {
+        // Previously Math.addExact threw on overflow; a saturated (degenerate-rate) component must instead
+        // clamp the total to Long.MAX_VALUE so the operation reaches the insufficient-balance outcome.
+        final var maxed = new Fees(Long.MAX_VALUE, Long.MAX_VALUE, Long.MAX_VALUE);
+        assertEquals(Long.MAX_VALUE, maxed.totalFee());
+        assertEquals(Long.MAX_VALUE, maxed.totalWithoutServiceFee());
+        assertEquals(Long.MAX_VALUE, maxed.totalWithoutNodeFee());
+    }
+
+    @Test
+    void totalFeeSaturatesWithSingleMaxComponent() {
+        // Even one saturated component plus another positive one must clamp rather than throw.
+        assertEquals(Long.MAX_VALUE, new Fees(Long.MAX_VALUE, 1, 0).totalFee());
+        assertEquals(Long.MAX_VALUE, new Fees(0, Long.MAX_VALUE, 1).totalFee());
+        assertEquals(Long.MAX_VALUE, new Fees(1, 0, Long.MAX_VALUE).totalFee());
+    }
+}
```

### hedera-node/hedera-app-spi/src/test/java/com/hedera/node/app/spi/fees/util/FeeUtilsTest.java
```diff
@@ -53,4 +53,45 @@ void tinycentsToTinybars_regularCalculation() {
         long result = FeeUtils.tinycentsToTinybars(10, rate);
         assertEquals(25, result); // (10 * 5) / 2 = 25
     }
+
+    @Test
+    void tinycentsToTinybars_saturatesOnNonPositiveCentEquiv() {
+        ExchangeRate rate = mock(ExchangeRate.class);
+        when(rate.getHbarEquiv()).thenReturn(1);
+        when(rate.getCentEquiv()).thenReturn(0);
+
+        // A zero centEquiv would divide by zero; the conversion saturates instead of throwing.
+        assertEquals(Long.MAX_VALUE, FeeUtils.tinycentsToTinybars(100L, rate));
+    }
+
+    @Test
+    void tinycentsToTinybars_saturatesOnNonPositiveHbarEquiv() {
+        ExchangeRate zeroHbarRate = mock(ExchangeRate.class);
+        when(zeroHbarRate.getHbarEquiv()).thenReturn(0);
+        when(zeroHbarRate.getCentEquiv()).thenReturn(120);
+        // A zero hbarEquiv would make the fee free; saturate so a degenerate rate is unpayable, not free.
+        assertEquals(Long.MAX_VALUE, FeeUtils.tinycentsToTinybars(100L, zeroHbarRate));
+
+        ExchangeRate negativeHbarRate = mock(ExchangeRate.class);
+        when(negativeHbarRate.getHbarEquiv()).thenReturn(-1);
+        when(negativeHbarRate.getCentEquiv()).thenReturn(120);
+        assertEquals(Long.MAX_VALUE, FeeUtils.tinycentsToTinybars(100L, negativeHbarRate));
+    }
+
+    @Test
+    void feeResultToFeesTotalSaturatesOnDegenerateRate() {
+        ExchangeRate rate = mock(ExchangeRate.class);
+        when(rate.getHbarEquiv()).thenReturn(1);
+        when(rate.getCentEquiv()).thenReturn(0);
+
+        // End-to-end: each component conversion saturates on the degenerate rate, and the saturating total
+        // clamps to Long.MAX_VALUE instead of overflowing Math.addExact in Fees.totalFee().
+        FeeResult feeResult = new FeeResult(30, 10, 2);
+        Fees fees = FeeUtils.feeResultToFees(feeResult, rate);
+
+        assertEquals(Long.MAX_VALUE, fees.nodeFee());
+        assertEquals(Long.MAX_VALUE, fees.networkFee());
+        assertEquals(Long.MAX_VALUE, fees.serviceFee());
+        assertEquals(Long.MAX_VALUE, fees.totalFee());
+    }
 }
```

### hedera-node/hedera-app/src/main/java/com/hedera/node/app/fees/ExchangeRateManager.java
```diff
@@ -53,6 +53,7 @@ public final class ExchangeRateManager {
     private static final Logger log = LogManager.getLogger(ExchangeRateManager.class);
 
     private static final BigInteger ONE_HUNDRED = BigInteger.valueOf(100);
+    private static final BigInteger LONG_MAX = BigInteger.valueOf(Long.MAX_VALUE);
 
     private final ConfigProvider configProvider;
 
@@ -113,6 +114,14 @@ private void internalUpdate(@NonNull final Bytes bytes, @Nullable AccountID paye
             throw new HandleException(ResponseCodeEnum.INVALID_EXCHANGE_RATE_FILE);
         }
 
+        // Reject degenerate rates: a non-positive hbarEquiv/centEquiv would make fee conversion divide by
+        // zero (see getAFromB) or yield a nonsensical price, so such a rate must never become the live rate.
+        final var current = proposedRates.currentRateOrThrow();
+        final var next = proposedRates.nextRateOrThrow();
+        if (current.hbarEquiv() <= 0 || current.centEquiv() <= 0 || next.hbarEquiv() <= 0 || next.centEquiv() <= 0) {
+            throw new HandleException(ResponseCodeEnum.INVALID_EXCHANGE_RATE_FILE);
+        }
+
         // Check bounds
         final var ratesConfig = configProvider.getConfiguration().getConfigData(RatesConfig.class);
         final var accountsConfig = configProvider.getConfiguration().getConfigData(AccountsConfig.class);
@@ -266,11 +275,15 @@ public long getTinybarsFromTinycents(final long amount, @NonNull final Instant c
     }
 
     private static long getAFromB(final long bAmount, final int aEquiv, final int bEquiv) {
-        final var aMultiplier = BigInteger.valueOf(aEquiv);
-        final var bDivisor = BigInteger.valueOf(bEquiv);
-        return BigInteger.valueOf(bAmount)
-                .multiply(aMultiplier)
-                .divide(bDivisor)
-                .longValueExact();
+        // A degenerate exchange rate would either divide by zero (non-positive divisor) or make the result
+        // free/negative (non-positive multiplier); saturate to Long.MAX_VALUE instead so a malformed rate
+        // yields an unpayable fee and cannot halt fee conversion network-wide.
+        if (aEquiv <= 0 || bEquiv <= 0) {
+            return Long.MAX_VALUE;
+        }
+        final var result =
+                BigInteger.valueOf(bAmount).multiply(BigInteger.valueOf(aEquiv)).divide(BigInteger.valueOf(bEquiv));
+        // longValueExact() throws when the result exceeds the long range; saturate to the maximum instead.
+        return result.compareTo(LONG_MAX) >= 0 ? Long.MAX_VALUE : result.longValue();
     }
 }
```

### hedera-node/hedera-app/src/test/java/com/hedera/node/app/fees/ExchangeRateManagerTest.java
```diff
@@ -91,6 +91,40 @@ void updateWithInvalidExchangeRateBytes() {
                 .has(responseCode(ResponseCodeEnum.INVALID_EXCHANGE_RATE_FILE));
     }
 
+    @Test
+    void updateRejectsNonPositiveCentEquiv() {
+        // A super-user bypasses the intraday-change limit, but must still not be able to install a rate whose
+        // centEquiv is zero -- that would make fee conversion divide by zero on every node.
+        final var zeroCentRate =
+                ExchangeRate.newBuilder().hbarEquiv(1).centEquiv(0).expirationTime(expirationTime);
+        final var zeroRates = ExchangeRateSet.newBuilder()
+                .currentRate(zeroCentRate)
+                .nextRate(zeroCentRate)
+                .build();
+        final var zeroRateBytes = ExchangeRateSet.PROTOBUF.toBytes(zeroRates);
+        final var superUser = AccountID.newBuilder().accountNum(50L).build();
+
+        assertThatThrownBy(() -> subject.update(zeroRateBytes, superUser))
+                .isInstanceOf(HandleException.class)
+                .has(responseCode(ResponseCodeEnum.INVALID_EXCHANGE_RATE_FILE));
+    }
+
+    @Test
+    void getAFromBSaturatesOnNonPositiveRateComponents() throws Exception {
+        // internalUpdate() is the single writer of the active rate and rejects degenerate rates, so the
+        // private converter can never see one through the public API. This exercises the defense-in-depth
+        // guard directly: a non-positive multiplier (aEquiv) or divisor (bEquiv) must saturate to
+        // Long.MAX_VALUE rather than divide by zero or yield a free/negative fee.
+        final var getAFromB =
+                ExchangeRateManager.class.getDeclaredMethod("getAFromB", long.class, int.class, int.class);
+        getAFromB.setAccessible(true);
+
+        assertEquals(Long.MAX_VALUE, (long) getAFromB.invoke(null, 100L, 0, centEquiv)); // aEquiv == 0
+        assertEquals(Long.MAX_VALUE, (long) getAFromB.invoke(null, 100L, -1, centEquiv)); // aEquiv < 0
+        assertEquals(Long.MAX_VALUE, (long) getAFromB.invoke(null, 100L, hbarEquiv, 0)); // bEquiv == 0
+        assertEquals(200L, (long) getAFromB.invoke(null, 100L, 100, 50)); // normal: 100 * 100 / 50
+    }
+
     @ParameterizedTest
     @MethodSource("provideConsensusTimesForActiveRate")
     void activeRateWorksAsExpected(Instant consensusTime, ExchangeRate expectedExchangeRate) {
```
