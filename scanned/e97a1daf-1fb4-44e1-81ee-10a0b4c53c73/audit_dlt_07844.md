# [?] Fix fork choice overflow\underflow bug (#9234)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys-Incorporated/teku
Published: 2025-03-14
Source: https://github.com/Consensys-Incorporated/teku/commit/a98149a53607d7ec1ceaa2f6d0bfbf5454ce395c
Type: security-commit

## Details
Fix fork choice overflow\underflow bug (#9234)

## Patch
### ethereum/statetransition/src/main/java/tech/pegasys/teku/statetransition/forkchoice/ForkChoice.java
```diff
@@ -376,6 +376,11 @@ private void updateHeadTransaction(
         spec.getBeaconStateUtil(justifiedState.getSlot())
             .getEffectiveActiveUnslashedBalances(justifiedState);
 
+    // If a runtime exception occurs while updating protoarray, we could skip the transaction
+    // commit.
+    // There is no clean way to solve it unless we move to a fully transactional protoarray update.
+    // Currently, the assumption is that any exception thrown by design is happening before any
+    // update to protoarray, so it is correct to skip the transaction commit.
     final Bytes32 headBlockRoot =
         transaction.applyForkChoiceScoreChanges(
             recentChainData.getCurrentEpoch().orElseThrow(),
@@ -385,17 +390,23 @@ private void updateHeadTransaction(
             recentChainData.getStore().getProposerBoostRoot(),
             spec.getProposerBoostAmount(justifiedState));
 
-    recentChainData.updateHead(
-        headBlockRoot,
-        nodeSlot.orElse(
-            forkChoiceStrategy
-                .blockSlot(headBlockRoot)
-                .orElseThrow(
-                    () ->
-                        new IllegalStateException(
-                            "Unable to retrieve the slot of fork choice head: " + headBlockRoot))));
-
-    transaction.commit();
+    try {
+      recentChainData.updateHead(
+          headBlockRoot,
+          nodeSlot.orElse(
+              forkChoiceStrategy
+                  .blockSlot(headBlockRoot)
+                  .orElseThrow(
+                      () ->
+                          new IllegalStateException(
+                              "Unable to retrieve the slot of fork choice head: "
+                                  + headBlockRoot))));
+    } finally {
+      // here we just make sure to commit, because protoarray has been updated. We just had an
+      // exception while updating recentChainData which will become consistent again on the next
+      // successful updateHead call
+      transaction.commit();
+    }
   }
 
   /**
@@ -833,7 +844,9 @@ private void storeEquivocatingIndices(
         .forEach(
             validatorIndex -> {
               final VoteTracker voteTracker = transaction.getVote(validatorIndex);
-              transaction.putVote(validatorIndex, voteTracker.createNextEquivocating());
+              if (!voteTracker.isEquivocating()) {
+                transaction.putVote(validatorIndex, voteTracker.createNextEquivocating());
+              }
             });
   }
 
```

### infrastructure/unsigned/src/main/java/tech/pegasys/teku/infrastructure/unsigned/UInt64.java
```diff
@@ -144,16 +144,14 @@ private UInt64 plus(final long longBits1, final long longBits2) {
     return fromLongBits(longBits1 + longBits2);
   }
 
-  public UInt64 safePlus(final long other) {
-    checkPositive(other);
+  public Optional<UInt64> safePlus(final long other) {
     if (value != 0 && Long.compareUnsigned(other, MAX_VALUE.longValue() - value) > 0) {
-      return UInt64.MAX_VALUE;
+      return Optional.empty();
     }
-    return plus(value, other);
+    return Optional.of(fromLongBits(value + other));
   }
 
-  public UInt64 safePlus(final UInt64 other) {
-    checkPositive(other.value);
+  public Optional<UInt64> safePlus(final UInt64 other) {
     return safePlus(other.value);
   }
 
```

### infrastructure/unsigned/src/test/java/tech/pegasys/teku/infrastructure/unsigned/UInt64Test.java
```diff
@@ -19,6 +19,7 @@
 
 import java.math.BigInteger;
 import java.util.List;
+import java.util.Optional;
 import java.util.stream.IntStream;
 import java.util.stream.Stream;
 import org.junit.jupiter.api.Test;
@@ -319,7 +320,7 @@ void plus_shouldThrowArithmeticExceptionWhenResultOverflows() {
   @ParameterizedTest
   @MethodSource("safePlusNumbers")
   void safePlus_shouldAddWhenNotOverflowingLongs(
-      final long value1, final long value2, final UInt64 expected) {
+      final long value1, final long value2, final Optional<UInt64> expected) {
     final UInt64 uint1 = UInt64.fromLongBits(value1);
     assertThat(uint1.safePlus(value2)).isEqualTo(expected);
   }
@@ -642,11 +643,12 @@ void range_shouldCreateStreamIncludingStartAndExcludingEnd(final int from, final
   static Stream<Arguments> safePlusNumbers() {
     final long max = UInt64.MAX_VALUE.longValue();
     return Stream.of(
-        Arguments.arguments(max, 0L, UInt64.MAX_VALUE),
-        Arguments.arguments(max - 10L, 10L, UInt64.MAX_VALUE),
-        Arguments.arguments(max - 11L, 10L, UInt64.MAX_VALUE.minus(1)),
-        Arguments.arguments(1L, 10L, UInt64.valueOf(11)),
-        Arguments.arguments(max, 1L, UInt64.MAX_VALUE));
+        Arguments.arguments(max, 0L, Optional.of(UInt64.MAX_VALUE)),
+        Arguments.arguments(max - 10L, 10L, Optional.of(UInt64.MAX_VALUE)),
+        Arguments.arguments(max - 11L, 10L, Optional.of(UInt64.MAX_VALUE.minus(1))),
+        Arguments.arguments(1L, 10L, Optional.of(UInt64.valueOf(11))),
+        Arguments.arguments(max, 1L, Optional.empty()),
+        Arguments.arguments(1L, max, Optional.empty()));
   }
 
   static List<Arguments> rangeNumbers() {
```

### storage/src/main/java/tech/pegasys/teku/storage/protoarray/ProtoArray.java
```diff
@@ -425,6 +425,10 @@ private void markDescendantsAsInvalid(final int index) {
    * Iterate backwards through the array, touching all nodes and their parents and potentially the
    * bestChildIndex of each parent.
    *
+   * <p>NOTE: this function should only throw exceptions when validating the parameters. Once we
+   * start updating the protoarray we should not throw exceptions because we are currently not able
+   * to rollback the changes. See {@link ForkChoiceStrategy#applyPendingVotes}.
+   *
    * <p>The structure of the `nodes` array ensures that the child of each node is always touched
    * before its parent.
    *
```

### storage/src/main/java/tech/pegasys/teku/storage/protoarray/ProtoNode.java
```diff
@@ -95,25 +95,34 @@ public class ProtoNode {
 
   public void adjustWeight(final long delta) {
     if (delta < 0) {
-      UInt64 deltaAbsoluteValue = UInt64.valueOf(Math.abs(delta));
-      if (deltaAbsoluteValue.isGreaterThan(weight)) {
-        throw new RuntimeException(
-            "ProtoNode: Delta to be subtracted is greater than node weight for block "
-                + blockRoot
-                + " ("
-                + blockSlot
-                + "). Attempting to subtract "
-                + deltaAbsoluteValue
-                + " from "
-                + weight);
-      }
-      weight = weight.minus(deltaAbsoluteValue);
+      final long absoluteDelta = -delta;
+      weight =
+          weight
+              .safeMinus(absoluteDelta)
+              .orElseGet(
+                  () -> {
+                    LOG.error(
+                        "PLEASE FIX OR REPORT ProtoArray adjustWeight bug: Delta to be subtracted is greater than node weight for block {} ({}). Attempting to subtract {} from {}",
+                        blockRoot,
+                        blockSlot,
+                        absoluteDelta,
+                        weight);
+                    return UInt64.ZERO;
+                  });
     } else {
-      final UInt64 newWeight = weight.safePlus(delta);
-      if (newWeight.equals(UInt64.MAX_VALUE)) {
-        LOG.trace("Unable to add delta {} to weight {}", delta, weight);
-      }
-      weight = newWeight;
+      weight =
+          weight
+              .safePlus(delta)
+              .orElseGet(
+                  () -> {
+                    LOG.error(
+                        "PLEASE FIX OR REPORT ProtoArray adjustWeight bug: Delta to be added causes uint64 overflow for block {} ({}). Attempting to add {} to {}",
+                        blockRoot,
+                        blockSlot,
+                        delta,
+                        weight);
+                    return UInt64.MAX_VALUE;
+                  });
     }
   }
 
```
