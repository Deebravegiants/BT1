# [?] Fix overflow/underflow instances (#2538)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys/teku
Published: 2020-08-09
Source: https://github.com/Consensys-Incorporated/teku/commit/f796cc5fe0f6dbed5ea3627fb3da921922a48952
Type: security-commit

## Details
Fix overflow/underflow instances (#2538)

Fix PendingPool to avoid overflows instead of handling them afterwards.
Update GetValidators to handle overflow when calculating slot from epoch.
Fix underflow in ForkChoiceUtil.getAncestors
Update tests to avoid overflows.

## Patch
### data/beaconrestapi/src/main/java/tech/pegasys/teku/beaconrestapi/handlers/beacon/GetValidators.java
```diff
@@ -133,7 +133,7 @@ public void handle(Context ctx) throws Exception {
         this.handlePossiblyMissingResult(
             ctx, future, getResultProcessor(activeOnly, pageSize, pageToken));
       }
-    } catch (final IllegalArgumentException e) {
+    } catch (final IllegalArgumentException | ArithmeticException e) {
       ctx.result(jsonProvider.objectToJSON(new BadRequest(e.getMessage())));
       ctx.status(SC_BAD_REQUEST);
     }
```

### data/beaconrestapi/src/test/java/tech/pegasys/teku/beaconrestapi/handlers/beacon/GetValidatorsTest.java
```diff
@@ -48,7 +48,7 @@
 public class GetValidatorsTest {
   private final DataStructureUtil dataStructureUtil = new DataStructureUtil();
   private Context context = mock(Context.class);
-  private final UnsignedLong epoch = dataStructureUtil.randomUnsignedLong();
+  private final UnsignedLong epoch = dataStructureUtil.randomEpoch();
   private final JsonProvider jsonProvider = new JsonProvider();
   private final Bytes32 blockRoot = dataStructureUtil.randomBytes32();
   private final tech.pegasys.teku.datastructures.state.BeaconState beaconStateInternal =
@@ -277,15 +277,10 @@ public void shouldReturnBadRequestWhenBadEpochParameterSpecified() throws Except
   @Test
   public void shouldReturnEmptyListWhenQueryByActiveAndFarFutureEpoch() throws Exception {
     final GetValidators handler = new GetValidators(provider, jsonProvider);
-    final UnsignedLong farFutureSlot =
-        BeaconStateUtil.compute_start_slot_at_epoch(Constants.FAR_FUTURE_EPOCH);
+    final UnsignedLong futureEpoch = UnsignedLong.valueOf(294829482492L);
+    final UnsignedLong farFutureSlot = BeaconStateUtil.compute_start_slot_at_epoch(futureEpoch);
     when(context.queryParamMap())
-        .thenReturn(
-            Map.of(
-                ACTIVE,
-                List.of("true"),
-                EPOCH,
-                List.of(String.valueOf(Constants.FAR_FUTURE_EPOCH))));
+        .thenReturn(Map.of(ACTIVE, List.of("true"), EPOCH, List.of(futureEpoch.toString())));
     when(provider.isStoreAvailable()).thenReturn(true);
     when(provider.getBestBlockRoot()).thenReturn(Optional.of(blockRoot));
     when(provider.getStateAtSlot(farFutureSlot))
```

### data/serializer/src/test/java/tech/pegasys/teku/api/schema/BeaconChainHeadTest.java
```diff
@@ -25,8 +25,9 @@
 
 class BeaconChainHeadTest {
   private final DataStructureUtil dataStructureUtil = new DataStructureUtil();
-  private BeaconState beaconState = dataStructureUtil.randomBeaconState();
-  private BeaconBlockAndState blockAndState = dataStructureUtil.randomBlockAndState(1, beaconState);
+  private final BeaconState beaconState = dataStructureUtil.randomBeaconState();
+  private final BeaconBlockAndState blockAndState =
+      dataStructureUtil.randomBlockAndState(1, beaconState);
 
   @Test
   public void shouldCreateFromBlockAndState() {
```

### ethereum/core/src/main/java/tech/pegasys/teku/core/ForkChoiceUtil.java
```diff
@@ -129,6 +129,7 @@ private static void maybeAddRoot(
     maybeSlot.ifPresent(
         slot -> {
           if (slot.compareTo(endSlot) <= 0
+              && slot.compareTo(startSlot) >= 0
               && slot.minus(startSlot).mod(step).equals(UnsignedLong.ZERO)) {
             roots.put(slot, root);
           }
```

### ethereum/datastructures/src/testFixtures/java/tech/pegasys/teku/datastructures/util/DataStructureUtil.java
```diff
@@ -183,8 +183,16 @@ public Eth1Data randomEth1Data() {
     return new Eth1Data(randomBytes32(), randomUnsignedLong(), randomBytes32());
   }
 
+  /**
+   * A random UnsignedLong that is within a reasonable bound for an epoch number. The maximum value
+   * returned won't be reached for another 12,000 years or so.
+   */
+  public UnsignedLong randomEpoch() {
+    return UnsignedLong.valueOf(new Random(nextSeed()).nextInt(1_000_000_000));
+  }
+
   public Checkpoint randomCheckpoint() {
-    return new Checkpoint(randomUnsignedLong(), randomBytes32());
+    return new Checkpoint(randomEpoch(), randomBytes32());
   }
 
   public AttestationData randomAttestationData() {
```

### ethereum/statetransition/src/main/java/tech/pegasys/teku/statetransition/util/PendingPool.java
```diff
@@ -293,13 +293,9 @@ private boolean isFromAFinalizedSlot(final T item) {
   }
 
   private UnsignedLong calculateItemAgeLimit() {
-    final UnsignedLong ageLimit =
-        currentSlot.minus(UnsignedLong.ONE).minus(historicalSlotTolerance);
-    if (ageLimit.compareTo(currentSlot) > 0) {
-      // If subtraction caused overflow, return genesis slot
-      return GENESIS_SLOT;
-    }
-    return ageLimit;
+    return currentSlot.compareTo(historicalSlotTolerance.plus(UnsignedLong.ONE)) > 0
+        ? currentSlot.minus(UnsignedLong.ONE).minus(historicalSlotTolerance)
+        : GENESIS_SLOT;
   }
 
   private UnsignedLong calculateFutureItemLimit() {
```

### networking/eth2/src/main/java/tech/pegasys/teku/networking/eth2/rpc/core/RpcException.java
```diff
@@ -90,8 +90,7 @@ public RpcException(final byte responseCode, final String errorMessage) {
   }
 
   public RpcException(final byte responseCode, final RpcErrorMessage errorMessage) {
-    this.responseCode = responseCode;
-    this.errorMessage = errorMessage.toString();
+    this(responseCode, errorMessage.toString());
   }
 
   public byte getResponseCode() {
```

### validator/client/src/test/java/tech/pegasys/teku/validator/client/signer/SignerTest.java
```diff
@@ -58,7 +58,7 @@ public void shouldSignBlock1() {
     final BeaconBlock block = dataStructureUtil.randomBeaconBlock(10);
     final BLSSignature signature = dataStructureUtil.randomSignature();
     final Bytes expectedSigningRoot =
-        Bytes.fromHexString("0xfa8b3cfed0268ed15e354e84db5558eb76ad30737a86d6d057615e331ff30d44");
+        Bytes.fromHexString("0xf6c68e87f3dbbe3d05de8eae204396ddea7fe13ffad0008f06748c9aa23fcc05");
     when(signerService.signBlock(expectedSigningRoot))
         .thenReturn(SafeFuture.completedFuture(signature));
 
@@ -73,7 +73,7 @@ public void shouldSignAttestationData() {
     final AttestationData attestationData = dataStructureUtil.randomAttestationData();
     final BLSSignature signature = dataStructureUtil.randomSignature();
     final Bytes expectedSigningRoot =
-        Bytes.fromHexString("0xc9e1788b5b1864e701e69969418d635ac48f1e7b6ab65113f981798d55f305cc");
+        Bytes.fromHexString("0x418f2ed4e878074a64b23102a90582d32099f3e74787a04a13ec0cecc86c070a");
     when(signerService.signAttestation(expectedSigningRoot))
         .thenReturn(SafeFuture.completedFuture(signature));
 
```
