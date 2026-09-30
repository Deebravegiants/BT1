# [?] fix committees computation overflow (#7408)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys-Incorporated/teku
Published: 2023-08-01
Source: https://github.com/Consensys-Incorporated/teku/commit/8882b2f0585a93e215f1603a520c5c53ccc174c2
Type: security-commit

## Details
fix committees computation overflow (#7408)

* fix committee computation overflow

## Patch
### CHANGELOG.md
```diff
@@ -21,3 +21,5 @@ For information on changes in released versions of Teku, see the [releases page]
 - The default state-cache size has been changed to 8 (previously 160), and there is now an epoch-states-cache, which defaults to a maximum of 6 elements. 
 
 ### Bug Fixes
+
+- Fixed a possibility of overflow errors when calculating validator duties if the number of active validators is >1M. 
```

### ethereum/spec/src/main/java/tech/pegasys/teku/spec/logic/common/helpers/MiscHelpers.java
```diff
@@ -158,16 +158,25 @@ public UInt64 getEarliestQueryableSlotForBeaconCommitteeInTargetEpoch(final UInt
   }
 
   public IntList computeCommittee(
-      BeaconState state, IntList indices, Bytes32 seed, int index, int count) {
-    int start = Math.floorDiv(indices.size() * index, count);
-    int end = Math.floorDiv(indices.size() * (index + 1), count);
+      final BeaconState state,
+      final IntList indices,
+      final Bytes32 seed,
+      final int index,
+      final int count) {
+    final UInt64 indicesSize = UInt64.valueOf(indices.size());
+    final int start = indicesSize.times(index).dividedBy(count).intValue();
+    final int end = indicesSize.times(index + 1).dividedBy(count).intValue();
     return computeCommitteeShuffle(state, indices, seed, start, end);
   }
 
   private IntList computeCommitteeShuffle(
-      BeaconState state, IntList indices, Bytes32 seed, int fromIndex, int toIndex) {
+      final BeaconState state,
+      final IntList indices,
+      final Bytes32 seed,
+      final int fromIndex,
+      final int toIndex) {
     if (fromIndex < toIndex) {
-      int indexCount = indices.size();
+      final int indexCount = indices.size();
       checkArgument(fromIndex < indexCount, "CommitteeUtil.getShuffledIndex1");
       checkArgument(toIndex <= indexCount, "CommitteeUtil.getShuffledIndex1");
     }
```

### ethereum/spec/src/test/java/tech/pegasys/teku/spec/logic/common/helpers/MiscHelpersTest.java
```diff
@@ -25,19 +25,23 @@
 import java.util.stream.IntStream;
 import java.util.stream.Stream;
 import org.apache.tuweni.bytes.Bytes32;
+import org.junit.jupiter.api.Assertions;
 import org.junit.jupiter.api.Test;
 import org.junit.jupiter.params.ParameterizedTest;
 import org.junit.jupiter.params.provider.Arguments;
 import org.junit.jupiter.params.provider.MethodSource;
 import tech.pegasys.teku.infrastructure.unsigned.UInt64;
+import tech.pegasys.teku.spec.Spec;
+import tech.pegasys.teku.spec.TestSpecFactory;
 import tech.pegasys.teku.spec.config.SpecConfig;
-import tech.pegasys.teku.spec.config.SpecConfigLoader;
-import tech.pegasys.teku.spec.networks.Eth2Network;
+import tech.pegasys.teku.spec.util.DataStructureUtil;
 
 class MiscHelpersTest {
-  private final SpecConfig specConfig =
-      SpecConfigLoader.loadConfig(Eth2Network.MINIMAL.configName());
+
+  private final Spec spec = TestSpecFactory.createMinimalPhase0();
+  private final SpecConfig specConfig = spec.getGenesisSpecConfig();
   private final MiscHelpers miscHelpers = new MiscHelpers(specConfig);
+  private final DataStructureUtil dataStructureUtil = new DataStructureUtil(spec);
 
   @Test
   void computeShuffledIndex_boundaryTest() {
@@ -179,6 +183,21 @@ public void computesTimeAtSlot(final UInt64 slot, final long expectedTime) {
     assertThat(actualTime).isEqualTo(UInt64.valueOf(expectedTime));
   }
 
+  @ParameterizedTest
+  @MethodSource("getCommitteeComputationArguments")
+  public void committeeComputationShouldNotOverflow(int activeValidatorsCount, int committeeIndex) {
+    final IntList indices = IntList.of(IntStream.range(0, activeValidatorsCount).toArray());
+    Assertions.assertDoesNotThrow(
+        () -> {
+          miscHelpers.computeCommittee(
+              dataStructureUtil.randomBeaconState(),
+              indices,
+              dataStructureUtil.randomBytes32(),
+              committeeIndex,
+              2048);
+        });
+  }
+
   public static Stream<Arguments> getComputesSlotAtTimeArguments() {
     // 6 seconds per slot
     return Stream.of(
@@ -201,4 +220,8 @@ public static Stream<Arguments> getNValues() {
     return Stream.of(
         Arguments.of(1), Arguments.of(2), Arguments.of(3), Arguments.of(4), Arguments.of(5));
   }
+
+  public static Stream<Arguments> getCommitteeComputationArguments() {
+    return Stream.of(Arguments.of(2_100_000, 1024), Arguments.of(1_049_088, 2047));
+  }
 }
```
