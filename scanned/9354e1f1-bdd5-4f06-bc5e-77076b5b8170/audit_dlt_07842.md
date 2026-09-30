# [?] Fix TOCTOU race condition for duplicate attestations (#10210)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys-Incorporated/teku
Published: 2025-12-09
Source: https://github.com/Consensys-Incorporated/teku/commit/ef4306f9fd251ee115fa02deeabff616e3082975
Type: security-commit

## Details
Fix TOCTOU race condition for duplicate attestations (#10210)

## Patch
### ethereum/statetransition/src/main/java/tech/pegasys/teku/statetransition/payloadattestation/PayloadAttestationMessageGossipValidator.java
```diff
@@ -85,14 +85,7 @@ public SafeFuture<InternalValidationResult> validate(
     final ValidatorIndexAndSlot key =
         new ValidatorIndexAndSlot(payloadAttestationMessage.getValidatorIndex(), data.getSlot());
     if (seenPayloadAttestations.contains(key)) {
-      LOG.trace(
-          "Payload attestation for slot {} and validator index {} already seen",
-          key.slot(),
-          key.validatorIndex());
-      return completedFuture(
-          ignore(
-              "Payload attestation for slot %s and validator index %s already seen",
-              key.slot(), key.validatorIndex()));
+      return completedFuture(ignoreAttestationAlreadySeenValidationResult(key));
     }
 
     /*
@@ -151,11 +144,26 @@ public SafeFuture<InternalValidationResult> validate(
               if (!isSignatureValid(payloadAttestationMessage, state)) {
                 return reject("Invalid payload attestation signature");
               }
-              seenPayloadAttestations.add(key);
-              return ACCEPT;
+
+              if (!seenPayloadAttestations.add(key)) {
+                return ignoreAttestationAlreadySeenValidationResult(key);
+              } else {
+                return ACCEPT;
+              }
             });
   }
 
+  private InternalValidationResult ignoreAttestationAlreadySeenValidationResult(
+      final ValidatorIndexAndSlot key) {
+    LOG.trace(
+        "Payload attestation for slot {} and validator index {} already seen",
+        key.slot(),
+        key.validatorIndex());
+    return ignore(
+        "Payload attestation for slot %s and validator index %s already seen",
+        key.slot(), key.validatorIndex());
+  }
+
   private boolean isSignatureValid(
       final PayloadAttestationMessage payloadAttestationMessage, final BeaconState state) {
     final Bytes signingRoot =
```

### ethereum/statetransition/src/test/java/tech/pegasys/teku/statetransition/payloadattestation/PayloadAttestationMessageGossipValidatorTest.java
```diff
@@ -13,6 +13,7 @@
 
 package tech.pegasys.teku.statetransition.payloadattestation;
 
+import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
 import static org.mockito.ArgumentMatchers.any;
 import static org.mockito.ArgumentMatchers.eq;
 import static org.mockito.Mockito.clearInvocations;
@@ -27,6 +28,7 @@
 import static tech.pegasys.teku.statetransition.validation.InternalValidationResult.reject;
 
 import it.unimi.dsi.fastutil.ints.IntList;
+import java.time.Duration;
 import java.util.HashMap;
 import java.util.Map;
 import java.util.Optional;
@@ -127,6 +129,31 @@ void shouldIgnore_whenAlreadySeen() {
                 slot, validatorIndex));
   }
 
+  @TestTemplate
+  void shouldIgnore_whenAlreadySeen_AfterInitialCheck() {
+    final SafeFuture<Optional<BeaconState>> getStateFuture1 = new SafeFuture<>();
+    final SafeFuture<Optional<BeaconState>> getStateFuture2 = new SafeFuture<>();
+    when(gossipValidationHelper.getStateAtSlotAndBlockRoot(any()))
+        .thenReturn(getStateFuture1)
+        .thenReturn(getStateFuture2);
+
+    final SafeFuture<InternalValidationResult> validationFuture1 =
+        payloadAttestationMessageGossipValidator.validate(payloadAttestationMessage);
+    final SafeFuture<InternalValidationResult> validationFuture2 =
+        payloadAttestationMessageGossipValidator.validate(payloadAttestationMessage);
+
+    getStateFuture1.complete(Optional.of(postState));
+    assertThat(validationFuture1).succeedsWithin(Duration.ofSeconds(10)).isEqualTo(ACCEPT);
+
+    getStateFuture2.complete(Optional.of(postState));
+    assertThat(validationFuture2)
+        .succeedsWithin(Duration.ofSeconds(10))
+        .isEqualTo(
+            ignore(
+                "Payload attestation for slot %s and validator index %s already seen",
+                slot, validatorIndex));
+  }
+
   @TestTemplate
   void shouldSaveForFuture_whenBlockNotAvailable() {
     when(gossipValidationHelper.isBlockAvailable(blockRoot)).thenReturn(false);
```
