# [?] Fix consensus vulnerability regarding excessively large 1559 fee fields (#2338)

## Summary
Severity: Unknown
Chain: Ethereum
Component: hyperledger/besu
Published: 2021-05-28
Source: https://github.com/besu-eth/besu/commit/68510e500bd37f9d7c2b33479d883ed07a9a72a0
Type: security-commit

## Details
Fix consensus vulnerability regarding excessively large 1559 fee fields (#2338)

based on:
https://github.com/ethereum/pm/issues/321#issuecomment-850230251

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

## Patch
### ethereum/core/src/main/java/org/hyperledger/besu/ethereum/core/Difficulty.java
```diff
@@ -69,6 +69,11 @@ public static Difficulty fromHexString(final String str) {
 
   @Override
   public Number getValue() {
+    return getAsBigInteger();
+  }
+
+  @Override
+  public BigInteger getAsBigInteger() {
     return toBigInteger();
   }
 
```

### ethereum/core/src/main/java/org/hyperledger/besu/ethereum/core/Transaction.java
```diff
@@ -536,10 +536,8 @@ public Wei getUpfrontGasCost() {
    * @return the up-front cost for the gas the transaction can use.
    */
   public Wei getUpfrontGasCost(final Wei gasPrice) {
-    if (gasPrice == null || gasPrice.isZero()) {
-      return Wei.ZERO;
-    }
-    return Wei.of(getGasLimit()).multiply(gasPrice);
+    return Wei.of(getGasLimit())
+        .multiply(Wei.of(getMaxFeePerGas().orElse(gasPrice).getAsBigInteger()));
   }
 
   /**
```

### ethereum/core/src/main/java/org/hyperledger/besu/ethereum/core/Wei.java
```diff
@@ -75,6 +75,11 @@ public static Wei fromEth(final long eth) {
 
   @Override
   public Number getValue() {
+    return getAsBigInteger();
+  }
+
+  @Override
+  public BigInteger getAsBigInteger() {
     return toBigInteger();
   }
 
```

### ethereum/core/src/main/java/org/hyperledger/besu/ethereum/core/encoding/TransactionDecoder.java
```diff
@@ -174,8 +174,8 @@ static Transaction decodeEIP1559(final RLPInput input) {
             .type(TransactionType.EIP1559)
             .chainId(chainId)
             .nonce(input.readLongScalar())
-            .maxPriorityFeePerGas(Wei.wrap(input.readBytes()))
-            .maxFeePerGas(Wei.wrap(input.readBytes()))
+            .maxPriorityFeePerGas(Wei.of(input.readUInt256Scalar()))
+            .maxFeePerGas(Wei.of(input.readUInt256Scalar()))
             .gasLimit(input.readLongScalar())
             .to(input.readBytes(v -> v.size() == 0 ? null : Address.wrap(v)))
             .value(Wei.of(input.readUInt256Scalar()))
```

### ethereum/core/src/main/java/org/hyperledger/besu/ethereum/mainnet/MainnetTransactionValidator.java
```diff
@@ -121,7 +121,7 @@ public ValidationResult<TransactionInvalidReason> validate(
           TransactionInvalidReason.INVALID_TRANSACTION_FORMAT,
           String.format(
               "Transaction type %s is invalid, accepted transaction types are %s",
-              transactionType, acceptedTransactionTypes.toString()));
+              transactionType, acceptedTransactionTypes));
     }
 
     if (baseFee.isPresent()) {
@@ -131,6 +131,19 @@ public ValidationResult<TransactionInvalidReason> validate(
             TransactionInvalidReason.INVALID_TRANSACTION_FORMAT,
             "gasPrice is less than the current BaseFee");
       }
+
+      // assert transaction.max_fee_per_gas >= transaction.max_priority_fee_per_gas
+      if (transaction.getType().supports1559FeeMarket()
+          && transaction
+                  .getMaxPriorityFeePerGas()
+                  .get()
+                  .getAsBigInteger()
+                  .compareTo(transaction.getMaxFeePerGas().get().getAsBigInteger())
+              > 0) {
+        return ValidationResult.invalid(
+            TransactionInvalidReason.INVALID_TRANSACTION_FORMAT,
+            "max priority fee per gas cannot be greater than max fee per gas");
+      }
     }
 
     final Gas intrinsicGasCost =
```

### ethereum/core/src/test/java/org/hyperledger/besu/ethereum/core/encoding/TransactionDecoderTest.java
```diff
@@ -15,12 +15,14 @@
 package org.hyperledger.besu.ethereum.core.encoding;
 
 import static org.assertj.core.api.Assertions.assertThat;
+import static org.assertj.core.api.Assertions.assertThatThrownBy;
 
 import org.hyperledger.besu.config.GoQuorumOptions;
 import org.hyperledger.besu.ethereum.core.Address;
 import org.hyperledger.besu.ethereum.core.Transaction;
 import org.hyperledger.besu.ethereum.core.Wei;
 import org.hyperledger.besu.ethereum.rlp.RLP;
+import org.hyperledger.besu.ethereum.rlp.RLPException;
 import org.hyperledger.besu.ethereum.rlp.RLPInput;
 
 import java.math.BigInteger;
@@ -69,4 +71,13 @@ public void decodeEIP1559NominalCase() {
     assertThat(transaction.getMaxPriorityFeePerGas()).hasValue(Wei.of(2L));
     assertThat(transaction.getMaxFeePerGas()).hasValue(Wei.of(new BigInteger("5000000000", 10)));
   }
+
+  @Test
+  public void doesNotDecodeEIP1559WithLargeMaxFeePerGasOrLargeMaxPriorityFeePerGas() {
+    final String txWithBigFees =
+        "0x02f84e0101a1648a5f8b2dcad5ea5ba6b720ff069c1d87c21a4a6a5b3766b39e2c2792367bb066a1ffa5ffaf5b0560d3a9fb186c2ede2ae6751bc0b4fef9107cf36389630b6196a38805800180c0010203";
+    assertThatThrownBy(
+            () -> TransactionDecoder.decodeOpaqueBytes(Bytes.fromHexString(txWithBigFees)))
+        .isInstanceOf(RLPException.class);
+  }
 }
```

### ethereum/core/src/test/java/org/hyperledger/besu/ethereum/mainnet/MainnetTransactionValidatorTest.java
```diff
@@ -16,6 +16,8 @@
 
 import static org.assertj.core.api.Assertions.assertThat;
 import static org.hyperledger.besu.ethereum.transaction.TransactionInvalidReason.GAS_PRICE_MUST_BE_ZERO;
+import static org.hyperledger.besu.ethereum.transaction.TransactionInvalidReason.INVALID_TRANSACTION_FORMAT;
+import static org.hyperledger.besu.ethereum.transaction.TransactionInvalidReason.UPFRONT_COST_EXCEEDS_BALANCE;
 import static org.mockito.ArgumentMatchers.any;
 import static org.mockito.ArgumentMatchers.anyBoolean;
 import static org.mockito.ArgumentMatchers.eq;
@@ -24,6 +26,7 @@
 import static org.mockito.Mockito.when;
 
 import org.hyperledger.besu.crypto.KeyPair;
+import org.hyperledger.besu.crypto.SECP256K1;
 import org.hyperledger.besu.crypto.SignatureAlgorithm;
 import org.hyperledger.besu.crypto.SignatureAlgorithmFactory;
 import org.hyperledger.besu.ethereum.core.Account;
@@ -45,6 +48,7 @@
 
 import com.google.common.base.Supplier;
 import com.google.common.base.Suppliers;
+import org.apache.tuweni.bytes.Bytes;
 import org.junit.Test;
 import org.junit.runner.RunWith;
 import org.mockito.ArgumentCaptor;
@@ -205,6 +209,63 @@ public void shouldAcceptValidTransactionIfAccountIsPermitted() {
         .isEqualTo(ValidationResult.valid());
   }
 
+  @Test
+  public void shouldRejectTransactionWithMaxFeeTimesGasLimitGreaterThanBalance() {
+    final MainnetTransactionValidator validator =
+        new MainnetTransactionValidator(
+            gasCalculator, false, Optional.empty(), defaultGoQuorumCompatibilityMode);
+    validator.setTransactionFilter(transactionFilter(true));
+
+    assertThat(
+            validator.validateForSender(
+                Transaction.builder()
+                    .type(TransactionType.EIP1559)
+                    .nonce(0)
+                    .maxPriorityFeePerGas(Wei.of(5))
+                    .maxFeePerGas(Wei.of(7))
+                    .gasLimit(15)
+                    .to(Address.ZERO)
+                    .value(Wei.of(0))
+                    .payload(Bytes.EMPTY)
+                    .chainId(BigInteger.ONE)
+                    .signAndBuild(new SECP256K1().generateKeyPair()),
+                account(Wei.of(100), 0),
+                true))
+        .isEqualTo(ValidationResult.invalid(UPFRONT_COST_EXCEEDS_BALANCE));
+  }
+
+  @Test
+  public void shouldRejectTransactionWithMaxPriorityFeeGreaterThanMaxFee() {
+    final MainnetTransactionValidator validator =
+        new MainnetTransactionValidator(
+            gasCalculator,
+            Optional.of(TransactionPriceCalculator.eip1559()),
+            false,
+            Optional.of(BigInteger.ONE),
+            Set.of(TransactionType.values()),
+            defaultGoQuorumCompatibilityMode);
+    validator.setTransactionFilter(transactionFilter(true));
+
+    final Transaction transaction =
+        Transaction.builder()
+            .type(TransactionType.EIP1559)
+            .nonce(0)
+            .maxPriorityFeePerGas(Wei.of(7))
+            .maxFeePerGas(Wei.of(4))
+            .gasLimit(15)
+            .to(Address.ZERO)
+            .value(Wei.of(0))
+            .payload(Bytes.EMPTY)
+            .chainId(BigInteger.ONE)
+            .signAndBuild(new SECP256K1().generateKeyPair());
+
+    final ValidationResult<TransactionInvalidReason> validationResult =
+        validator.validate(transaction, Optional.of(1L));
+    assertThat(validationResult).isEqualTo(ValidationResult.invalid(INVALID_TRANSACTION_FORMAT));
+    assertThat(validationResult.getErrorMessage())
+        .isEqualTo("max priority fee per gas cannot be greater than max fee per gas");
+  }
+
   @Test
   public void shouldPropagateCorrectStateChangeParamToTransactionFilter() {
     final ArgumentCaptor<Boolean> stateChangeLocalParamCaptor =
```

### plugin-api/build.gradle
```diff
@@ -64,7 +64,7 @@ Calculated : ${currentHash}
 tasks.register('checkAPIChanges', FileStateChecker) {
   description = "Checks that the API for the Plugin-API project does not change without deliberate thought"
   files = sourceSets.main.allJava.files
-  knownHash = 'VhijQ2/y9GqGlgxreOf6nIXZB6eSNb2m7uhibCPPJvI='
+  knownHash = 'hS/pEDa9mV5gqekY7f00rDxan6OC99cr/pMSx1rCQvI='
 }
 check.dependsOn('checkAPIChanges')
 
```

### plugin-api/src/main/java/org/hyperledger/besu/plugin/data/Quantity.java
```diff
@@ -14,6 +14,8 @@
  */
 package org.hyperledger.besu.plugin.data;
 
+import java.math.BigInteger;
+
 /**
  * An interface to mark objects that also represents a disceete quantity, such as an unsigned
  * integer value.
@@ -30,8 +32,11 @@ public interface Quantity {
    *
    * @return The boxed or object based value of the quantity.
    */
+  @Deprecated
   Number getValue();
 
+  BigInteger getAsBigInteger();
+
   /**
    * The value as a hexadecimal string.
    *
```
