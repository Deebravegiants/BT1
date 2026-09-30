# [?] Fixes: GHSA-23rh-rrqg-wq82 Cap BFT round change number (#11102)

## Summary
Severity: Unknown
Chain: Ethereum
Component: besu-eth/besu
Published: 2026-08-20
Source: https://github.com/besu-eth/besu/commit/118f8b1920f91dc883b9155d5226f634f75d4cff
Type: security-commit

## Details
Fixes: GHSA-23rh-rrqg-wq82 Cap BFT round change number (#11102)

Signed-off-by: Sally MacFarlane <macfarla.github@gmail.com>

## Patch
### CHANGELOG.md
```diff
@@ -68,6 +68,7 @@
 - Removed the legacy `PANTHEON_` environment variable prefix for configuration options, everyone should already use the `BESU_` prefix at this time.
 
 ### Bug fixes
+- Cap the QBFT/IBFT round change number to prevent unbounded memory growth from malformed round-change messages.
 - Cap pre-STATUS RLPx connections and close them on eviction to prevent resource exhaustion.
 - Improve logging for malformed discv4 UDP packets.
 - Bound the snap sync storage sub-range split count to prevent unbounded memory growth under a malformed snap response.
```

### consensus/ibft/src/main/java/org/hyperledger/besu/consensus/ibft/validation/RoundChangePayloadValidator.java
```diff
@@ -32,6 +32,9 @@ public class RoundChangePayloadValidator {
 
   private static final Logger LOG = LoggerFactory.getLogger(RoundChangePayloadValidator.class);
 
+  /** maximum allowed round */
+  public static final int MAX_ALLOWED_ROUND = 1000;
+
   private final MessageValidatorForHeightFactory messageValidatorFactory;
   private final Collection<Address> validators;
   private final long minimumPrepareMessages;
@@ -78,6 +81,13 @@ public boolean validateRoundChange(final SignedData<RoundChangePayload> msg) {
       return false;
     }
 
+    final int roundNumber = targetRound.getRoundNumber();
+    if (roundNumber <= 0 || roundNumber > MAX_ALLOWED_ROUND) {
+      LOG.info(
+          "Invalid RoundChange message, round number out of range [1, {}].", MAX_ALLOWED_ROUND);
+      return false;
+    }
+
     if (msg.getPayload().getPreparedCertificate().isPresent()) {
       final PreparedCertificate certificate = msg.getPayload().getPreparedCertificate().get();
 
```

### consensus/ibft/src/test/java/org/hyperledger/besu/consensus/ibft/statemachine/RoundChangeManagerTest.java
```diff
@@ -15,6 +15,7 @@
 package org.hyperledger.besu.consensus.ibft.statemachine;
 
 import static org.assertj.core.api.Assertions.assertThat;
+import static org.hyperledger.besu.consensus.ibft.validation.RoundChangePayloadValidator.MAX_ALLOWED_ROUND;
 import static org.mockito.ArgumentMatchers.any;
 import static org.mockito.Mockito.mock;
 import static org.mockito.Mockito.when;
@@ -217,6 +218,15 @@ public void stopsAcceptingMessagesAfterReady() {
     assertThat(manager.roundChangeCache.get(ri2).receivedMessages.size()).isEqualTo(2);
   }
 
+  @Test
+  public void rejectsRoundChangeMessageWithExcessiveRoundNumber() {
+    final ConsensusRoundIdentifier excessiveRound =
+        new ConsensusRoundIdentifier(2, MAX_ALLOWED_ROUND + 1);
+    final RoundChange roundChangeData = makeRoundChangeMessage(proposerKey, excessiveRound);
+    assertThat(manager.appendRoundChangeMessage(roundChangeData)).isEmpty();
+    assertThat(manager.roundChangeCache.get(excessiveRound)).isNull();
+  }
+
   @Test
   public void roundChangeMessagesWithPreparedCertificateMustHaveSufficientPrepareMessages() {
     // Specifically, prepareMessage count is ONE LESS than the calculated quorum size (as the
```

### consensus/qbft-core/src/main/java/org/hyperledger/besu/consensus/qbft/core/validation/RoundChangePayloadValidator.java
```diff
@@ -34,6 +34,9 @@ public class RoundChangePayloadValidator {
   private static final String ERROR_PREFIX = "Invalid RoundChange Payload";
   private static final Logger LOG = LoggerFactory.getLogger(RoundChangePayloadValidator.class);
 
+  /** maximum allowed round */
+  public static final int MAX_ALLOWED_ROUND = 1000;
+
   private final Collection<Address> validators;
   private final long chainHeight;
 
@@ -69,8 +72,8 @@ public boolean validate(final SignedData<RoundChangePayload> signedPayload) {
     }
 
     final int targetRound = payload.getRoundIdentifier().getRoundNumber();
-    if (targetRound <= 0) {
-      LOG.info("{}: must contain a positive target round number", ERROR_PREFIX);
+    if (targetRound <= 0 || targetRound > MAX_ALLOWED_ROUND) {
+      LOG.info("{}: target round number out of range [1, {}]", ERROR_PREFIX, MAX_ALLOWED_ROUND);
       return false;
     }
 
```

### consensus/qbft-core/src/test/java/org/hyperledger/besu/consensus/qbft/core/validation/RoundChangePayloadValidatorTest.java
```diff
@@ -15,6 +15,7 @@
 package org.hyperledger.besu.consensus.qbft.core.validation;
 
 import static org.assertj.core.api.Assertions.assertThat;
+import static org.hyperledger.besu.consensus.qbft.core.validation.RoundChangePayloadValidator.MAX_ALLOWED_ROUND;
 
 import org.hyperledger.besu.consensus.common.bft.ConsensusRoundIdentifier;
 import org.hyperledger.besu.consensus.common.bft.payload.SignedData;
@@ -148,6 +149,28 @@ public void roundChangeWithZeroTargetRoundFails() {
     assertThat(messageValidator.validate(signedPayload)).isFalse();
   }
 
+  @Test
+  public void roundChangeWithExcessiveTargetRoundFails() {
+    final RoundChangePayload payload =
+        new RoundChangePayload(
+            new ConsensusRoundIdentifier(chainHeight, MAX_ALLOWED_ROUND + 1), Optional.empty());
+
+    final SignedData<RoundChangePayload> signedPayload =
+        createSignedPayload(payload, validators.getNode(0).getNodeKey());
+    assertThat(messageValidator.validate(signedPayload)).isFalse();
+  }
+
+  @Test
+  public void roundChangeAtMaxAllowedRoundPasses() {
+    final RoundChangePayload payload =
+        new RoundChangePayload(
+            new ConsensusRoundIdentifier(chainHeight, MAX_ALLOWED_ROUND), Optional.empty());
+
+    final SignedData<RoundChangePayload> signedPayload =
+        createSignedPayload(payload, validators.getNode(0).getNodeKey());
+    assertThat(messageValidator.validate(signedPayload)).isTrue();
+  }
+
   private SignedData<RoundChangePayload> createSignedPayload(
       final RoundChangePayload payload, final NodeKey nodeKey) {
     final SECPSignature signature =
```
