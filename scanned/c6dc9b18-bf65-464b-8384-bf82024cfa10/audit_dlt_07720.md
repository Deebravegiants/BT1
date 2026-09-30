# [?] fix exponent overflow (#2014)

## Summary
Severity: Unknown
Chain: Ethereum
Component: besu-eth/besu
Published: 2021-03-13
Source: https://github.com/besu-eth/besu/commit/a5d078f46d0f6f2f0553a807bd394db3112c9e22
Type: security-commit

## Details
fix exponent overflow (#2014)

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

## Patch
### ethereum/core/src/main/java/org/hyperledger/besu/ethereum/mainnet/precompiles/BigIntegerModularExponentiationPrecompiledContract.java
```diff
@@ -58,6 +58,12 @@ public Bytes compute(final Bytes input, final MessageFrame messageFrame) {
     final BigInteger baseLength = baseLength(input);
     final BigInteger exponentLength = exponentLength(input);
     final BigInteger modulusLength = modulusLength(input);
+    // If baseLength and modulusLength are zero
+    // we could have a massively overflowing exp because it wouldn't have been filtered out at the
+    // gas cost phase
+    if (baseLength.equals(BigInteger.ZERO) && modulusLength.equals(BigInteger.ZERO)) {
+      return Bytes.EMPTY;
+    }
     final BigInteger exponentOffset = BASE_OFFSET.add(baseLength);
     final BigInteger modulusOffset = exponentOffset.add(exponentLength);
     final BigInteger base = extractParameter(input, BASE_OFFSET, baseLength.intValue());
```
