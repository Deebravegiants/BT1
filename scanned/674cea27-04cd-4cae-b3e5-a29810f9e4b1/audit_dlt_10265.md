# [?] Merge branch 'feature/vertex-store-overflow-mitigations' into feature/slow-down-consensus-when-vertex-store-full

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/babylon-node
Published: 2025-02-20
Source: https://github.com/radixdlt/babylon-node/commit/68d09c364452d3ac505002f5e5c649d50412204f
Type: security-commit

## Details
Merge branch 'feature/vertex-store-overflow-mitigations' into feature/slow-down-consensus-when-vertex-store-full

## Patch
### core/src/integration/java/com/radixdlt/integration/steady_state/deterministic/consensus/DivergentExecutionLivenessBreakTest.java
```diff
@@ -73,11 +73,13 @@
 import com.radixdlt.consensus.NextEpoch;
 import com.radixdlt.consensus.bft.Round;
 import com.radixdlt.consensus.vertexstore.ExecutedVertex;
+import com.radixdlt.consensus.vertexstore.VertexStore;
 import com.radixdlt.consensus.vertexstore.VertexStoreConfig;
 import com.radixdlt.crypto.HashUtils;
 import com.radixdlt.environment.deterministic.network.MessageSelector;
 import com.radixdlt.genesis.GenesisBuilder;
 import com.radixdlt.genesis.GenesisConsensusManagerConfig;
+import com.radixdlt.harness.deterministic.DeterministicNodes;
 import com.radixdlt.harness.deterministic.DeterministicTest;
 import com.radixdlt.harness.deterministic.PhysicalNodeConfig;
 import com.radixdlt.harness.predicates.NodePredicate;
@@ -94,9 +96,9 @@
 import com.radixdlt.rev2.Decimal;
 import com.radixdlt.rev2.REV2TransactionGenerator;
 import com.radixdlt.rev2.REv2StateComputer;
-import com.radixdlt.rev2.REv2TransactionsAndProofReader;
 import com.radixdlt.transactions.RawNotarizedTransaction;
 import com.radixdlt.utils.WrappedByteArray;
+import java.util.HashSet;
 import java.util.List;
 import java.util.Random;
 import java.util.function.Consumer;
@@ -232,7 +234,7 @@ private DeterministicTest createTest() {
         .functionalNodeModule(
             new FunctionalRadixNodeModule(
                 NodeStorageConfig.tempFolder(folder),
-                true,
+                false,
                 FunctionalRadixNodeModule.SafetyRecoveryConfig.REAL,
                 INITIAL_CONSENSUS_CONFIG,
                 FunctionalRadixNodeModule.LedgerConfig.stateComputerNoSync(
@@ -255,7 +257,7 @@ public void test_divergent_execution_liveness_break_and_recovery() {
       test.startAllNodes();
       test.runUntilState(
           NodesPredicate.allNodesMatch(
-              NodePredicate.atOrOverRound(LIVENESS_BREAK_START_ROUND.previous())));
+              NodePredicate.nonEpochedBftAtOrOverRound(LIVENESS_BREAK_START_ROUND.previous())));
 
       verifyMetricsOnAllNodes(
           test,
@@ -274,38 +276,18 @@ public void test_divergent_execution_liveness_break_and_recovery() {
           });
 
       // Phase 2: Liveness break
-      // Run until we observe that vertex store hits its size limit
-      // 100 occurrences is chosen arbitrarily, just to make sure that the issue is not transient
-      test.runUntilState(
-          NodesPredicate.allNodesMatch(
-              NodePredicate.metricsPredicate(
-                  metrics -> metrics.bft().vertexStore().errorsDueToSizeLimit().get() > 100)));
-
-      verifyMetricsOnAllNodes(
-          test,
-          metrics -> {
-            // Verify that the cause is what we expect: a divergent execution
-            assertTrue(metrics.bft().divergentVertexExecutions().getSum() > 1);
-            // Cross-check another metric to verify that vertex store
-            // indeed holds more vertices than expected in a healthy scenario.
-            assertTrue(metrics.bft().vertexStore().vertexCount().get() >= 20);
-          });
-
-      // Another verification that we're in a liveness break
-      final var stateVersionA =
-          test.getInstance(0, REv2TransactionsAndProofReader.class)
-              .getLatestProofBundle()
-              .orElseThrow()
-              .primaryProof()
-              .stateVersion();
-      test.runForCount(1000);
-      final var stateVersionB =
-          test.getInstance(0, REv2TransactionsAndProofReader.class)
-              .getLatestProofBundle()
-              .orElseThrow()
-              .primaryProof()
-              .stateVersion();
-      assertEquals(stateVersionA, stateVersionB);
+      // Run until we observe that vertex store hits its size limit on all nodes
+      // (VertexStoreSizeExceededException)
+      HashSet<Integer> crashedNodes = new HashSet<>();
+      while (crashedNodes.size() != NUM_VALIDATORS) {
+        try {
+          test.runForCount(1);
+        } catch (DeterministicNodes.EventHandleException e) {
+          if (e.getCause() instanceof VertexStore.VertexStoreSizeExceededException) {
+            crashedNodes.add(e.getControlledMessage().channelId().receiverIndex());
+          }
+        }
+      }
 
       // Phase 3: Recovery
       for (var i = 0; i < test.numNodes(); i++) {
```

### core/src/integration/java/com/radixdlt/integration/targeted/rev2/recovery/RecoveryAfterTimeoutQuorumTest.java
```diff
@@ -135,7 +135,9 @@ public void recovery_after_timeout_quorum_test() {
 
       // Run until the round that's expected to form a timeout quorum
       test.runUntilState(
-          NodesPredicate.allNodesMatch(NodePredicate.bftAtOrOverRound(TIMEOUT_QUORUM_ROUND)), 1000);
+          NodesPredicate.allNodesMatch(
+              NodePredicate.nonEpochedBftAtOrOverRound(TIMEOUT_QUORUM_ROUND)),
+          1000);
 
       // Make sure that round was indeed due to a timeout quorum
       for (var node : test.getNodeInjectors()) {
@@ -177,15 +179,17 @@ public void recovery_after_timeout_quorum_test() {
       for (var i = 0; i < NUM_VALIDATORS; i++) {
         if (i != LEADER_INDEX_AT_TIMEOUT_ROUND) {
           test.runUntilState(
-              NodesPredicate.nodeAt(i, NodePredicate.bftAtOrOverRound(Round.of(10))), 1000);
+              NodesPredicate.nodeAt(i, NodePredicate.nonEpochedBftAtOrOverRound(Round.of(10))),
+              1000);
         }
       }
 
       // The leader for the timeout round, once started, should catch up too
       test.startNode(LEADER_INDEX_AT_TIMEOUT_ROUND);
       test.runUntilState(
           NodesPredicate.nodeAt(
-              LEADER_INDEX_AT_TIMEOUT_ROUND, NodePredicate.bftAtOrOverRound(Round.of(10))),
+              LEADER_INDEX_AT_TIMEOUT_ROUND,
+              NodePredicate.nonEpochedBftAtOrOverRound(Round.of(10))),
           1000);
     }
   }
```

### core/src/main/java/com/radixdlt/consensus/BFTConfiguration.java
```diff
@@ -73,15 +73,15 @@
 public final class BFTConfiguration {
   private final ProposerElection proposerElection;
   private final BFTValidatorSet validatorSet;
-  private final VertexStoreState vertexStoreState;
+  private final VertexStoreState initialVertexStoreState;
 
   public BFTConfiguration(
       ProposerElection proposerElection,
       BFTValidatorSet validatorSet,
       VertexStoreState vertexStoreState) {
     this.proposerElection = Objects.requireNonNull(proposerElection);
     this.validatorSet = Objects.requireNonNull(validatorSet);
-    this.vertexStoreState = Objects.requireNonNull(vertexStoreState);
+    this.initialVertexStoreState = Objects.requireNonNull(vertexStoreState);
   }
 
   public ProposerElection getProposerElection() {
@@ -93,20 +93,20 @@ public BFTValidatorSet getValidatorSet() {
   }
 
   public VertexStoreState getVertexStoreState() {
-    return vertexStoreState;
+    return initialVertexStoreState;
   }
 
   @Override
   public int hashCode() {
-    return Objects.hash(this.proposerElection, this.validatorSet, this.vertexStoreState);
+    return Objects.hash(this.proposerElection, this.validatorSet, this.initialVertexStoreState);
   }
 
   @Override
   public boolean equals(Object obj) {
     if (obj instanceof BFTConfiguration) {
       BFTConfiguration that = (BFTConfiguration) obj;
       return Objects.equals(this.validatorSet, that.validatorSet)
-          && Objects.equals(this.vertexStoreState, that.vertexStoreState)
+          && Objects.equals(this.initialVertexStoreState, that.initialVertexStoreState)
           && Objects.equals(this.proposerElection, that.proposerElection);
     }
     return false;
@@ -115,7 +115,7 @@ public boolean equals(Object obj) {
   @Override
   public String toString() {
     return String.format(
-        "%s[validatorSet=%s, vertexStoreState=%s]",
-        getClass().getSimpleName(), this.validatorSet, this.vertexStoreState);
+        "%s[validatorSet=%s, initialVertexStoreState=%s]",
+        getClass().getSimpleName(), this.validatorSet, this.initialVertexStoreState);
   }
 }
```

### core/src/main/java/com/radixdlt/consensus/VertexWithHash.java
```diff
@@ -98,14 +98,13 @@ public HashCode hash() {
 
   @Override
   public int hashCode() {
-    return Objects.hash(this.vertex, this.vertexHash);
+    return Objects.hash(this.vertexHash);
   }
 
   @Override
   public boolean equals(Object o) {
     if (o instanceof final VertexWithHash that) {
-      return Objects.equals(this.vertexHash, that.vertexHash)
-          && Objects.equals(this.vertex, that.vertex);
+      return Objects.equals(this.vertexHash, that.vertexHash);
     }
     return false;
   }
```

### core/src/main/java/com/radixdlt/consensus/bft/processor/SyncUpPreprocessor.java
```diff
@@ -168,7 +168,7 @@ public void processBFTUpdate(BFTInsertUpdate update) {
   public void processBFTRebuildUpdate(BFTRebuildUpdate rebuildUpdate) {
     rebuildUpdate
         .vertexStoreState()
-        .getVertices()
+        .getNonRootVertices()
         .forEach(
             v -> {
               HashCode vertexId = v.hash();
```

### core/src/main/java/com/radixdlt/consensus/epoch/EpochsConsensusModule.java
```diff
@@ -463,10 +463,10 @@ private VertexStoreFactory vertexStoreFactory(
       Serialization serialization,
       Metrics metrics,
       VertexStoreConfig vertexStoreConfig) {
-    return vertexStoreState ->
+    return initialVertexStoreState ->
         new VertexStoreAdapter(
             new VertexStoreJavaImpl(
-                ledger, hasher, serialization, metrics, vertexStoreConfig, vertexStoreState),
+                ledger, hasher, serialization, metrics, vertexStoreConfig, initialVertexStoreState),
             highQCUpdateEventDispatcher,
             updateSender,
             rebuildUpdateDispatcher);
```

### core/src/main/java/com/radixdlt/consensus/liveness/MultiFactorPacemakerTimeoutCalculator.java
```diff
@@ -64,17 +64,27 @@
 
 package com.radixdlt.consensus.liveness;
 
-import com.google.common.math.LinearTransformation;
 import com.google.common.primitives.Doubles;
+import com.google.common.util.concurrent.RateLimiter;
 import com.google.inject.Inject;
+import org.apache.logging.log4j.LogManager;
+import org.apache.logging.log4j.Logger;
 
 /**
- * Main timeout calculator implementation, which uses two factors to calculate the timeout: - the
- * number of consecutive timeout occurrences - and the current capacity of the vertex store
+ * Main timeout calculator implementation, which uses two factors to calculate the timeout:
+ *
+ * <ol>
+ *   <li>- the number of consecutive timeout occurrences
+ *   <li>- and the current capacity of the vertex store
  */
 public final class MultiFactorPacemakerTimeoutCalculator implements PacemakerTimeoutCalculator {
+  private static final Logger logger = LogManager.getLogger();
+
   private final PacemakerTimeoutCalculatorConfig config;
 
+  private final RateLimiter logRatelimiter =
+      RateLimiter.create(0.016); // At most one log every ~minute
+
   @Inject
   public MultiFactorPacemakerTimeoutCalculator(PacemakerTimeoutCalculatorConfig config) {
     this.config = config;
@@ -92,23 +102,52 @@ public long calculateTimeoutMs(long timeoutOccurrences, double vertexStoreUtiliz
     final var vertexStoreUtilizationRatioClamped =
         Doubles.constrainToRange(vertexStoreUtilizationRatio, 0, 1);
 
-    // We're linearly transforming the current utilization
-    // from [threshold, 1] to [1, maxExponent] to get the exponent
-    // for the vertex store utilization factor.
-    // Values below the threshold are mapped to an exponent of 0
-    // and don't contribute to the overall timeout.
-    final var vertexStoreUtilizationFactorExponent =
-        Math.max(
-            0,
-            LinearTransformation.mapping(config.vertexStoreUtilizationFactorThreshold(), 1.0)
-                .and(1.0, config.vertexStoreUtilizationFactorMaxExponent())
-                .transform(vertexStoreUtilizationRatioClamped));
+    final double vertexStoreUtilizationFactor;
+    if (vertexStoreUtilizationRatioClamped <= config.vertexStoreUtilizationFactorThreshold()) {
+      vertexStoreUtilizationFactor = 1;
+    } else {
+      // We're linearly transforming the current utilization
+      // from [threshold, 1] to [1, maxExponent] to get the exponent
+      // for the vertex store utilization factor.
+      final var exponent =
+          lerp(
+              config.vertexStoreUtilizationFactorThreshold(),
+              1.0,
+              0.0,
+              config.vertexStoreUtilizationFactorMaxExponent(),
+              vertexStoreUtilizationRatioClamped);
+      vertexStoreUtilizationFactor = Math.pow(config.vertexStoreUtilizationFactorRate(), exponent);
+    }
 
-    final var vertexStoreUtilizationFactor =
-        Math.pow(config.vertexStoreUtilizationFactorRate(), vertexStoreUtilizationFactorExponent);
+    final var res =
+        Math.round(
+            config.baseTimeoutMs() * consecutiveTimeoutFactor * vertexStoreUtilizationFactor);
+
+    if (vertexStoreUtilizationRatioClamped >= config.vertexStoreUtilizationFactorThreshold()
+        && logRatelimiter.tryAcquire()) {
+      logger.warn(
+          "Vertex store is currently at {} of its maximum byte capacity. Consensus timeouts are"
+              + " being slowed down to slow down pressure accumulation on the vertex store."
+              + " [base_timeout ({} ms) * consecutive_timeout_factor ({}) *"
+              + " vertex_store_utilization_factor ({}) = resultant_timeout ({} ms)]",
+          vertexStoreUtilizationRatioClamped,
+          config.baseTimeoutMs(),
+          consecutiveTimeoutFactor,
+          vertexStoreUtilizationFactor,
+          res);
+    }
+
+    return res;
+  }
 
-    return Math.round(
-        config.baseTimeoutMs() * consecutiveTimeoutFactor * vertexStoreUtilizationFactor);
+  // Computes a linear interpolation (or extrapolation).
+  // The input value `z` is interpolated from the source range [x, y]
+  // to the target range [p, q].
+  // E.g. if [x, y] = [10, 20], z = 15 and [p, q] = [0, 1], returns 0.5.
+  // If z is outside [x, y] then it's extrapolated (linearly) and can produce
+  // a value outside [p, q]. This should be handled by the caller.
+  private static double lerp(double x, double y, double p, double q, double z) {
+    return p + (q - p) * (z - x) / (y - x);
   }
 
   @Override
```

### core/src/main/java/com/radixdlt/consensus/vertexstore/VertexStore.java
```diff
@@ -163,4 +163,6 @@ enum RebuildError {
    * between 0 and 1 (both inclusive). In practice the size is always above 0.
    */
   double getCurrentUtilizationRatio();
+
+  class VertexStoreSizeExceededException extends RuntimeException {}
 }
```

### core/src/main/java/com/radixdlt/consensus/vertexstore/VertexStoreAdapter.java
```diff
@@ -141,7 +141,8 @@ public VertexStore.InsertQcResult insertQuorumCertificate(QuorumCertificate qc)
               inserted.newHighQc(),
               inserted.committedUpdate().map(VertexStore.CommittedUpdate::committedVertices),
               inserted.serializedVertexStoreState()));
-      default -> {} // no-op
+      case VertexStore.InsertQcResult.Ignored ignored -> {} // No-op
+      case VertexStore.InsertQcResult.VertexIsMissing ignored -> {} // No-op
     }
     return result;
   }
```

### core/src/main/java/com/radixdlt/consensus/vertexstore/VertexStoreJavaImpl.java
```diff
@@ -138,7 +138,7 @@ private void resetToState(VertexStoreState state) {
     this.executedVertices.clear();
     this.vertexChildren.clear();
 
-    for (var vertexWithHash : state.getVertices()) {
+    for (var vertexWithHash : state.getNonRootVertices()) {
       this.vertices.put(vertexWithHash.hash(), vertexWithHash);
       this.vertexChildren.put(vertexWithHash.vertex().getParentVertexId(), vertexWithHash.hash());
     }
@@ -159,7 +159,7 @@ public Result<RebuildSummary, RebuildError> tryRebuild(VertexStoreState vertexSt
     // FIXME: Currently this assumes vertexStoreState is a chain with no forks which is our only use
     // case at the moment.
     var executedVertices = new LinkedList<ExecutedVertex>();
-    for (VertexWithHash vertex : vertexStoreState.getVertices()) {
+    for (VertexWithHash vertex : vertexStoreState.getNonRootVertices()) {
       var executedVertexMaybe = ledger.prepare(executedVertices, vertex);
 
       // If any vertex couldn't be executed successfully, our saved state is invalid
@@ -179,7 +179,7 @@ public Result<RebuildSummary, RebuildError> tryRebuild(VertexStoreState vertexSt
       this.executedVertices.put(executedVertex.getVertexHash(), executedVertex);
     }
 
-    metrics.bft().vertexStore().vertexCount().set(vertexStoreState.getVertices().size());
+    metrics.bft().vertexStore().vertexCount().set(vertexStoreState.getNonRootVertices().size());
     metrics.bft().vertexStore().rebuilds().inc();
 
     return Result.success(new RebuildSummary(vertexStoreState, serializedVertexStoreState));
@@ -188,13 +188,13 @@ public Result<RebuildSummary, RebuildError> tryRebuild(VertexStoreState vertexSt
   @Override
   public InsertQcResult insertQc(QuorumCertificate qc) {
     if (!this.containsVertex(qc.getProposedHeader().getVertexId())) {
-      return new VertexStore.InsertQcResult.VertexIsMissing();
+      return new InsertQcResult.VertexIsMissing();
     }
 
     final var hasAnyChildren = vertexChildren.containsKey(qc.getProposedHeader().getVertexId());
     if (hasAnyChildren) {
       // TODO: Check to see if qc's match in case there's a fault
-      return new VertexStore.InsertQcResult.Ignored();
+      return new InsertQcResult.Ignored();
     }
 
     // Proposed vertex doesn't have any children
@@ -218,17 +218,14 @@ public InsertQcResult insertQc(QuorumCertificate qc) {
       committedUpdate = Option.empty();
     }
 
-    metrics.bft().vertexStore().vertexCount().set(vertices.size());
-
     if (isHighQC || committedUpdate.isPresent()) {
       // We have either received a new highQc, or some vertices were committed, or both.
       final var serializedVertexStoreState = recordHighQcOrVertexChange();
 
-      return new VertexStore.InsertQcResult.Inserted(
-          highQC(), serializedVertexStoreState, committedUpdate);
+      return new InsertQcResult.Inserted(highQC(), serializedVertexStoreState, committedUpdate);
     } else {
       // This wasn't our new high QC and nothing has been committed
-      return new VertexStore.InsertQcResult.Ignored();
+      return new InsertQcResult.Ignored();
     }
   }
 
@@ -341,13 +338,22 @@ public InsertVertexChainResult insertVertexChain(VertexChain vertexChain) {
         bftInsertUpdates.add(insertRes.unwrap());
       } else {
         switch (insertRes.unwrapError()) {
-          case ALREADY_PRESENT, PREPARE_FAILED -> {
+          case ALREADY_PRESENT -> {
             // No-op, continue iterating the vertices
           }
-          case VERTEX_STORE_SIZE_EXCEEDED -> {
-            // Stop if we hit the size limit
+          case PREPARE_FAILED -> {
+            logger.warn(
+                "Failed to insert vertex chain: prepare failed for {} (successfully inserted {} QCs"
+                    + " and {} vertices)",
+                v,
+                insertedQcs.size(),
+                bftInsertUpdates.size());
             break vertices_loop;
           }
+          case VERTEX_STORE_SIZE_EXCEEDED -> {
+            logVertexStoreSizeExceededError();
+            throw new VertexStoreSizeExceededException();
+          }
         }
       }
     }
@@ -357,7 +363,28 @@ public InsertVertexChainResult insertVertexChain(VertexChain vertexChain) {
 
   @Override
   public Option<BFTInsertUpdate> insertVertex(VertexWithHash vertexWithHash) {
-    return insertVertexInternal(vertexWithHash).toOption();
+    return switch (insertVertexInternal(vertexWithHash)) {
+      case Result.Success<BFTInsertUpdate, VertexInsertError> v -> Option.some(v.value());
+      case Result.Error<BFTInsertUpdate, VertexInsertError> v -> switch (v.error()) {
+        case ALREADY_PRESENT -> Option.none();
+        case PREPARE_FAILED -> Option.none();
+        case VERTEX_STORE_SIZE_EXCEEDED -> {
+          logVertexStoreSizeExceededError();
+          throw new VertexStoreSizeExceededException();
+        }
+      };
+    };
+  }
+
+  private void logVertexStoreSizeExceededError() {
+    logger.error(
+        "Vertex store has reached its maximum capacity of {} bytes (serialized). This indicates"
+            + " likely consensus issues. Please check the official Radix communication channels"
+            + " (Discord) for more information. The limit can be overridden using the"
+            + " `bft.vertex_store.max_serialized_size_bytes` config (bound to"
+            + " `RADIXDLT_BFT_VERTEX_STORE_MAX_SERIALIZED_SIZE_BYTES` env var), but it should never"
+            + " exceed ~250 MiB, which is right below SBOR limits.",
+        config.maxSerializedSizeBytes());
   }
 
   private Result<BFTInsertUpdate, VertexInsertError> insertVertexInternal(
@@ -461,16 +488,16 @@ public boolean containsVertex(HashCode vertexId) {
   private VertexStoreState getState() {
     // TODO: store list dynamically rather than recomputing
     ImmutableSet.Builder<VertexWithHash> verticesBuilder = ImmutableSet.builder();
-    getChildrenVerticesList(this.rootVertex, verticesBuilder);
+    addChildrenRecursive(this.rootVertex, verticesBuilder);
     return VertexStoreState.create(this.highQC(), this.rootVertex, verticesBuilder.build(), hasher);
   }
 
-  private void getChildrenVerticesList(
+  private void addChildrenRecursive(
       VertexWithHash parent, ImmutableSet.Builder<VertexWithHash> builder) {
     for (HashCode child : this.vertexChildren.get(parent.hash())) {
       final var v = vertices.get(child);
       builder.add(v);
-      getChildrenVerticesList(v, builder);
+      addChildrenRecursive(v, builder);
     }
   }
 
```

### core/src/main/java/com/radixdlt/consensus/vertexstore/VertexStoreState.java
```diff
@@ -95,13 +95,13 @@ public final class VertexStoreState {
 
   private final VertexWithHash root;
   private final HighQC highQC;
-  private final ImmutableSet<VertexWithHash> vertices;
+  private final ImmutableSet<VertexWithHash> nonRootVertices;
 
   private VertexStoreState(
-      HighQC highQC, VertexWithHash root, ImmutableSet<VertexWithHash> vertices) {
+      HighQC highQC, VertexWithHash root, ImmutableSet<VertexWithHash> nonRootVertices) {
     this.highQC = highQC;
     this.root = root;
-    this.vertices = vertices;
+    this.nonRootVertices = nonRootVertices;
   }
 
   public static VertexStoreState createNewForNextEpoch(
@@ -128,7 +128,10 @@ public static VertexStoreState create(HighQC highQC, VertexWithHash root, Hasher
   }
 
   public static VertexStoreState create(
-      HighQC highQC, VertexWithHash root, ImmutableSet<VertexWithHash> vertices, Hasher hasher) {
+      HighQC highQC,
+      VertexWithHash root,
+      ImmutableSet<VertexWithHash> nonRootVertices,
+      Hasher hasher) {
     final var processedQcCommit =
         highQC
             .highestCommittedQC()
@@ -146,12 +149,13 @@ public static VertexStoreState create(
     var seen = new HashMap<HashCode, VertexWithHash>();
     seen.put(root.hash(), root);
 
-    for (var vertexWithHash : vertices) {
+    for (var vertexWithHash : nonRootVertices) {
       final var vertex = vertexWithHash.vertex();
       if (!seen.containsKey(vertex.getParentVertexId())) {
         throw new IllegalStateException(
             String.format(
-                "Missing qc=%s {root=%s vertices=%s}", vertex.getQCToParent(), root, vertices));
+                "Missing qc=%s {root=%s vertices=%s}",
+                vertex.getQCToParent(), root, nonRootVertices));
       }
       seen.put(vertexWithHash.hash(), vertexWithHash);
     }
@@ -163,7 +167,7 @@ public static VertexStoreState create(
       logger.warn(
           String.format(
               "highQC=%s highCommitted proposed missing {root=%s vertices=%s}",
-              highQC, root, vertices));
+              highQC, root, nonRootVertices));
       /*
       throw new IllegalStateException(
           String.format(
@@ -210,21 +214,14 @@ public static VertexStoreState create(
        */
     }
 
-    return new VertexStoreState(highQC, root, vertices);
-  }
-
-  public VertexStoreState withVertex(VertexWithHash vertex) {
-    return new VertexStoreState(
-        this.highQC,
-        this.root,
-        ImmutableSet.<VertexWithHash>builder().addAll(this.vertices).add(vertex).build());
+    return new VertexStoreState(highQC, root, nonRootVertices);
   }
 
   public SerializableVertexStoreState toSerializable() {
     return new SerializableVertexStoreState(
         this.highQC,
         this.root.vertex(),
-        this.vertices.stream()
+        this.nonRootVertices.stream()
             .map(VertexWithHash::vertex)
             .collect(ImmutableList.toImmutableList()));
   }
@@ -237,13 +234,13 @@ public VertexWithHash getRoot() {
     return root;
   }
 
-  public ImmutableSet<VertexWithHash> getVertices() {
-    return vertices;
+  public ImmutableSet<VertexWithHash> getNonRootVertices() {
+    return nonRootVertices;
   }
 
   @Override
   public int hashCode() {
-    return Objects.hash(root, highQC, vertices);
+    return Objects.hash(root, highQC, nonRootVertices);
   }
 
   @Override
@@ -255,7 +252,7 @@ public boolean equals(Object o) {
     return o instanceof VertexStoreState other
         && Objects.equals(this.root, other.root)
         && Objects.equals(this.highQC, other.highQC)
-        && Objects.equals(this.vertices, other.vertices);
+        && Objects.equals(this.nonRootVertices, other.nonRootVertices);
   }
 
   @Override
@@ -266,7 +263,7 @@ public String toString() {
         + ", highQC="
         + highQC
         + ", vertices="
-        + vertices
+        + nonRootVertices
         + '}';
   }
 
```

### core/src/test-core/java/com/radixdlt/harness/deterministic/DeterministicNodes.java
```diff
@@ -268,6 +268,10 @@ public static class EventHandleException extends RuntimeException {
       super("Exception: " + e + "\nOn message: " + message.toString(), e);
       this.message = message;
     }
+
+    public ControlledMessage getControlledMessage() {
+      return message;
+    }
   }
 
   public void startNode(int nodeIndex, long time) {
```
