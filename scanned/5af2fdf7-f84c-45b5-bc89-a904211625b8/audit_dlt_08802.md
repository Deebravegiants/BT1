# [?] fix: overflow for modexp arg (#489)

## Summary
Severity: Unknown
Chain: Linea
Component: LFDT-Lineth/lineth-monorepo
Published: 2023-12-13
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/92d24363743f716771509f1787bcf55496cfbf9c
Type: security-commit

## Details
fix: overflow for modexp arg (#489)

* fix: overflow for modexp arg

* fix: can be longer than 32 Bytes

## Patch
### tracer/arithmetization/src/main/java/net/consensys/linea/zktracer/module/Util.java
```diff
@@ -20,7 +20,6 @@
 
 import java.math.BigInteger;
 
-import net.consensys.linea.zktracer.types.EWord;
 import net.consensys.linea.zktracer.types.UnsignedByte;
 import org.apache.tuweni.bytes.Bytes;
 import org.apache.tuweni.units.bigints.UInt256;
@@ -183,10 +182,10 @@ public static Bytes slice(Bytes data, int positionStart, int size) {
 
     if (dataSize >= positionStart) {
       if (dataSize >= (positionStart + size)) {
-        output = EWord.of(data.slice(positionStart, size));
+        output = data.slice(positionStart, size);
       } else {
         final int nbPresentBytes = dataSize - positionStart;
-        output = EWord.of(rightPadTo(data.slice(positionStart, nbPresentBytes), size));
+        output = rightPadTo(data.slice(positionStart, nbPresentBytes), size);
       }
     }
     return output;
```

### tracer/arithmetization/src/main/java/net/consensys/linea/zktracer/module/limits/precompiles/Modexp.java
```diff
@@ -38,7 +38,7 @@
 public class Modexp implements Module {
   private final Hub hub;
   private final Stack<Integer> counts = new Stack<>();
-  private static final int PROVER_MAX_INPUT_BIT_SIZE = 4096;
+  private static final BigInteger PROVER_MAX_INPUT_BIT_SIZE = BigInteger.valueOf(4096);
   private static final int EVM_WORD_SIZE = 32;
 
   @Override
@@ -78,8 +78,9 @@ public void tracePreOpcode(MessageFrame frame) {
           }
           final Bytes inputData = frame.shadowReadMemory(offset, length);
 
-          final int baseLength = slice(inputData, 0, EVM_WORD_SIZE).toInt();
-          if (baseLength * 8 > PROVER_MAX_INPUT_BIT_SIZE) {
+          // Get the Base length
+          final BigInteger baseLength = slice(inputData, 0, EVM_WORD_SIZE).toUnsignedBigInteger();
+          if (baseLength.multiply(BigInteger.valueOf(8)).compareTo(PROVER_MAX_INPUT_BIT_SIZE) > 0) {
             log.info(
                 "Too big argument, base bit length = {} > {}",
                 baseLength,
@@ -88,16 +89,23 @@ public void tracePreOpcode(MessageFrame frame) {
             this.counts.push(Integer.MAX_VALUE);
             return;
           }
-          final int expLength = slice(inputData, EVM_WORD_SIZE, EVM_WORD_SIZE).toInt();
-          if (expLength * 8 > PROVER_MAX_INPUT_BIT_SIZE) {
+
+          // Get the Exponent length
+          final BigInteger expLength =
+              slice(inputData, EVM_WORD_SIZE, EVM_WORD_SIZE).toUnsignedBigInteger();
+          if (expLength.multiply(BigInteger.valueOf(8)).compareTo(PROVER_MAX_INPUT_BIT_SIZE) > 0) {
             log.info(
                 "Too big argument, exp bit length = {} > {}", expLength, PROVER_MAX_INPUT_BIT_SIZE);
             this.counts.pop();
             this.counts.push(Integer.MAX_VALUE);
             return;
           }
-          final int moduloLength = slice(inputData, 2 * EVM_WORD_SIZE, EVM_WORD_SIZE).toInt();
-          if (expLength * 8 > PROVER_MAX_INPUT_BIT_SIZE) {
+
+          // Get the Modulo length
+          final BigInteger moduloLength =
+              slice(inputData, 2 * EVM_WORD_SIZE, EVM_WORD_SIZE).toUnsignedBigInteger();
+          if (moduloLength.multiply(BigInteger.valueOf(8)).compareTo(PROVER_MAX_INPUT_BIT_SIZE)
+              > 0) {
             log.info(
                 "Too big argument, modulo bit length = {} > {}",
                 moduloLength,
@@ -106,11 +114,23 @@ public void tracePreOpcode(MessageFrame frame) {
             this.counts.push(Integer.MAX_VALUE);
             return;
           }
-          final Bytes exp = slice(inputData, 3 * EVM_WORD_SIZE + baseLength, expLength);
+
+          // Get the Exponent
+          final Bytes exp =
+              slice(
+                  inputData,
+                  3 * EVM_WORD_SIZE + baseLength.intValueExact(),
+                  expLength.intValueExact());
 
           final long gasPaid = Words.clampedToLong(frame.getStackItem(0));
 
-          if (gasPaid >= gasPrice(baseLength, expLength, moduloLength, exp)) {
+          // If enough gas, add 1 to the call of the precompile
+          if (gasPaid
+              >= gasPrice(
+                  baseLength.intValueExact(),
+                  expLength.intValueExact(),
+                  moduloLength.intValueExact(),
+                  exp)) {
             this.counts.push(this.counts.pop() + 1);
           }
         }
```

### tracer/zkevm-constraints
```diff
@@ -1 +1 @@
-Subproject commit 6e292276396e2309dac45e8905bdfc0fd45e8cf6
+Subproject commit 405afa488d169ec188702b2084ec5c608b415f38
```
