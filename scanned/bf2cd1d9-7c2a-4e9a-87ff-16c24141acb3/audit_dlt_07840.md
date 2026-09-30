# [?] Fix maxSlot overflow in all byRange handlers (#10924)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys-Incorporated/teku
Published: 2026-07-03
Source: https://github.com/Consensys-Incorporated/teku/commit/82cc7904036b23ccf9790abeae9f66665841ac58
Type: security-commit

## Details
Fix maxSlot overflow in all byRange handlers (#10924)

## Patch
### networking/eth2/src/main/java/tech/pegasys/teku/networking/eth2/rpc/beaconchain/methods/BlobSidecarsByRangeMessageHandler.java
```diff
@@ -81,13 +81,19 @@ public BlobSidecarsByRangeMessageHandler(
   @Override
   public Optional<RpcException> validateRequest(
       final String protocolId, final BlobSidecarsByRangeRequestMessage request) {
+    final UInt64 maxSlot;
+    try {
+      maxSlot = request.getMaxSlot();
+    } catch (final ArithmeticException __) {
+      return Optional.of(
+          new RpcException(INVALID_REQUEST_CODE, "Requested slot is too far in the future"));
+    }
 
     final SpecConfigDeneb specConfig =
-        SpecConfigDeneb.required(
-            spec.atSlot(getEndSlotBeforeFulu(request.getMaxSlot())).getConfig());
+        SpecConfigDeneb.required(spec.atSlot(getEndSlotBeforeFulu(maxSlot)).getConfig());
 
     final int maxRequestBlobSidecars = specConfig.getMaxRequestBlobSidecars();
-    final int maxBlobsPerBlock = spec.getMaxBlobsPerBlockAtSlot(request.getMaxSlot()).orElseThrow();
+    final int maxBlobsPerBlock = spec.getMaxBlobsPerBlockAtSlot(maxSlot).orElseThrow();
 
     final int requestedCount = calculateRequestedCount(request, maxBlobsPerBlock);
 
```

### networking/eth2/src/main/java/tech/pegasys/teku/networking/eth2/rpc/beaconchain/methods/DataColumnSidecarsByRangeMessageHandler.java
```diff
@@ -92,11 +92,19 @@ public DataColumnSidecarsByRangeMessageHandler(
   @Override
   public Optional<RpcException> validateRequest(
       final String protocolId, final DataColumnSidecarsByRangeRequestMessage request) {
+    final UInt64 maxSlot;
+    try {
+      maxSlot = request.getMaxSlot();
+    } catch (final ArithmeticException __) {
+      return Optional.of(
+          new RpcException(INVALID_REQUEST_CODE, "Requested slot is too far in the future"));
+    }
+
     final int requestedCount = calculateRequestedCount(request);
     final int maxRequestDataColumnSidecars;
     try {
       maxRequestDataColumnSidecars =
-          spec.atSlot(request.getMaxSlot()).miscHelpers().getMaxRequestDataColumnSidecars();
+          spec.atSlot(maxSlot).miscHelpers().getMaxRequestDataColumnSidecars();
     } catch (final UnsupportedOperationException __) {
       return Optional.of(
           new RpcException(
```

### networking/eth2/src/main/java/tech/pegasys/teku/networking/eth2/rpc/beaconchain/methods/ExecutionPayloadEnvelopesByRangeMessageHandler.java
```diff
@@ -80,6 +80,13 @@ public ExecutionPayloadEnvelopesByRangeMessageHandler(
   @Override
   public Optional<RpcException> validateRequest(
       final String protocolId, final ExecutionPayloadEnvelopesByRangeRequestMessage request) {
+    try {
+      request.getMaxSlot();
+    } catch (final ArithmeticException __) {
+      return Optional.of(
+          new RpcException(INVALID_REQUEST_CODE, "Requested slot is too far in the future"));
+    }
+
     if (request.getCount().isGreaterThan(config.getMaxRequestBlocksDeneb())) {
       requestCounter.labels("count_too_big").inc();
       return Optional.of(
```

### networking/eth2/src/test/java/tech/pegasys/teku/networking/eth2/rpc/beaconchain/methods/BlobSidecarsByRangeMessageHandlerTest.java
```diff
@@ -146,6 +146,19 @@ public void validateRequest_validRequest() {
     assertThat(result).isEmpty();
   }
 
+  @TestTemplate
+  public void validateRequest_shouldRejectRequestWhenGetMaxSlotOverflows() {
+    final Optional<RpcException> result =
+        handler.validateRequest(
+            protocolId,
+            new BlobSidecarsByRangeRequestMessage(
+                UInt64.MAX_VALUE, UInt64.valueOf(10), maxBlobsPerBlock));
+
+    assertThat(result)
+        .hasValue(
+            new RpcException(INVALID_REQUEST_CODE, "Requested slot is too far in the future"));
+  }
+
   @TestTemplate
   public void validateRequest_shouldRejectRequestWhenCountIsTooBig() {
     final UInt64 maxRequestBlobSidecars =
```

### networking/eth2/src/test/java/tech/pegasys/teku/networking/eth2/rpc/beaconchain/methods/DataColumnSidecarsByRangeMessageHandlerTest.java
```diff
@@ -153,6 +153,19 @@ public void validateRequest_validRequest() {
     assertThat(result).isEmpty();
   }
 
+  @TestTemplate
+  public void validateRequest_shouldRejectRequestWhenGetMaxSlotOverflows() {
+    final Optional<RpcException> result =
+        handler.validateRequest(
+            protocolId,
+            dataColumnSidecarsByRangeRequestMessageSchema.create(
+                UInt64.MAX_VALUE, UInt64.valueOf(10), columnIndices));
+
+    assertThat(result)
+        .hasValue(
+            new RpcException(INVALID_REQUEST_CODE, "Requested slot is too far in the future"));
+  }
+
   @TestTemplate
   public void validateRequest_shouldRejectRequestWhenCountIsTooBig() {
     final DataColumnSidecarsByRangeRequestMessage request =
```

### networking/eth2/src/test/java/tech/pegasys/teku/networking/eth2/rpc/beaconchain/methods/ExecutionPayloadEnvelopesByRangeMessageHandlerTest.java
```diff
@@ -25,6 +25,7 @@
 import static org.mockito.Mockito.when;
 import static tech.pegasys.teku.infrastructure.metrics.TekuMetricCategory.NETWORK;
 import static tech.pegasys.teku.infrastructure.unsigned.UInt64.ZERO;
+import static tech.pegasys.teku.networking.eth2.rpc.core.RpcResponseStatus.INVALID_REQUEST_CODE;
 
 import java.util.List;
 import java.util.Optional;
@@ -126,6 +127,20 @@ void validateRequest_maxCount() {
     assertThat(getLabelledCounterValue("count_too_big")).isEqualTo(0);
   }
 
+  @Test
+  void validateRequest_shouldRejectRequestWhenGetMaxSlotOverflows() {
+    final Optional<RpcException> response =
+        handler.validateRequest(
+            PROTOCOL_ID,
+            new ExecutionPayloadEnvelopesByRangeRequestMessage(
+                UInt64.MAX_VALUE, UInt64.valueOf(10)));
+
+    assertThat(response)
+        .hasValue(
+            new RpcException(INVALID_REQUEST_CODE, "Requested slot is too far in the future"));
+    verifyNoInteractions(combinedChainDataClient);
+  }
+
   @Test
   void onIncomingMessage_requestNotApproved() {
     when(peer.approveRequest()).thenReturn(false);
```
