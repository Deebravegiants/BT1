# [?] [Issue 2037] Limit hot blocks in memory (with race condition fix) (#2271)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys-Incorporated/teku
Published: 2020-07-01
Source: https://github.com/Consensys-Incorporated/teku/commit/68f9af79ee2cbe1ac0eee5b443cd3c93de423d9e
Type: security-commit

## Details
[Issue 2037] Limit hot blocks in memory (with race condition fix) (#2271)

## Patch
### ethereum/core/src/main/java/tech/pegasys/teku/core/StateGenerator.java
```diff
@@ -1,222 +0,0 @@
-/*
- * Copyright 2020 ConsenSys AG.
- *
- * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
- * the License. You may obtain a copy of the License at
- *
- * http://www.apache.org/licenses/LICENSE-2.0
- *
- * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
- * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
- * specific language governing permissions and limitations under the License.
- */
-
-package tech.pegasys.teku.core;
-
-import static com.google.common.base.Preconditions.checkArgument;
-
-import java.util.ArrayDeque;
-import java.util.ArrayList;
-import java.util.Collections;
-import java.util.Deque;
-import java.util.HashMap;
-import java.util.List;
-import java.util.Map;
-import java.util.Optional;
-import java.util.function.Function;
-import org.apache.tuweni.bytes.Bytes32;
-import tech.pegasys.teku.core.blockvalidator.NopBlockValidator;
-import tech.pegasys.teku.datastructures.blocks.BlockTree;
-import tech.pegasys.teku.datastructures.blocks.SignedBeaconBlock;
-import tech.pegasys.teku.datastructures.state.BeaconState;
-import tech.pegasys.teku.util.collections.LimitStrategy;
-import tech.pegasys.teku.util.collections.LimitedMap;
-
-/** Utility for regenerating block states given a block tree and a root state. */
-public class StateGenerator {
-  private static final int DEFAULT_STATE_CACHE_SIZE = 50;
-
-  private final BlockTree blockTree;
-  private final Map<Bytes32, BeaconState> knownStates = new HashMap<>();
-
-  private StateGenerator(
-      final BlockTree blockTree,
-      final BeaconState rootState,
-      final Map<Bytes32, BeaconState> knownStates) {
-    final SignedBeaconBlock rootBlock = blockTree.getRootBlock();
-    checkArgument(
-        rootBlock.getStateRoot().equals(rootState.hash_tree_root()),
-        "Root state must match the root block of the blockTree");
-    this.blockTree = blockTree;
-    this.knownStates.putAll(knownStates);
-    this.knownStates.put(rootBlock.getRoot(), rootState);
-  }
-
-  public static StateGenerator create(final BlockTree blockTree, final BeaconState rootState) {
-    return new StateGenerator(blockTree, rootState, Collections.emptyMap());
-  }
-
-  public static StateGenerator create(
-      final BlockTree blockTree,
-      final BeaconState rootState,
-      final Map<Bytes32, BeaconState> knownStates) {
-    return new StateGenerator(blockTree, rootState, knownStates);
-  }
-
-  /**
-   * Regenerate a state for a single block.
-   *
-   * @param blockRoot The root of the block
-   * @return
-   */
-  public BeaconState regenerateStateForBlock(final Bytes32 blockRoot) {
-    return regenerateStateForBlock(blockRoot, new StateCache(0, knownStates));
-  }
-
-  private BeaconState regenerateStateForBlock(
-      final Bytes32 blockRoot, final StateCache stateCache) {
-    final Optional<BeaconState> knownState = stateCache.get(blockRoot);
-    if (knownState.isPresent()) {
-      return knownState.get();
-    }
-
-    // Walk from target block towards root of the tree, stopping when we find an available state
-    final List<SignedBeaconBlock> blocks = new ArrayList<>();
-    Optional<SignedBeaconBlock> curBlock = blockTree.getBlock(blockRoot);
-    Optional<BeaconState> baseState = Optional.empty();
-    while (curBlock.isPresent()) {
-      final Bytes32 root = curBlock.get().getRoot();
-      baseState = stateCache.get(root);
-      if (baseState.isPresent()) {
-        break;
-      }
-      blocks.add(curBlock.get());
-      curBlock = blockTree.getBlock(curBlock.get().getParent_root());
-    }
-    checkArgument(
-        blocks.size() > 0,
-        "Block %s does not belong to this %s.",
-        blockRoot,
-        getClass().getSimpleName());
-
-    // Process blocks in order
-    BeaconState state = baseState.orElseThrow();
-    SignedBeaconBlock block = null;
-    for (int i = blocks.size() - 1; i >= 0; i--) {
-      block = blocks.get(i);
-      state = processBlock(state, block);
-    }
-
-    // Validate result and return
-    if (!block.getStateRoot().equals(state.hash_tree_root())) {
-      final String msg =
-          String.format(
-              "Failed to regenerate state for block root %s.  Generated state root %s does not match expected state root %s",
-              blockRoot, state.hash_tree_root(), block.getStateRoot());
-      throw new IllegalStateException(msg);
-    }
-    return state;
-  }
-
-  /**
-   * Regenerate all states in the block tree.
-   *
-   * @param stateHandler A handler to process each state as it is generated.
-   */
-  public void regenerateAllStates(final StateHandler stateHandler) {
-    regenerateAllStates(stateHandler, DEFAULT_STATE_CACHE_SIZE);
-  }
-
-  void regenerateAllStates(final StateHandler stateHandler, final int maxCachedStates) {
-    final StateCache stateCache = new StateCache(maxCachedStates, knownStates);
-
-    final Deque<SignedBeaconBlock> branchesToProcess = new ArrayDeque<>();
-    final SignedBeaconBlock rootBlock = blockTree.getRootBlock();
-    blockTree.getChildren(rootBlock).forEach(branchesToProcess::push);
-
-    while (!branchesToProcess.isEmpty()) {
-      SignedBeaconBlock branchBlock = branchesToProcess.pop();
-      BeaconState preState =
-          stateCache.getOrGenerate(
-              branchBlock.getParent_root(), root -> regenerateStateForBlock(root, stateCache));
-      while (branchBlock != null) {
-        // Produce state for the current branch block
-        final BeaconState state = preState;
-        final SignedBeaconBlock block = branchBlock;
-        final BeaconState branchBlockState =
-            stateCache.get(branchBlock.getRoot()).orElseGet(() -> processBlock(state, block));
-        stateHandler.handle(branchBlock.getRoot(), branchBlockState);
-
-        // Process children
-        final List<SignedBeaconBlock> children =
-            new ArrayList<>(blockTree.getChildren(branchBlock.getRoot()));
-        // Save branches for later processing
-        if (children.size() > 1) {
-          // Only cache the current state if there are other branches we need to come back to later
-          stateCache.put(branchBlock.getRoot(), branchBlockState);
-          children.subList(1, children.size()).forEach(branchesToProcess::push);
-        }
-        // Continue processing the first child
-        branchBlock = children.isEmpty() ? null : children.get(0);
-        preState = branchBlockState;
-      }
-    }
-  }
-
-  private BeaconState processBlock(final BeaconState preState, final SignedBeaconBlock block) {
-    StateTransition stateTransition = new StateTransition(new NopBlockValidator());
-    try {
-      final BeaconState postState = stateTransition.initiate(preState, block);
-      // Validate that state matches expectation
-      if (!block.getMessage().getState_root().equals(postState.hash_tree_root())) {
-        throw new IllegalStateException(getFailedStateGenerationError(block));
-      }
-      return postState;
-    } catch (StateTransitionException e) {
-      throw new IllegalStateException(getFailedStateGenerationError(block), e);
-    }
-  }
-
-  private String getFailedStateGenerationError(final SignedBeaconBlock block) {
-    return String.format(
-        "Unable to produce state for block at slot %s (%s)", block.getSlot(), block.getRoot());
-  }
-
-  public interface StateHandler {
-    void handle(final Bytes32 blockRoot, final BeaconState state);
-  }
-
-  private static class StateCache {
-    private final Map<Bytes32, BeaconState> cache;
-    private final Map<Bytes32, BeaconState> knownStates;
-
-    public StateCache(final int maxCachedStates, final Map<Bytes32, BeaconState> knownStates) {
-      this.cache = LimitedMap.create(maxCachedStates, LimitStrategy.DROP_LEAST_RECENTLY_ACCESSED);
-      this.knownStates = knownStates;
-    }
-
-    /**
-     * Get the state or generate and cache it.
-     *
-     * @param blockRoot The block root the state corresponds to
-     * @param stateSupplier A state generator that will be invoked if the state isn't found
-     * @return
-     */
-    public BeaconState getOrGenerate(
-        final Bytes32 blockRoot, Function<Bytes32, BeaconState> stateSupplier) {
-      return Optional.ofNullable(knownStates.get(blockRoot))
-          .orElseGet(() -> cache.computeIfAbsent(blockRoot, stateSupplier));
-    }
-
-    public Optional<BeaconState> get(final Bytes32 blockRoot) {
-      return Optional.ofNullable(knownStates.get(blockRoot))
-          .or(() -> Optional.ofNullable(cache.get(blockRoot)));
-    }
-
-    public void put(final Bytes32 blockRoot, final BeaconState state) {
-      if (!knownStates.containsKey(blockRoot)) {
-        cache.put(blockRoot, state);
-      }
-    }
-  }
-}
```

### ethereum/core/src/main/java/tech/pegasys/teku/core/lookup/BlockProvider.java
```diff
@@ -0,0 +1,98 @@
+/*
+ * Copyright 2020 ConsenSys AG.
+ *
+ * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
+ * the License. You may obtain a copy of the License at
+ *
+ * http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
+ * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
+ * specific language governing permissions and limitations under the License.
+ */
+
+package tech.pegasys.teku.core.lookup;
+
+import com.google.common.collect.Sets;
+import java.util.Collections;
+import java.util.HashSet;
+import java.util.List;
+import java.util.Map;
+import java.util.Objects;
+import java.util.Optional;
+import java.util.Set;
+import java.util.function.Function;
+import java.util.function.Supplier;
+import java.util.stream.Collectors;
+import org.apache.tuweni.bytes.Bytes32;
+import tech.pegasys.teku.datastructures.blocks.SignedBeaconBlock;
+import tech.pegasys.teku.util.async.SafeFuture;
+
+@FunctionalInterface
+public interface BlockProvider {
+
+  BlockProvider NOOP = (roots) -> SafeFuture.completedFuture(Collections.emptyMap());
+
+  static BlockProvider fromDynamicMap(Supplier<Map<Bytes32, SignedBeaconBlock>> mapSupplier) {
+    return (roots) -> fromMap(mapSupplier.get()).getBlocks(roots);
+  }
+
+  static BlockProvider fromMap(final Map<Bytes32, SignedBeaconBlock> blockMap) {
+    return (roots) ->
+        SafeFuture.completedFuture(
+            roots.stream()
+                .map(blockMap::get)
+                .filter(Objects::nonNull)
+                .collect(Collectors.toMap(SignedBeaconBlock::getRoot, Function.identity())));
+  }
+
+  static BlockProvider fromList(final List<SignedBeaconBlock> blockAndStates) {
+    final Map<Bytes32, SignedBeaconBlock> blocks =
+        blockAndStates.stream()
+            .collect(Collectors.toMap(SignedBeaconBlock::getRoot, Function.identity()));
+
+    return fromMap(blocks);
+  }
+
+  static BlockProvider withKnownBlocks(
+      final BlockProvider blockProvider, final Map<Bytes32, SignedBeaconBlock> knownBlocks) {
+    return combined(fromMap(knownBlocks), blockProvider);
+  }
+
+  static BlockProvider combined(
+      final BlockProvider primaryProvider, final BlockProvider... secondaryProviders) {
+
+    return (final Set<Bytes32> blockRoots) -> {
+      SafeFuture<Map<Bytes32, SignedBeaconBlock>> result = primaryProvider.getBlocks(blockRoots);
+      for (BlockProvider nextProvider : secondaryProviders) {
+        result =
+            result.thenCompose(
+                blocks -> {
+                  final Set<Bytes32> remainingRoots = Sets.difference(blockRoots, blocks.keySet());
+                  if (remainingRoots.isEmpty()) {
+                    return SafeFuture.completedFuture(blocks);
+                  }
+                  return nextProvider
+                      .getBlocks(remainingRoots)
+                      .thenApply(
+                          moreBlocks -> {
+                            blocks.putAll(moreBlocks);
+                            return blocks;
+                          });
+                });
+      }
+      return result;
+    };
+  }
+
+  SafeFuture<Map<Bytes32, SignedBeaconBlock>> getBlocks(final Set<Bytes32> blockRoots);
+
+  default SafeFuture<Map<Bytes32, SignedBeaconBlock>> getBlocks(final List<Bytes32> blockRoots) {
+    return getBlocks(new HashSet<>(blockRoots));
+  }
+
+  default SafeFuture<Optional<SignedBeaconBlock>> getBlock(final Bytes32 blockRoot) {
+    return getBlocks(Set.of(blockRoot))
+        .thenApply(blocks -> Optional.ofNullable(blocks.get(blockRoot)));
+  }
+}
```

### ethereum/core/src/main/java/tech/pegasys/teku/core/stategenerator/AsyncChainStateGenerator.java
```diff
@@ -0,0 +1,163 @@
+/*
+ * Copyright 2020 ConsenSys AG.
+ *
+ * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
+ * the License. You may obtain a copy of the License at
+ *
+ * http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
+ * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
+ * specific language governing permissions and limitations under the License.
+ */
+
+package tech.pegasys.teku.core.stategenerator;
+
+import static com.google.common.base.Preconditions.checkArgument;
+
+import com.google.common.collect.Lists;
+import java.util.List;
+import java.util.Objects;
+import java.util.concurrent.atomic.AtomicReference;
+import java.util.stream.Collectors;
+import org.apache.logging.log4j.LogManager;
+import org.apache.logging.log4j.Logger;
+import org.apache.tuweni.bytes.Bytes32;
+import tech.pegasys.teku.core.lookup.BlockProvider;
+import tech.pegasys.teku.datastructures.blocks.SignedBeaconBlock;
+import tech.pegasys.teku.datastructures.hashtree.HashTree;
+import tech.pegasys.teku.datastructures.state.BeaconState;
+import tech.pegasys.teku.util.async.SafeFuture;
+
+class AsyncChainStateGenerator {
+  private static final Logger LOG = LogManager.getLogger();
+  public static final int DEFAULT_BLOCK_BATCH_SIZE = 250;
+
+  private final HashTree blockTree;
+  private final BlockProvider blockProvider;
+  private final StateProvider stateProvider;
+  private final int blockBatchSize;
+
+  private AsyncChainStateGenerator(
+      final HashTree blockTree,
+      final BlockProvider blockProvider,
+      final StateProvider stateProvider,
+      final int blockBatchSize) {
+    this.blockTree = blockTree;
+    this.blockProvider = blockProvider;
+    this.stateProvider = stateProvider;
+    this.blockBatchSize = blockBatchSize;
+  }
+
+  public static AsyncChainStateGenerator create(
+      final HashTree blockTree,
+      final BlockProvider blockProvider,
+      final StateProvider stateProvider) {
+    return new AsyncChainStateGenerator(
+        blockTree, blockProvider, stateProvider, DEFAULT_BLOCK_BATCH_SIZE);
+  }
+
+  public SafeFuture<BeaconState> generateTargetState(final Bytes32 targetRoot) {
+    if (!blockTree.contains(targetRoot)) {
+      return SafeFuture.failedFuture(
+          new IllegalArgumentException("Target root is unknown: " + targetRoot));
+    }
+
+    final SafeFuture<BeaconState> lastState = new SafeFuture<>();
+    generateStates(
+            targetRoot,
+            (block, state) -> {
+              if (block.getRoot().equals(targetRoot)) {
+                lastState.complete(state);
+              }
+            })
+        .finish(
+            // Make sure future is completed
+            () ->
+                lastState.completeExceptionally(
+                    new IllegalStateException("Failed to generate state for " + targetRoot)),
+            lastState::completeExceptionally);
+
+    return lastState;
+  }
+
+  public SafeFuture<?> generateStates(final Bytes32 targetRoot, final StateHandler handler) {
+    return SafeFuture.of(
+        () -> {
+          // Build chain from target root to the first ancestor with a known state
+          final AtomicReference<BeaconState> baseState = new AtomicReference<>(null);
+          final List<Bytes32> chain =
+              blockTree.collectChainRoots(
+                  targetRoot,
+                  (currentRoot) -> {
+                    stateProvider.getState(currentRoot).ifPresent(baseState::set);
+                    return baseState.get() == null;
+                  });
+
+          if (baseState.get() == null) {
+            throw new IllegalArgumentException("Unable to find base state to build on");
+          }
+
+          if (chain.size() == 0) {
+            throw new IllegalStateException("Failed to retrieve chain");
+          }
+
+          LOG.debug(
+              "Regenerate state at {}, processing {} blocks on top of slot {} (root: {})",
+              targetRoot,
+              chain.size(),
+              baseState.get().getSlot(),
+              chain.get(0));
+
+          // Process chain in batches
+          final List<List<Bytes32>> blockBatches = Lists.partition(chain, blockBatchSize);
+          // Request and process each batch of blocks in order
+          SafeFuture<BeaconState> future =
+              processBlockBatch(blockBatches.get(0), baseState.get(), handler);
+          for (int i = 1; i < blockBatches.size(); i++) {
+            final List<Bytes32> blockBatch = blockBatches.get(i);
+            future = future.thenCompose(state -> processBlockBatch(blockBatch, state, handler));
+          }
+          return future;
+        });
+  }
+
+  private SafeFuture<BeaconState> processBlockBatch(
+      final List<Bytes32> blockRoots, final BeaconState startState, final StateHandler handler) {
+    checkArgument(startState != null, "Must provide start state");
+    LOG.debug("Retrieve and process {} blocks", blockRoots.size());
+    return blockProvider
+        .getBlocks(blockRoots)
+        .thenApply(
+            blocks -> {
+              final List<SignedBeaconBlock> chainBlocks =
+                  blockRoots.stream()
+                      .map(blocks::get)
+                      .filter(Objects::nonNull)
+                      .collect(Collectors.toList());
+              if (chainBlocks.size() < blockRoots.size()) {
+                final String missingBlocks =
+                    blockRoots.stream()
+                        .filter(root -> !blocks.containsKey(root))
+                        .map(Object::toString)
+                        .collect(Collectors.joining(", "));
+                final int missingCount = blockRoots.size() - chainBlocks.size();
+                throw new IllegalStateException(
+                    String.format(
+                        "Failed to retrieve %d / %d blocks building on state at slot %s: %s",
+                        missingCount, blockRoots.size(), startState.getSlot(), missingBlocks));
+              }
+
+              final ChainStateGenerator chainStateGenerator =
+                  ChainStateGenerator.create(chainBlocks, startState, true);
+              final AtomicReference<BeaconState> lastState = new AtomicReference<>(null);
+              chainStateGenerator.generateStates(
+                  (block, state) -> {
+                    lastState.set(state);
+                    handler.handle(block, state);
+                  });
+
+              return lastState.get();
+            });
+  }
+}
```

### ethereum/core/src/main/java/tech/pegasys/teku/core/stategenerator/BlockProcessor.java
```diff
@@ -0,0 +1,50 @@
+/*
+ * Copyright 2020 ConsenSys AG.
+ *
+ * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
+ * the License. You may obtain a copy of the License at
+ *
+ * http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
+ * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
+ * specific language governing permissions and limitations under the License.
+ */
+
+package tech.pegasys.teku.core.stategenerator;
+
+import tech.pegasys.teku.core.StateTransition;
+import tech.pegasys.teku.core.StateTransitionException;
+import tech.pegasys.teku.core.blockvalidator.NopBlockValidator;
+import tech.pegasys.teku.datastructures.blocks.SignedBeaconBlock;
+import tech.pegasys.teku.datastructures.state.BeaconState;
+
+class BlockProcessor {
+  private final StateTransition stateTransition = new StateTransition(new NopBlockValidator());
+
+  public BeaconState process(final BeaconState preState, final SignedBeaconBlock block) {
+
+    try {
+      final BeaconState postState = stateTransition.initiate(preState, block);
+      assertBlockAndStateMatch(block, postState);
+      return postState;
+    } catch (StateTransitionException e) {
+      throw new IllegalStateException(getFailedStateGenerationError(block), e);
+    }
+  }
+
+  public void assertBlockAndStateMatch(final SignedBeaconBlock block, final BeaconState state) {
+    if (!block.getStateRoot().equals(state.hash_tree_root())) {
+      final String msg =
+          String.format(
+              "Failed to regenerate state for block root %s.  Generated state root %s does not match expected state root %s",
+              block.getRoot(), state.hash_tree_root(), block.getStateRoot());
+      throw new IllegalStateException(msg);
+    }
+  }
+
+  private String getFailedStateGenerationError(final SignedBeaconBlock block) {
+    return String.format(
+        "Unable to produce state for block at slot %s (%s)", block.getSlot(), block.getRoot());
+  }
+}
```

### ethereum/core/src/main/java/tech/pegasys/teku/core/stategenerator/ChainStateGenerator.java
```diff
@@ -0,0 +1,75 @@
+/*
+ * Copyright 2020 ConsenSys AG.
+ *
+ * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
+ * the License. You may obtain a copy of the License at
+ *
+ * http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
+ * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
+ * specific language governing permissions and limitations under the License.
+ */
+
+package tech.pegasys.teku.core.stategenerator;
+
+import static com.google.common.base.Preconditions.checkArgument;
+
+import java.util.List;
+import tech.pegasys.teku.datastructures.blocks.SignedBeaconBlock;
+import tech.pegasys.teku.datastructures.state.BeaconState;
+
+class ChainStateGenerator {
+  private final BlockProcessor blockProcessor = new BlockProcessor();
+  private final List<SignedBeaconBlock> chain;
+  private final BeaconState baseState;
+
+  private ChainStateGenerator(
+      final List<SignedBeaconBlock> chain,
+      final BeaconState baseState,
+      final boolean skipValidation) {
+    if (!skipValidation) {
+      for (int i = chain.size() - 1; i > 0; i--) {
+        checkArgument(
+            chain.get(i).getParent_root().equals(chain.get(i - 1).getRoot()),
+            "Blocks must form an ordered chain");
+      }
+    }
+
+    this.chain = chain;
+    this.baseState = baseState;
+  }
+
+  /**
+   * Create a chain generator that can replay the given blocks on top of the base state.
+   *
+   * @param chain A sorted chain of blocks in ascending order by slot
+   * @param baseState A base state corresponding to the first block in the chain
+   * @return
+   */
+  public static ChainStateGenerator create(
+      final List<SignedBeaconBlock> chain, final BeaconState baseState) {
+    return create(chain, baseState, false);
+  }
+
+  static ChainStateGenerator create(
+      final List<SignedBeaconBlock> chain,
+      final BeaconState baseState,
+      final boolean skipValidation) {
+    return new ChainStateGenerator(chain, baseState, skipValidation);
+  }
+
+  public void generateStates(final StateHandler handler) {
+    // Process blocks in order
+    BeaconState state = baseState;
+    for (SignedBeaconBlock currentBlock : chain) {
+      if (currentBlock.getStateRoot().equals(baseState.hash_tree_root())) {
+        // Don't process base block
+        handler.handle(currentBlock, baseState);
+        continue;
+      }
+      state = blockProcessor.process(state, currentBlock);
+      handler.handle(currentBlock, state);
+    }
+  }
+}
```

### ethereum/core/src/main/java/tech/pegasys/teku/core/stategenerator/StateCache.java
```diff
@@ -0,0 +1,56 @@
+/*
+ * Copyright 2020 ConsenSys AG.
+ *
+ * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
+ * the License. You may obtain a copy of the License at
+ *
+ * http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
+ * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
+ * specific language governing permissions and limitations under the License.
+ */
+
+package tech.pegasys.teku.core.stategenerator;
+
+import com.google.common.annotations.VisibleForTesting;
+import java.util.Map;
+import java.util.Optional;
+import org.apache.tuweni.bytes.Bytes32;
+import tech.pegasys.teku.datastructures.state.BeaconState;
+import tech.pegasys.teku.util.collections.LimitStrategy;
+import tech.pegasys.teku.util.collections.LimitedMap;
+
+class StateCache {
+  private final Map<Bytes32, BeaconState> cache;
+  private final Map<Bytes32, BeaconState> knownStates;
+
+  public StateCache(final int maxCachedStates, final Map<Bytes32, BeaconState> knownStates) {
+    this.cache = LimitedMap.create(maxCachedStates, LimitStrategy.DROP_LEAST_RECENTLY_ACCESSED);
+    this.knownStates = knownStates;
+  }
+
+  boolean containsKnownState(final Bytes32 blockRoot) {
+    return knownStates.containsKey(blockRoot);
+  }
+
+  @VisibleForTesting
+  int countCachedStates() {
+    return cache.size();
+  }
+
+  public Optional<BeaconState> get(final Bytes32 blockRoot) {
+    return Optional.ofNullable(knownStates.get(blockRoot))
+        .or(() -> Optional.ofNullable(cache.get(blockRoot)));
+  }
+
+  public void put(final Bytes32 blockRoot, final BeaconState state) {
+    if (!knownStates.containsKey(blockRoot)) {
+      cache.put(blockRoot, state);
+    }
+  }
+
+  public void clear() {
+    cache.clear();
+  }
+}
```

### ethereum/core/src/main/java/tech/pegasys/teku/core/stategenerator/StateGenerator.java
```diff
@@ -0,0 +1,213 @@
+/*
+ * Copyright 2020 ConsenSys AG.
+ *
+ * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
+ * the License. You may obtain a copy of the License at
+ *
+ * http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
+ * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
+ * specific language governing permissions and limitations under the License.
+ */
+
+package tech.pegasys.teku.core.stategenerator;
+
+import static com.google.common.base.Preconditions.checkArgument;
+import static tech.pegasys.teku.core.stategenerator.AsyncChainStateGenerator.DEFAULT_BLOCK_BATCH_SIZE;
+
+import com.google.common.annotations.VisibleForTesting;
+import com.google.common.collect.Lists;
+import java.util.Collections;
+import java.util.HashMap;
+import java.util.List;
+import java.util.Map;
+import java.util.Optional;
+import java.util.stream.Collectors;
+import org.apache.logging.log4j.LogManager;
+import org.apache.logging.log4j.Logger;
+import org.apache.tuweni.bytes.Bytes32;
+import tech.pegasys.teku.core.lookup.BlockProvider;
+import tech.pegasys.teku.datastructures.blocks.SignedBeaconBlock;
+import tech.pegasys.teku.datastructures.blocks.SignedBlockAndState;
+import tech.pegasys.teku.datastructures.hashtree.HashTree;
+import tech.pegasys.teku.datastructures.state.BeaconState;
+import tech.pegasys.teku.datastructures.state.BlockRootAndState;
+import tech.pegasys.teku.util.async.SafeFuture;
+
+public class StateGenerator {
+  public static final int DEFAULT_STATE_CACHE_SIZE = 50;
+  private static final Logger LOG = LogManager.getLogger();
+
+  private final BlockProcessor blockProcessor = new BlockProcessor();
+  private final HashTree blockTree;
+  private final BlockProvider blockProvider;
+  private final AsyncChainStateGenerator chainStateGenerator;
+
+  private final StateCache stateCache;
+  private final int blockBatchSize;
+
+  private StateGenerator(
+      final HashTree blockTree,
+      final BlockProvider blockProvider,
+      final AsyncChainStateGenerator chainStateGenerator,
+      final StateCache stateCache,
+      final int blockBatchSize) {
+    checkArgument(blockBatchSize > 0, "Must provide a block batch size > 0");
+    checkArgument(
+        stateCache.containsKnownState(blockTree.getRootHash()), "Root state must be available");
+
+    this.blockTree = blockTree;
+    this.blockProvider = blockProvider;
+    this.stateCache = stateCache;
+    this.blockBatchSize = blockBatchSize;
+    this.chainStateGenerator = chainStateGenerator;
+  }
+
+  public static StateGenerator create(
+      final HashTree blockTree,
+      final SignedBlockAndState rootBlockAndState,
+      final BlockProvider blockProvider) {
+    return create(blockTree, rootBlockAndState, blockProvider, Collections.emptyMap());
+  }
+
+  public static StateGenerator create(
+      final HashTree blockTree,
+      final SignedBlockAndState rootBlockAndState,
+      final BlockProvider blockProvider,
+      final Map<Bytes32, BeaconState> knownStates) {
+    return create(
+        blockTree,
+        rootBlockAndState,
+        blockProvider,
+        knownStates,
+        DEFAULT_BLOCK_BATCH_SIZE,
+        DEFAULT_STATE_CACHE_SIZE);
+  }
+
+  public static StateGenerator create(
+      final HashTree blockTree,
+      final SignedBlockAndState rootBlockAndState,
+      final BlockProvider blockProvider,
+      final Map<Bytes32, BeaconState> knownStates,
+      final int blockBatchSize,
+      final int stateCacheSize) {
+    checkArgument(
+        rootBlockAndState.getRoot().equals(blockTree.getRootHash()),
+        "Provided root block must match the root of the provided block tree");
+
+    final Map<Bytes32, BeaconState> availableStates = new HashMap<>(knownStates);
+    availableStates.put(rootBlockAndState.getRoot(), rootBlockAndState.getState());
+    final StateCache stateCache = new StateCache(stateCacheSize, availableStates);
+
+    final AsyncChainStateGenerator chainStateGenerator =
+        AsyncChainStateGenerator.create(blockTree, blockProvider, stateCache::get);
+    return new StateGenerator(
+        blockTree, blockProvider, chainStateGenerator, stateCache, blockBatchSize);
+  }
+
+  public SafeFuture<BeaconState> regenerateStateForBlock(final Bytes32 blockRoot) {
+    LOG.debug("Regenerate state for block {}", blockRoot);
+    return chainStateGenerator.generateTargetState(blockRoot);
+  }
+
+  public SafeFuture<Void> regenerateAllStates(final StateHandler stateHandler) {
+    LOG.debug(
+        "Regenerate all states for block tree of size {} rooted at block {}",
+        blockTree.size(),
+        blockTree.getRootHash());
+    return regenerateAllStatesInternal(stateHandler).thenAccept(__ -> stateCache.clear());
+  }
+
+  @VisibleForTesting
+  SafeFuture<?> regenerateAllStatesInternal(final StateHandler stateHandler) {
+    final List<Bytes32> blockRoots = blockTree.preOrderStream().collect(Collectors.toList());
+    if (blockRoots.size() == 0) {
+      return SafeFuture.completedFuture(null);
+    }
+
+    // Break up blocks into batches
+    final List<List<Bytes32>> blockBatches = Lists.partition(blockRoots, blockBatchSize);
+    // Request and process each batch of blocks in order
+    final Bytes32 rootHash = blockTree.getRootHash();
+    final BeaconState rootState = stateCache.get(rootHash).orElseThrow();
+    final BlockRootAndState rootAndState = new BlockRootAndState(rootHash, rootState);
+    SafeFuture<BlockRootAndState> future =
+        regenerateAllStatesForBatch(blockBatches.get(0), stateCache, rootAndState, stateHandler);
+    for (int i = 1; i < blockBatches.size(); i++) {
+      final List<Bytes32> batch = blockBatches.get(i);
+      future =
+          future.thenCompose(
+              state -> regenerateAllStatesForBatch(batch, stateCache, state, stateHandler));
+    }
+
+    return future;
+  }
+
+  @VisibleForTesting
+  int countCachedStates() {
+    return stateCache.countCachedStates();
+  }
+
+  private SafeFuture<BlockRootAndState> regenerateAllStatesForBatch(
+      final List<Bytes32> blockRoots,
+      final StateCache stateCache,
+      final BlockRootAndState lastProcessedState,
+      final StateHandler stateHandler) {
+    return blockProvider
+        .getBlocks(blockRoots)
+        .thenCompose(
+            (blocks) -> {
+              LOG.debug("Process {} blocks", blocks.size());
+              BlockRootAndState currentState = lastProcessedState;
+              for (int i = 0; i < blockRoots.size(); i++) {
+                final Bytes32 blockRoot = blockRoots.get(i);
+                final SignedBeaconBlock currentBlock = blocks.get(blockRoot);
+                if (currentBlock == null) {
+                  throw new IllegalStateException(
+                      String.format(
+                          "Failed to retrieve required block %s. Last processed block was at slot %s.",
+                          blockRoot, lastProcessedState.getState().getSlot()));
+                }
+
+                BeaconState postState = stateCache.get(currentBlock.getRoot()).orElse(null);
+                if (postState == null) {
+                  // Generate post state
+                  final Bytes32 parentRoot = currentBlock.getParent_root();
+                  // Find pre-state to build on
+                  final BeaconState preState;
+                  if (currentState.getBlockRoot().equals(parentRoot)) {
+                    preState = currentState.getState();
+                  } else {
+                    final Optional<BeaconState> maybePreState = stateCache.get(parentRoot);
+                    if (maybePreState.isPresent()) {
+                      preState = maybePreState.get();
+                    } else {
+                      LOG.debug("Regenerate missing state for block {}", parentRoot);
+                      final List<Bytes32> remainingRoots = blockRoots.subList(i, blockRoots.size());
+                      return chainStateGenerator
+                          .generateTargetState(parentRoot)
+                          .thenApply(parentState -> new BlockRootAndState(parentRoot, parentState))
+                          .thenCompose(
+                              (lastState) ->
+                                  regenerateAllStatesForBatch(
+                                      remainingRoots, stateCache, lastState, stateHandler));
+                    }
+                  }
+
+                  // Cache state if other branches exist that might need it
+                  if (blockTree.countChildren(parentRoot) > 1) {
+                    stateCache.put(parentRoot, preState);
+                  }
+                  postState = blockProcessor.process(preState, currentBlock);
+                }
+
+                blockProcessor.assertBlockAndStateMatch(currentBlock, postState);
+                stateHandler.handle(currentBlock, postState);
+                currentState = new BlockRootAndState(currentBlock.getRoot(), postState);
+              }
+
+              return SafeFuture.completedFuture(currentState);
+            });
+  }
+}
```

### ethereum/core/src/main/java/tech/pegasys/teku/core/stategenerator/StateHandler.java
```diff
@@ -0,0 +1,23 @@
+/*
+ * Copyright 2020 ConsenSys AG.
+ *
+ * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
+ * the License. You may obtain a copy of the License at
+ *
+ * http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
+ * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
+ * specific language governing permissions and limitations under the License.
+ */
+
+package tech.pegasys.teku.core.stategenerator;
+
+import tech.pegasys.teku.datastructures.blocks.SignedBeaconBlock;
+import tech.pegasys.teku.datastructures.state.BeaconState;
+
+public interface StateHandler {
+  StateHandler NOOP = (block, state) -> {};
+
+  void handle(final SignedBeaconBlock block, final BeaconState state);
+}
```

### ethereum/core/src/main/java/tech/pegasys/teku/core/stategenerator/StateProvider.java
```diff
@@ -0,0 +1,23 @@
+/*
+ * Copyright 2020 ConsenSys AG.
+ *
+ * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
+ * the License. You may obtain a copy of the License at
+ *
+ * http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
+ * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
+ * specific language governing permissions and limitations under the License.
+ */
+
+package tech.pegasys.teku.core.stategenerator;
+
+import java.util.Optional;
+import org.apache.tuweni.bytes.Bytes32;
+import tech.pegasys.teku.datastructures.state.BeaconState;
+
+@FunctionalInterface
+interface StateProvider {
+  Optional<BeaconState> getState(final Bytes32 blockRoot);
+}
```

### ethereum/core/src/test/java/tech/pegasys/teku/core/lookup/BlockProviderTest.java
```diff
@@ -0,0 +1,135 @@
+/*
+ * Copyright 2020 ConsenSys AG.
+ *
+ * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
+ * the License. You may obtain a copy of the License at
+ *
+ * http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
+ * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
+ * specific language governing permissions and limitations under the License.
+ */
+
+package tech.pegasys.teku.core.lookup;
+
+import static org.assertj.core.api.Assertions.assertThat;
+
+import java.util.Collections;
+import java.util.Map;
+import java.util.Optional;
+import java.util.concurrent.ExecutionException;
+import java.util.concurrent.atomic.AtomicReference;
+import java.util.stream.Collectors;
+import org.apache.tuweni.bytes.Bytes32;
+import org.junit.jupiter.api.Test;
+import tech.pegasys.teku.core.ChainBuilder;
+import tech.pegasys.teku.core.StateTransitionException;
+import tech.pegasys.teku.datastructures.blocks.SignedBeaconBlock;
+import tech.pegasys.teku.datastructures.blocks.SignedBlockAndState;
+
+public class BlockProviderTest {
+  private final ChainBuilder chainBuilder = ChainBuilder.createDefault();
+
+  @Test
+  void withKnownBlocks_withEmptyProvider()
+      throws StateTransitionException, ExecutionException, InterruptedException {
+    chainBuilder.generateGenesis();
+    chainBuilder.generateBlocksUpToSlot(2);
+    final Map<Bytes32, SignedBeaconBlock> knownBlocks =
+        chainBuilder
+            .streamBlocksAndStates()
+            .collect(Collectors.toMap(SignedBlockAndState::getRoot, SignedBlockAndState::getBlock));
+
+    final BlockProvider provider = BlockProvider.withKnownBlocks(BlockProvider.NOOP, knownBlocks);
+    for (Bytes32 root : knownBlocks.keySet()) {
+      assertThat(provider.getBlock(root).get()).contains(knownBlocks.get(root));
+    }
+  }
+
+  @Test
+  void withKnownBlocks_withNonEmptyProvider()
+      throws StateTransitionException, ExecutionException, InterruptedException {
+    chainBuilder.generateGenesis();
+    chainBuilder.generateBlocksUpToSlot(10);
+
+    final Map<Bytes32, SignedBeaconBlock> knownBlocks =
+        chainBuilder
+            .streamBlocksAndStates(0, 5)
+            .collect(Collectors.toMap(SignedBlockAndState::getRoot, SignedBlockAndState::getBlock));
+    final Map<Bytes32, SignedBeaconBlock> otherBlocks =
+        chainBuilder
+            .streamBlocksAndStates(6)
+            .collect(Collectors.toMap(SignedBlockAndState::getRoot, SignedBlockAndState::getBlock));
+
+    final BlockProvider origProvider = BlockProvider.fromMap(otherBlocks);
+    final BlockProvider provider = BlockProvider.withKnownBlocks(origProvider, knownBlocks);
+
+    // Pull known blocks
+    for (Bytes32 root : knownBlocks.keySet()) {
+      assertThat(provider.getBlock(root).get()).contains(knownBlocks.get(root));
+    }
+    // Pull blocks from original provider
+    for (Bytes32 root : otherBlocks.keySet()) {
+      assertThat(provider.getBlock(root).get()).contains(otherBlocks.get(root));
+    }
+  }
+
+  @Test
+  void combined() throws StateTransitionException, ExecutionException, InterruptedException {
+    chainBuilder.generateGenesis();
+    chainBuilder.generateBlocksUpToSlot(10);
+
+    final Map<Bytes32, SignedBeaconBlock> allBlocks =
+        chainBuilder
+            .streamBlocksAndStates()
+            .collect(Collectors.toMap(SignedBlockAndState::getRoot, SignedBlockAndState::getBlock));
+    final Map<Bytes32, SignedBeaconBlock> setA =
+        chainBuilder
+            .streamBlocksAndStates(0, 3)
+            .collect(Collectors.toMap(SignedBlockAndState::getRoot, SignedBlockAndState::getBlock));
+    final Map<Bytes32, SignedBeaconBlock> setB =
+        chainBuilder
+            .streamBlocksAndStates(4, 6)
+            .collect(Collectors.toMap(SignedBlockAndState::getRoot, SignedBlockAndState::getBlock));
+    final Map<Bytes32, SignedBeaconBlock> setC =
+        chainBuilder
+            .streamBlocksAndStates(7, 10)
+            .collect(Collectors.toMap(SignedBlockAndState::getRoot, SignedBlockAndState::getBlock));
+
+    final BlockProvider provider =
+        BlockProvider.combined(
+            BlockProvider.fromMap(setA), BlockProvider.fromMap(setB), BlockProvider.fromMap(setC));
+
+    // Check all blocks are available
+    for (Bytes32 root : allBlocks.keySet()) {
+      assertThat(provider.getBlock(root).get()).contains(allBlocks.get(root));
+    }
+  }
+
+  @Test
+  void fromDynamicMap() throws StateTransitionException {
+    chainBuilder.generateGenesis();
+    SignedBlockAndState blockA = chainBuilder.generateNextBlock();
+    SignedBlockAndState blockB = chainBuilder.generateNextBlock();
+
+    final AtomicReference<Map<Bytes32, SignedBeaconBlock>> mapSupplier =
+        new AtomicReference<>(Collections.emptyMap());
+    final BlockProvider provider = BlockProvider.fromDynamicMap(mapSupplier::get);
+
+    assertThat(provider.getBlock(blockA.getRoot())).isCompletedWithValue(Optional.empty());
+    assertThat(provider.getBlock(blockB.getRoot())).isCompletedWithValue(Optional.empty());
+
+    mapSupplier.set(Map.of(blockA.getRoot(), blockA.getBlock()));
+
+    assertThat(provider.getBlock(blockA.getRoot()))
+        .isCompletedWithValue(Optional.of(blockA.getBlock()));
+    assertThat(provider.getBlock(blockB.getRoot())).isCompletedWithValue(Optional.empty());
+
+    mapSupplier.set(Map.of(blockB.getRoot(), blockB.getBlock()));
+
+    assertThat(provider.getBlock(blockA.getRoot())).isCompletedWithValue(Optional.empty());
+    assertThat(provider.getBlock(blockB.getRoot()))
+        .isCompletedWithValue(Optional.of(blockB.getBlock()));
+  }
+}
```

### ethereum/core/src/test/java/tech/pegasys/teku/core/stategenerator/StateCacheTest.java
```diff
@@ -0,0 +1,94 @@
+/*
+ * Copyright 2020 ConsenSys AG.
+ *
+ * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
+ * the License. You may obtain a copy of the License at
+ *
+ * http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
+ * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
+ * specific language governing permissions and limitations under the License.
+ */
+
+package tech.pegasys.teku.core.stategenerator;
+
+import static org.assertj.core.api.Assertions.assertThat;
+
+import java.util.List;
+import java.util.Map;
+import java.util.stream.Collectors;
+import org.apache.tuweni.bytes.Bytes32;
+import org.junit.jupiter.api.BeforeEach;
+import org.junit.jupiter.api.Test;
+import tech.pegasys.teku.core.ChainBuilder;
+import tech.pegasys.teku.core.StateTransitionException;
+import tech.pegasys.teku.datastructures.blocks.SignedBlockAndState;
+import tech.pegasys.teku.datastructures.state.BeaconState;
+
+public class StateCacheTest {
+
+  private final ChainBuilder chainBuilder = ChainBuilder.createDefault();
+
+  private final int chainSize = 10;
+  private final int maxSize = 2;
+
+  private List<SignedBlockAndState> chain;
+  private SignedBlockAndState knownState1;
+  private SignedBlockAndState knownState2;
+  private Map<Bytes32, BeaconState> knownStates;
+  private StateCache cache;
+
+  @BeforeEach
+  void setup() throws StateTransitionException {
+    chainBuilder.generateGenesis();
+    chainBuilder.generateBlocksUpToSlot(chainSize);
+    chain = chainBuilder.streamBlocksAndStates().collect(Collectors.toList());
+
+    knownState1 = chain.get(0);
+    knownState2 = chain.get(1);
+    knownStates =
+        Map.of(
+            knownState1.getRoot(),
+            knownState1.getState(),
+            knownState2.getRoot(),
+            knownState2.getState());
+
+    cache = new StateCache(maxSize, knownStates);
+  }
+
+  @Test
+  public void put_exceedsMaxSize() {
+    List<SignedBlockAndState> toAdd =
+        chain.stream()
+            .filter(b -> !knownStates.containsKey(b.getRoot()))
+            .limit(maxSize + 1)
+            .collect(Collectors.toList());
+    for (int i = 0; i < toAdd.size(); i++) {
+      SignedBlockAndState blockAndState = toAdd.get(i);
+      cache.put(blockAndState.getRoot(), blockAndState.getState());
+      assertThat(cache.countCachedStates()).isEqualTo(Math.min(i + 1, maxSize));
+    }
+
+    // Known states should still be available
+    assertThat(cache.get(knownState1.getRoot())).contains(knownState1.getState());
+    assertThat(cache.get(knownState2.getRoot())).contains(knownState2.getState());
+  }
+
+  @Test
+  public void get_knownState() {
+    assertThat(cache.get(knownState1.getRoot())).contains(knownState1.getState());
+    assertThat(cache.get(knownState2.getRoot())).contains(knownState2.getState());
+
+    cache.clear();
+
+    assertThat(cache.get(knownState1.getRoot())).contains(knownState1.getState());
+    assertThat(cache.get(knownState2.getRoot())).contains(knownState2.getState());
+  }
+
+  @Test
+  public void put_knownState() {
+    cache.put(knownState1.getRoot(), knownState1.getState());
+    assertThat(cache.countCachedStates()).isEqualTo(0);
+  }
+}
```

### ethereum/core/src/test/java/tech/pegasys/teku/core/stategenerator/StateGeneratorTest.java
```diff
@@ -11,16 +11,20 @@
  * specific language governing permissions and limitations under the License.
  */
 
-package tech.pegasys.teku.core;
+package tech.pegasys.teku.core.stategenerator;
 
 import static org.assertj.core.api.Assertions.assertThat;
+import static org.assertj.core.api.Assertions.assertThatThrownBy;
 
 import com.google.common.collect.Streams;
 import com.google.common.primitives.UnsignedLong;
 import java.util.ArrayList;
 import java.util.Collections;
 import java.util.List;
 import java.util.Map;
+import java.util.concurrent.ExecutionException;
+import java.util.function.BiConsumer;
+import java.util.function.Function;
 import java.util.stream.Collectors;
 import java.util.stream.Stream;
 import org.apache.tuweni.bytes.Bytes32;
@@ -30,18 +34,22 @@
 import org.junit.jupiter.params.provider.MethodSource;
 import tech.pegasys.teku.bls.BLSKeyGenerator;
 import tech.pegasys.teku.bls.BLSKeyPair;
-import tech.pegasys.teku.datastructures.blocks.BlockTree;
+import tech.pegasys.teku.core.ChainBuilder;
+import tech.pegasys.teku.core.StateTransitionException;
+import tech.pegasys.teku.core.lookup.BlockProvider;
 import tech.pegasys.teku.datastructures.blocks.SignedBeaconBlock;
 import tech.pegasys.teku.datastructures.blocks.SignedBlockAndState;
+import tech.pegasys.teku.datastructures.hashtree.HashTree;
 import tech.pegasys.teku.datastructures.state.BeaconState;
+import tech.pegasys.teku.util.async.SafeFuture;
 
 public class StateGeneratorTest {
   protected static final List<BLSKeyPair> VALIDATOR_KEYS = BLSKeyGenerator.generateKeyPairs(3);
   private final ChainBuilder chainBuilder = ChainBuilder.create(VALIDATOR_KEYS);
 
-  @ParameterizedTest(name = "cache size: {0}")
-  @MethodSource("getCacheSize")
-  public void shouldHandleValidChainFromGenesis(final int cacheSize)
+  @ParameterizedTest(name = "cache size: {0}, block batch size: {1}")
+  @MethodSource("getParameters")
+  public void shouldHandleValidChainFromGenesis(final int cacheSize, final int blockBatchSize)
       throws StateTransitionException {
     // Build a small chain
     final SignedBlockAndState genesis = chainBuilder.generateGenesis();
@@ -52,12 +60,12 @@ public void shouldHandleValidChainFromGenesis(final int cacheSize)
                 genesis.getSlot().plus(UnsignedLong.ONE), chainBuilder.getLatestSlot())
             .collect(Collectors.toList());
 
-    testRegenerateAllStates(cacheSize, genesis, newBlocksAndStates);
+    testRegenerateAllStates(cacheSize, blockBatchSize, genesis, 0, newBlocksAndStates);
   }
 
-  @ParameterizedTest(name = "cache size: {0}")
-  @MethodSource("getCacheSize")
-  public void shouldHandleValidPostGenesisChain(final int cacheSize)
+  @ParameterizedTest(name = "cache size: {0}, block batch size: {1}")
+  @MethodSource("getParameters")
+  public void shouldHandleValidPostGenesisChain(final int cacheSize, final int blockBatchSize)
       throws StateTransitionException {
     // Build a small chain
     chainBuilder.generateGenesis();
@@ -69,12 +77,13 @@ public void shouldHandleValidPostGenesisChain(final int cacheSize)
                 baseBlock.getSlot().plus(UnsignedLong.ONE), chainBuilder.getLatestSlot())
             .collect(Collectors.toList());
 
-    testRegenerateAllStates(cacheSize, baseBlock, newBlocksAndStates);
+    testRegenerateAllStates(cacheSize, blockBatchSize, baseBlock, 0, newBlocksAndStates);
   }
 
-  @ParameterizedTest(name = "cache size: {0}")
-  @MethodSource("getCacheSize")
-  public void shouldHandleInvalidForkBlocks(final int cacheSize) throws StateTransitionException {
+  @ParameterizedTest(name = "cache size: {0}, block batch size: {1}")
+  @MethodSource("getParameters")
+  public void shouldHandleInvalidForkBlocks(final int cacheSize, final int blockBatchSize)
+      throws StateTransitionException {
     // Build a small chain
     chainBuilder.generateGenesis();
     chainBuilder.generateBlocksUpToSlot(5);
@@ -99,12 +108,14 @@ public void shouldHandleInvalidForkBlocks(final int cacheSize) throws StateTrans
             .map(SignedBlockAndState::getBlock)
             .collect(Collectors.toList());
 
-    testRegenerateAllStates(cacheSize, baseBlock, newBlocksAndStates, newForkBlocks);
+    testRegenerateAllStates(
+        cacheSize, blockBatchSize, baseBlock, 0, newBlocksAndStates, newForkBlocks);
   }
 
-  @ParameterizedTest(name = "cache size: {0}")
-  @MethodSource("getCacheSize")
-  public void shouldHandleForkBlocks(final int cacheSize) throws StateTransitionException {
+  @ParameterizedTest(name = "cache size: {0}, block batch size: {1}")
+  @MethodSource("getParameters")
+  public void shouldHandleForkBlocks(final int cacheSize, final int blockBatchSize)
+      throws StateTransitionException {
     // Build a small chain
     chainBuilder.generateGenesis();
     chainBuilder.generateBlocksUpToSlot(5);
@@ -124,21 +135,24 @@ public void shouldHandleForkBlocks(final int cacheSize) throws StateTransitionEx
     fork.streamBlocksAndStates(baseBlock.getSlot().plus(UnsignedLong.ONE), fork.getLatestSlot())
         .forEach(newBlocksAndStates::add);
 
-    testRegenerateAllStates(cacheSize, baseBlock, newBlocksAndStates);
+    testRegenerateAllStates(cacheSize, blockBatchSize, baseBlock, 1, newBlocksAndStates);
   }
 
-  @ParameterizedTest(name = "cache size: {0}")
-  @MethodSource("getCacheSize")
-  public void shouldHandleMultipleForks(final int cacheSize) throws StateTransitionException {
+  @ParameterizedTest(name = "cache size: {0}, block batch size: {1}")
+  @MethodSource("getParameters")
+  public void shouldHandleMultipleForks(final int cacheSize, final int blockBatchSize)
+      throws StateTransitionException {
     // Build a small chain
     chainBuilder.generateGenesis();
     chainBuilder.generateBlocksUpToSlot(5);
     final SignedBlockAndState baseBlock = chainBuilder.getLatestBlockAndState();
+    // Branch at current block
     final ChainBuilder fork = chainBuilder.fork();
 
     chainBuilder.generateBlocksUpToSlot(10);
     // Fork chain skips a block
     final SignedBlockAndState forkBase = fork.generateBlockAtSlot(7);
+    // Branch at current block
     final ChainBuilder fork2 = fork.fork();
     final ChainBuilder fork3 = fork.fork();
     final ChainBuilder fork4 = fork.fork();
@@ -161,71 +175,175 @@ public void shouldHandleMultipleForks(final int cacheSize) throws StateTransitio
                     forkBase.getSlot().plus(UnsignedLong.ONE), fork4.getLatestSlot()))
             .collect(Collectors.toList());
 
-    testRegenerateAllStates(cacheSize, baseBlock, newBlocksAndStates);
+    testRegenerateAllStates(cacheSize, blockBatchSize, baseBlock, 2, newBlocksAndStates);
   }
 
   @Test
   public void produceStatesForBlocks_emptyNewBlockCollection() {
     final SignedBlockAndState genesis = chainBuilder.generateGenesis();
 
-    testRegenerateAllStates(0, genesis, Collections.emptyList());
+    testRegenerateAllStates(0, 10, genesis, 0, Collections.emptyList());
+  }
+
+  @Test
+  public void regenerateAllStates_failOnMissingBlocks() throws StateTransitionException {
+    testGeneratorWithMissingBlock(
+        (generator, missingBlock) -> {
+          SafeFuture<Void> result = generator.regenerateAllStates(StateHandler.NOOP);
+          assertThatThrownBy(result::get)
+              .hasCauseInstanceOf(IllegalStateException.class)
+              .hasMessageContaining(
+                  "Failed to retrieve required block "
+                      + missingBlock.getRoot()
+                      + ". Last processed block was at slot 0.");
+        });
+  }
+
+  @Test
+  public void regenerateStateForBlock_failOnMissingBlocks() throws StateTransitionException {
+    testGeneratorWithMissingBlock(
+        (generator, missingBlock) -> {
+          SafeFuture<BeaconState> result =
+              generator.regenerateStateForBlock(missingBlock.getRoot());
+          assertThatThrownBy(result::get)
+              .hasCauseInstanceOf(IllegalStateException.class)
+              .hasMessageContaining(
+                  "Failed to retrieve 1 / 3 blocks building on state at slot 0: "
+                      + missingBlock.getRoot());
+        });
+  }
+
+  @Test
+  public void regenerateStateForBlock_blockPastTargetIsMissing() throws StateTransitionException {
+    testGeneratorWithMissingBlock(
+        (generator, missingBlock) -> {
+          SignedBlockAndState target =
+              chainBuilder.getBlockAndStateAtSlot(missingBlock.getSlot().minus(UnsignedLong.ONE));
+          SafeFuture<BeaconState> result = generator.regenerateStateForBlock(target.getRoot());
+          assertThat(result).isCompletedWithValue(target.getState());
+        });
+  }
+
+  private void testGeneratorWithMissingBlock(
+      BiConsumer<StateGenerator, SignedBeaconBlock> processor) throws StateTransitionException {
+    // Build a small chain
+    final SignedBlockAndState genesis = chainBuilder.generateGenesis();
+    chainBuilder.generateBlocksUpToSlot(5);
+    final Map<Bytes32, SignedBeaconBlock> blockMap =
+        chainBuilder
+            .streamBlocksAndStates()
+            .map(SignedBlockAndState::getBlock)
+            .collect(Collectors.toMap(SignedBeaconBlock::getRoot, Function.identity()));
+
+    final HashTree tree =
+        HashTree.builder().rootHash(genesis.getRoot()).blocks(blockMap.values()).build();
+    // Create block provider that is missing some blocks
+    final SignedBeaconBlock missingBlock =
+        chainBuilder.getBlockAtSlot(genesis.getSlot().plus(UnsignedLong.valueOf(2)));
+    blockMap.remove(missingBlock.getRoot());
+    final BlockProvider blockProvider = BlockProvider.fromMap(blockMap);
+
+    final StateGenerator generator = StateGenerator.create(tree, genesis, blockProvider);
+    processor.accept(generator, missingBlock);
   }
 
   private void testRegenerateAllStates(
       final int cacheSize,
+      final int blockBatchSize,
       final SignedBlockAndState rootBlockAndState,
+      final int expectedCachedStateCount,
       final List<SignedBlockAndState> descendantBlocksAndStates) {
     testRegenerateAllStates(
-        cacheSize, rootBlockAndState, descendantBlocksAndStates, Collections.emptyList());
+        cacheSize,
+        blockBatchSize,
+        rootBlockAndState,
+        expectedCachedStateCount,
+        descendantBlocksAndStates,
+        Collections.emptyList());
   }
 
   private void testRegenerateAllStates(
       final int cacheSize,
+      final int blockBatchSize,
       final SignedBlockAndState rootBlockAndState,
+      final int expectedCachedStateCount,
       final List<SignedBlockAndState> descendantBlocksAndStates,
       final List<SignedBeaconBlock> unconnectedBlocks) {
     testRegenerateAllStates(
-        cacheSize, rootBlockAndState, descendantBlocksAndStates, unconnectedBlocks, false);
+        cacheSize,
+        blockBatchSize,
+        rootBlockAndState,
+        expectedCachedStateCount,
+        descendantBlocksAndStates,
+        unconnectedBlocks,
+        false);
     testRegenerateAllStates(
-        cacheSize, rootBlockAndState, descendantBlocksAndStates, unconnectedBlocks, true);
+        cacheSize,
+        blockBatchSize,
+        rootBlockAndState,
+        expectedCachedStateCount,
+        descendantBlocksAndStates,
+        unconnectedBlocks,
+        true);
   }
 
   private void testRegenerateAllStates(
       final int cacheSize,
+      final int blockBatchSize,
       final SignedBlockAndState rootBlockAndState,
+      final int expectedCachedStateCount,
       final List<SignedBlockAndState> descendantBlocksAndStates,
       final List<SignedBeaconBlock> unconnectedBlocks,
       final boolean supplyAllKnownStates) {
     final List<SignedBeaconBlock> descendantBlocks =
         descendantBlocksAndStates.stream()
             .map(SignedBlockAndState::getBlock)
             .collect(Collectors.toList());
+
+    final List<SignedBlockAndState> allBlocksAndStates = new ArrayList<>();
+    allBlocksAndStates.add(rootBlockAndState);
+    allBlocksAndStates.addAll(descendantBlocksAndStates);
+    final List<SignedBeaconBlock> allBlocks =
+        allBlocksAndStates.stream().map(SignedBlockAndState::getBlock).collect(Collectors.toList());
     final Map<Bytes32, BeaconState> expectedResult =
-        descendantBlocksAndStates.stream()
+        allBlocksAndStates.stream()
             .collect(Collectors.toMap(SignedBlockAndState::getRoot, SignedBlockAndState::getState));
 
     // Create generator
-    final BlockTree blockTree =
-        BlockTree.builder()
-            .rootBlock(rootBlockAndState.getBlock())
+    final HashTree blockTree =
+        HashTree.builder()
+            .rootHash(rootBlockAndState.getRoot())
+            .block(rootBlockAndState.getBlock())
             .blocks(descendantBlocks)
             .blocks(unconnectedBlocks)
             .build();
+    final BlockProvider blockProvider = BlockProvider.fromList(allBlocks);
     final StateGenerator generator =
         supplyAllKnownStates
-            ? StateGenerator.create(blockTree, rootBlockAndState.getState(), expectedResult)
-            : StateGenerator.create(blockTree, rootBlockAndState.getState());
+            ? StateGenerator.create(
+                blockTree, rootBlockAndState, blockProvider, expectedResult, 1000, cacheSize)
+            : StateGenerator.create(
+                blockTree,
+                rootBlockAndState,
+                blockProvider,
+                Collections.emptyMap(),
+                blockBatchSize,
+                cacheSize);
 
     // Regenerate all states and collect results
-    final List<StateAndBlockRoot> results = new ArrayList<>();
-    generator.regenerateAllStates(
-        (root, state) -> results.add(new StateAndBlockRoot(root, state)), cacheSize);
+    final List<SignedBlockAndState> results = new ArrayList<>();
+    generator
+        .regenerateAllStatesInternal(
+            (block, state) -> results.add(new SignedBlockAndState(block, state)))
+        .join();
+    // Check that we don't cache more states than we're expected
+    // We should only cache states for blocks that have multiple descendants
+    assertThat(generator.countCachedStates()).isLessThanOrEqualTo(expectedCachedStateCount);
 
     // Verify results
     final Map<Bytes32, BeaconState> resultMap =
         results.stream()
-            .collect(
-                Collectors.toMap(StateAndBlockRoot::getBlockRoot, StateAndBlockRoot::getState));
+            .collect(Collectors.toMap(SignedBlockAndState::getRoot, SignedBlockAndState::getState));
     // We shouldn't process any duplicates
     assertThat(resultMap.size()).isEqualTo(results.size());
     // Check that our expectations are met
@@ -240,38 +358,39 @@ private void testRegenerateAllStates(
     } else if (cacheSize == 0) {
       // All states should be regenerated and should not match the known states
       for (Bytes32 root : expectedResult.keySet()) {
+        // Skip root state
+        if (root.equals(rootBlockAndState.getRoot())) {
+          continue;
+        }
         assertThat(resultMap.get(root)).isNotSameAs(expectedResult.get(root));
       }
     }
 
-    // Test generating each expected state 1 by 1
-    for (SignedBlockAndState descendant : descendantBlocksAndStates) {
-      final BeaconState stateResult = generator.regenerateStateForBlock(descendant.getRoot());
-      assertThat(stateResult)
-          .isEqualToIgnoringGivenFields(
-              descendant.getState(), "transitionCaches", "childrenViewCache", "backingNode");
+    try {
+      // Test generating each expected state 1 by 1
+      for (SignedBlockAndState descendant : descendantBlocksAndStates) {
+        final BeaconState stateResult =
+            generator.regenerateStateForBlock(descendant.getRoot()).get();
+        assertThat(stateResult)
+            .isEqualToIgnoringGivenFields(
+                descendant.getState(), "transitionCaches", "childrenViewCache", "backingNode");
+      }
+    } catch (ExecutionException | InterruptedException e) {
+      throw new RuntimeException(e);
     }
   }
 
-  public static Stream<Arguments> getCacheSize() {
-    return Stream.of(Arguments.of(0), Arguments.of(1), Arguments.of(100));
-  }
-
-  private static class StateAndBlockRoot {
-    private final BeaconState state;
-    private final Bytes32 blockRoot;
+  public static Stream<Arguments> getParameters() {
+    Stream.Builder<Arguments> builder = Stream.builder();
 
-    private StateAndBlockRoot(final Bytes32 blockRoot, final BeaconState state) {
-      this.state = state;
-      this.blockRoot = blockRoot;
-    }
-
-    public BeaconState getState() {
-      return state;
+    final List<Integer> stateCacheSizes = List.of(0, 1, 100);
+    final List<Integer> blockBatchSizes = List.of(1, 5, 1000);
+    for (Integer stateCacheSize : stateCacheSizes) {
+      for (Integer blockBatchSize : blockBatchSizes) {
+        builder.add(Arguments.of(stateCacheSize, blockBatchSize));
+      }
     }
 
-    public Bytes32 getBlockRoot() {
-      return blockRoot;
-    }
+    return builder.build();
   }
 }
```
