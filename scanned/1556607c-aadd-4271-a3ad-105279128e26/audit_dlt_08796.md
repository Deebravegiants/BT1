# [?] fix(exp and mxp and oob and ecdata): turned toBigInteger() into toUnsignedBigInteger() (#765)

## Summary
Severity: Unknown
Chain: Linea
Component: LFDT-Lineth/lineth-monorepo
Published: 2024-06-06
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/2a65f89d72fc472d9a117a00f121e4894a3491ca
Type: security-commit

## Details
fix(exp and mxp and oob and ecdata): turned toBigInteger() into toUnsignedBigInteger() (#765)

## Patch
### tracer/arithmetization/src/main/java/net/consensys/linea/zktracer/module/ecdata/EcDataOperation.java
```diff
@@ -373,10 +373,10 @@ private static EWord extractRecoveredAddress(EWord h, EWord v, EWord r, EWord s)
           secp256K1.recoverPublicKeyFromSignature(
               h.toBytes(),
               SECPSignature.create(
-                  r.toBigInteger(),
-                  s.toBigInteger(),
+                  r.toUnsignedBigInteger(),
+                  s.toUnsignedBigInteger(),
                   (byte) (v.toInt() - 27),
-                  SECP256K1N.toBigInteger()));
+                  SECP256K1N.toUnsignedBigInteger()));
       return optionalRecoveredAddress
           .map(e -> EWord.of(Hash.keccak256(e.getEncodedBytes()).slice(32 - 20)))
           .orElse(EWord.ZERO);
```

### tracer/arithmetization/src/main/java/net/consensys/linea/zktracer/module/exp/ExpOperation.java
```diff
@@ -91,7 +91,7 @@ final void traceComputation(int stamp, Trace trace) {
       pComputationMsb
       */
       // tanzb turns to 1 iff trimAcc is nonzero
-      tanzb = pComputationTrimAcc.slice(0, i + 1).toBigInteger().signum() != 0;
+      tanzb = pComputationTrimAcc.slice(0, i + 1).toUnsignedBigInteger().signum() != 0;
       pComputationTanzbAcc += (short) (tanzb ? 1 : 0);
       // manzb turns to 1 iff msbAcc is nonzero
       manzb = i > maxCt - 8 && pComputationMsb.slice(0, i % 8 + 1) != 0;
```

### tracer/arithmetization/src/main/java/net/consensys/linea/zktracer/module/mxp/Chunk.java
```diff
@@ -1,18 +0,0 @@
-/*
- * Copyright Consensys Software Inc.
- *
- * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
- * the License. You may obtain a copy of the License at
- *
- * http://www.apache.org/licenses/LICENSE-2.0
- *
- * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
- * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
- * specific language governing permissions and limitations under the License.
- *
- * SPDX-License-Identifier: Apache-2.0
- */
-
-package net.consensys.linea.zktracer.module.mxp;
-
-public record Chunk() {}
```

### tracer/arithmetization/src/main/java/net/consensys/linea/zktracer/module/mxp/Mxp.java
```diff
@@ -27,7 +27,7 @@
 /** Implementation of a {@link Module} for memory expansion. */
 public class Mxp implements Module {
   /** A list of the operations to trace */
-  private final StackedList<MxpData> chunks = new StackedList<>();
+  private final StackedList<MxpOperation> chunks = new StackedList<>();
 
   private Hub hub;
 
@@ -45,7 +45,7 @@ public Mxp() {}
 
   @Override
   public void tracePreOpcode(MessageFrame frame) { // This will be renamed to tracePreOp
-    this.chunks.add(new MxpData(frame, hub));
+    this.chunks.add(new MxpOperation(frame, hub));
   }
 
   @Override
```

### tracer/arithmetization/src/main/java/net/consensys/linea/zktracer/module/mxp/MxpOperation.java
```diff
@@ -46,7 +46,7 @@
 import org.hyperledger.besu.evm.internal.Words;
 
 @Getter
-public class MxpData extends ModuleOperation {
+public class MxpOperation extends ModuleOperation {
   public static final BigInteger TWO_POW_128 = BigInteger.ONE.shiftLeft(128);
   public static final BigInteger TWO_POW_32 = BigInteger.ONE.shiftLeft(32);
 
@@ -90,7 +90,7 @@ public class MxpData extends ModuleOperation {
   private long linCost = 0;
   private final boolean deploys;
 
-  public MxpData(final MessageFrame frame, final Hub hub) {
+  public MxpOperation(final MessageFrame frame, final Hub hub) {
     this.opCodeData = hub.opCodeData();
     this.contextNumber = hub.currentFrame().contextNumber();
     this.typeMxp = opCodeData.billing().type();
@@ -192,16 +192,16 @@ private void setOffsetsAndSizes(final MessageFrame frame) {
   protected void setRoob() {
     roob =
         switch (typeMxp) {
-          case TYPE_2, TYPE_3 -> offset1.toBigInteger().compareTo(TWO_POW_128) >= 0;
-          case TYPE_4 -> size1.toBigInteger().compareTo(TWO_POW_128) >= 0
-              || (offset1.toBigInteger().compareTo(TWO_POW_128) >= 0
-                  && !size1.toBigInteger().equals(BigInteger.ZERO));
-          case TYPE_5 -> size1.toBigInteger().compareTo(TWO_POW_128) >= 0
-              || (offset1.toBigInteger().compareTo(TWO_POW_128) >= 0
-                  && !size1.toBigInteger().equals(BigInteger.ZERO))
-              || (size2.toBigInteger().compareTo(TWO_POW_128) >= 0
-                  || (offset2.toBigInteger().compareTo(TWO_POW_128) >= 0
-                      && !size2.toBigInteger().equals(BigInteger.ZERO)));
+          case TYPE_2, TYPE_3 -> offset1.toUnsignedBigInteger().compareTo(TWO_POW_128) >= 0;
+          case TYPE_4 -> size1.toUnsignedBigInteger().compareTo(TWO_POW_128) >= 0
+              || (offset1.toUnsignedBigInteger().compareTo(TWO_POW_128) >= 0
+                  && !size1.toUnsignedBigInteger().equals(BigInteger.ZERO));
+          case TYPE_5 -> size1.toUnsignedBigInteger().compareTo(TWO_POW_128) >= 0
+              || (offset1.toUnsignedBigInteger().compareTo(TWO_POW_128) >= 0
+                  && !size1.toUnsignedBigInteger().equals(BigInteger.ZERO))
+              || (size2.toUnsignedBigInteger().compareTo(TWO_POW_128) >= 0
+                  || (offset2.toUnsignedBigInteger().compareTo(TWO_POW_128) >= 0
+                      && !size2.toUnsignedBigInteger().equals(BigInteger.ZERO)));
           default -> false;
         };
   }
@@ -228,19 +228,31 @@ private void setMtntop() {
   protected void setMaxOffset1and2() {
     if (getMxpExecutionPath() != mxpExecutionPath.TRIVIAL) {
       switch (typeMxp) {
-        case TYPE_2 -> maxOffset1 = offset1.toBigInteger().add(BigInteger.valueOf(31));
-        case TYPE_3 -> maxOffset1 = offset1.toBigInteger();
+        case TYPE_2 -> maxOffset1 = offset1.toUnsignedBigInteger().add(BigInteger.valueOf(31));
+        case TYPE_3 -> maxOffset1 = offset1.toUnsignedBigInteger();
         case TYPE_4 -> {
-          if (!size1.toBigInteger().equals(BigInteger.ZERO)) {
-            maxOffset1 = offset1.toBigInteger().add(size1.toBigInteger()).subtract(BigInteger.ONE);
+          if (!size1.toUnsignedBigInteger().equals(BigInteger.ZERO)) {
+            maxOffset1 =
+                offset1
+                    .toUnsignedBigInteger()
+                    .add(size1.toUnsignedBigInteger())
+                    .subtract(BigInteger.ONE);
           }
         }
         case TYPE_5 -> {
-          if (!size1.toBigInteger().equals(BigInteger.ZERO)) {
-            maxOffset1 = offset1.toBigInteger().add(size1.toBigInteger()).subtract(BigInteger.ONE);
+          if (!size1.toUnsignedBigInteger().equals(BigInteger.ZERO)) {
+            maxOffset1 =
+                offset1
+                    .toUnsignedBigInteger()
+                    .add(size1.toUnsignedBigInteger())
+                    .subtract(BigInteger.ONE);
           }
-          if (!size2.toBigInteger().equals(BigInteger.ZERO)) {
-            maxOffset2 = offset2.toBigInteger().add(size2.toBigInteger()).subtract(BigInteger.ONE);
+          if (!size2.toUnsignedBigInteger().equals(BigInteger.ZERO)) {
+            maxOffset2 =
+                offset2
+                    .toUnsignedBigInteger()
+                    .add(size2.toUnsignedBigInteger())
+                    .subtract(BigInteger.ONE);
           }
         }
       }
@@ -354,9 +366,10 @@ protected void setAccWAndLastTwoBytesOfByteR() {
         return;
       }
 
-      accW = size1.toBigInteger().add(BigInteger.valueOf(31)).divide(BigInteger.valueOf(32));
+      accW =
+          size1.toUnsignedBigInteger().add(BigInteger.valueOf(31)).divide(BigInteger.valueOf(32));
 
-      BigInteger r = accW.multiply(BigInteger.valueOf(32)).subtract(size1.toBigInteger());
+      BigInteger r = accW.multiply(BigInteger.valueOf(32)).subtract(size1.toUnsignedBigInteger());
 
       // r in [0,31]
       UnsignedByte rByte = UnsignedByte.of(r.toByteArray()[r.toByteArray().length - 1]);
@@ -439,7 +452,7 @@ protected void setBytes() {
   }
 
   private void setWordsNew(final MessageFrame frame) {
-    if (getMxpExecutionPath() == MxpData.mxpExecutionPath.NON_TRIVIAL && expands) {
+    if (getMxpExecutionPath() == MxpOperation.mxpExecutionPath.NON_TRIVIAL && expands) {
       switch (getTypeMxp()) {
         case TYPE_1 -> wordsNew = frame.calculateMemoryExpansion(Words.clampedToLong(offset1), 0);
         case TYPE_2 -> wordsNew = frame.calculateMemoryExpansion(Words.clampedToLong(offset1), 32);
@@ -461,7 +474,7 @@ private void setWordsNew(final MessageFrame frame) {
   }
 
   private void setCMemNew() {
-    if (getMxpExecutionPath() == MxpData.mxpExecutionPath.NON_TRIVIAL && expands) {
+    if (getMxpExecutionPath() == MxpOperation.mxpExecutionPath.NON_TRIVIAL && expands) {
       cMemNew = memoryCost(wordsNew);
     }
   }
```

### tracer/arithmetization/src/main/java/net/consensys/linea/zktracer/module/oob/OobOperation.java
```diff
@@ -191,7 +191,7 @@ public OobOperation(
   private void setOpCodeFlagsAndWghtSumAndIncomingInst(MessageFrame frame) {
     final OpCode opCode = OpCode.of(frame.getCurrentOperation().getOpcode());
     // In the case of CALLs and CREATEs this value will be replaced
-    wghtSum = UnsignedByte.of(opCode.byteValue()).toBigInteger();
+    wghtSum = BigInteger.valueOf(Byte.toUnsignedInt(opCode.byteValue()));
 
     switch (opCode) {
       case JUMP:
```
