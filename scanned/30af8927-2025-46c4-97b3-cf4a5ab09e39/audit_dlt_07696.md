# [?] Fixes: GHSA-9w9r-w3rf-j6vj enforce maxLogRange on eth_getFilterLogs and eth_newFilter (#11099)

## Summary
Severity: Unknown
Chain: Ethereum
Component: besu-eth/besu
Published: 2026-08-24
Source: https://github.com/besu-eth/besu/commit/7c3a30b8a24c4e5d896d9230cc223962b61af4c1
Type: security-commit

## Details
Fixes: GHSA-9w9r-w3rf-j6vj enforce maxLogRange on eth_getFilterLogs and eth_newFilter (#11099)

Signed-off-by: Sally MacFarlane <macfarla.github@gmail.com>

## Patch
### CHANGELOG.md
```diff
@@ -79,13 +79,12 @@
 - Bound the DiscV4 inbound packet pipeline with an admission gate (256 in-flight packets) and a bounded crypto executor queue, preventing a UDP flood from exhausting memory.
 - Cap the number of snap/1-2 GET_* requests concurrently scheduled for processing on a snap-serving node, both per-peer (--Xsnapsync-server-max-concurrent-requests-per-peer, default 8) and globally (--Xsnapsync-server-max-concurrent-requests, default 200). [#11101](https://github.com/besu-eth/besu/pull/11101)
 - Cap the QBFT/IBFT round change number to prevent unbounded memory growth from malformed round-change messages.
-- Cap pre-STATUS RLPx connections and close them on eviction to prevent resource exhaustion.
 - Improve logging for malformed discv4 UDP packets.
 - Bound the snap sync storage sub-range split count to prevent unbounded memory growth under a malformed snap response.
 - Added a configurable range cap (--graphql-max-blocks-range, default 5000) for GraphQL blocks(from, to) range queries; queries exceeding the cap are cancelled.
 - Bound secp256k1 signature r and s values to [1, n) on signature recovery, fixing a consensus divergence with EIP-7702 code delegations.
-- Reject RLP-wrapped typed transactions in block-body opaque decoding, preventing a potential consensus divergence.
 - Add a server-side cap on EVM steps captured per debug_traceCall, debug_traceTransaction, and related trace methods to prevent unbounded execution.
+- Apply --rpc-max-logs-range to eth_getFilterLogs and eth_newFilter to prevent unbounded log queries.
 - Fix optimistic parallel execution materialising an empty account for an unrewarded fee recipient, causing incorrect EIP-158 account deletion.
 - Remove `System.out`/`System.err` logging from `P256VerifyPrecompiledContract` and `BlockchainQueries` — these could leak sensitive data to stdout/stderr in production.
 - EIP-1459 DNS discovery now rejoins TXT records split across multiple `<character-string>`s. Records longer than 255 bytes were truncated, so Besu silently discarded most of every tree, resolving 832 of 3000 nodes from the mainnet tree. [#10985](https://github.com/besu-eth/besu/pull/10985)
@@ -102,6 +101,9 @@
 - Fix `ibft_*` and `qbft_*` JSON-RPC methods returning `Method not enabled` on IBFT2->QBFT migration networks (genesis containing both `ibft2` and `qbft` sections). [#10679](https://github.com/besu-eth/besu/issues/10679)
 - Fix `admin_nodeInfo` reporting wrong RLPx/discovery ephemeral ports under `--nat-method=DOCKER`, due to a swapped NAT port mapping and a stale pre-bind snapshot. [#10860](https://github.com/besu-eth/besu/pull/10860)
 - Recover from restart during flatDB heal sync step [#10883](https://github.com/besu-eth/besu/pull/10883)
+- Cap pre-STATUS RLPx connections and close them on eviction to prevent resource exhaustion.
+- Fix txpool incorrectly evicting authority pending transactions when EIP-7702 delegation tuples are skipped during block execution
+- Reject RLP-wrapped typed transactions in block-body opaque decoding, preventing a potential consensus divergence.
 
 ### Additions and Improvements
 - Add `--checkpoint=<hash>:<number>:<totalDifficulty>` CLI option to anchor sync to a trusted checkpoint, overriding any checkpoint configured in the genesis file. The option is only used by snap sync and is ignored (with a warning) in FULL sync-mode.
```

### app/src/main/java/org/hyperledger/besu/RunnerBuilder.java
```diff
@@ -886,6 +886,7 @@ public Runner build() {
         new FilterManagerBuilder()
             .blockchainQueries(blockchainQueries)
             .transactionPool(transactionPool)
+            .maxLogRange(apiConfiguration.getMaxLogsRange())
             .maxFilterCount(apiConfiguration.getMaxFilterCount())
             .filterTimeout(apiConfiguration.getFilterTimeout())
             .build();
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/ApiConfiguration.java
```diff
@@ -123,7 +123,7 @@ public double getGasPriceFraction() {
    */
   @Value.Default
   public Long getMaxLogsRange() {
-    return 5000L;
+    return DEFAULT_MAX_LOGS_RANGE;
   }
 
   /**
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/jsonrpc/internal/filter/FilterManager.java
```diff
@@ -18,7 +18,9 @@
 import static java.util.stream.Collectors.toUnmodifiableList;
 
 import org.hyperledger.besu.datatypes.Hash;
+import org.hyperledger.besu.ethereum.api.jsonrpc.internal.exception.InvalidJsonRpcParameters;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.parameters.BlockParameter;
+import org.hyperledger.besu.ethereum.api.jsonrpc.internal.response.RpcErrorType;
 import org.hyperledger.besu.ethereum.api.query.BlockchainQueries;
 import org.hyperledger.besu.ethereum.api.query.LogsQuery;
 import org.hyperledger.besu.ethereum.chain.BlockAddedEvent;
@@ -31,6 +33,7 @@
 import java.util.Collection;
 import java.util.List;
 import java.util.Optional;
+import java.util.function.Supplier;
 
 import com.google.common.annotations.VisibleForTesting;
 import io.vertx.core.AbstractVerticle;
@@ -43,17 +46,20 @@ public class FilterManager extends AbstractVerticle {
   private final FilterIdGenerator filterIdGenerator;
   private final FilterRepository filterRepository;
   private final BlockchainQueries blockchainQueries;
+  private final long maxLogRange;
   private final Duration filterTimeout;
 
   FilterManager(
       final BlockchainQueries blockchainQueries,
       final TransactionPool transactionPool,
       final FilterIdGenerator filterIdGenerator,
       final FilterRepository filterRepository,
-      final Duration filterTimeout) {
+      final Duration filterTimeout,
+      final long maxLogRange) {
     this.filterIdGenerator = filterIdGenerator;
     this.filterRepository = filterRepository;
     this.filterTimeout = filterTimeout;
+    this.maxLogRange = maxLogRange;
     checkNotNull(blockchainQueries.getBlockchain());
     blockchainQueries.getBlockchain().observeBlockAdded(this::recordBlockEvent);
     transactionPool.subscribePendingTransactions(this::recordPendingTransactionEvent);
@@ -236,24 +242,44 @@ public List<LogWithMetadata> logsChanges(final String filterId) {
     return logs;
   }
 
-  public List<LogWithMetadata> logs(final String filterId) {
+  public List<LogWithMetadata> logs(final String filterId, final Supplier<Boolean> isAlive) {
     final LogFilter filter = filterRepository.getFilter(filterId, LogFilter.class).orElse(null);
     if (filter == null) {
       return null;
     } else {
       filter.resetExpireTime();
     }
 
+    // Read head exactly once so that LATEST..LATEST filters always refer to the same block,
+    // avoiding a race where a new block lands between the two reads and shifts the range.
     final long headBlockNumber = blockchainQueries.headBlockNumber();
-    final long fromBlockNumber = filter.getFromBlock().getNumber().orElse(headBlockNumber);
-    final long toBlockNumber = filter.getToBlock().getNumber().orElse(headBlockNumber);
+    final long fromBlockNumber = resolveFilterBlockNumber(filter.getFromBlock(), headBlockNumber);
+    final long toBlockNumber = resolveFilterBlockNumber(filter.getToBlock(), headBlockNumber);
 
-    return findLogsWithinRange(filter, fromBlockNumber, toBlockNumber);
+    if (maxLogRange > 0 && (toBlockNumber - fromBlockNumber) > maxLogRange) {
+      throw new InvalidJsonRpcParameters(
+          "Requested range exceeds maximum range limit", RpcErrorType.EXCEEDS_RPC_MAX_BLOCK_RANGE);
+    }
+
+    return findLogsWithinRange(filter, fromBlockNumber, toBlockNumber, isAlive);
+  }
+
+  // Resolves a filter block parameter to a concrete block number without calling headBlockNumber()
+  // again. FINALIZED and SAFE are looked up via the chain; everything else (LATEST, PENDING,
+  // NUMERIC, EARLIEST) either returns its stored number or falls back to the already-read head.
+  private long resolveFilterBlockNumber(final BlockParameter param, final long headBlockNumber) {
+    if (param.isFinalized() || param.isSafe()) {
+      return param.getBlockNumber(blockchainQueries).orElse(headBlockNumber);
+    }
+    return param.getNumber().orElse(headBlockNumber);
   }
 
   private List<LogWithMetadata> findLogsWithinRange(
-      final LogFilter filter, final long fromBlockNumber, final long toBlockNumber) {
+      final LogFilter filter,
+      final long fromBlockNumber,
+      final long toBlockNumber,
+      final Supplier<Boolean> isAlive) {
     return blockchainQueries.matchingLogs(
-        fromBlockNumber, toBlockNumber, filter.getLogsQuery(), () -> true);
+        fromBlockNumber, toBlockNumber, filter.getLogsQuery(), isAlive);
   }
 }
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/jsonrpc/internal/filter/FilterManagerBuilder.java
```diff
@@ -26,6 +26,7 @@ public class FilterManagerBuilder {
   private TransactionPool transactionPool;
   private FilterIdGenerator filterIdGenerator = new FilterIdGenerator();
   private FilterRepository filterRepository;
+  private long maxLogRange = ApiConfiguration.DEFAULT_MAX_LOGS_RANGE;
   private int maxFilterCount = ApiConfiguration.DEFAULT_MAX_FILTER_COUNT;
   private Duration filterTimeout = ApiConfiguration.DEFAULT_FILTER_TIMEOUT;
 
@@ -72,6 +73,11 @@ public FilterManagerBuilder transactionPool(final TransactionPool transactionPoo
     return this;
   }
 
+  public FilterManagerBuilder maxLogRange(final long maxLogRange) {
+    this.maxLogRange = maxLogRange;
+    return this;
+  }
+
   public FilterManager build() {
     if (blockchainQueries == null) {
       throw new IllegalStateException("BlockchainQueries is required to build FilterManager");
@@ -85,6 +91,11 @@ public FilterManager build() {
         filterRepository != null ? filterRepository : new FilterRepository(maxFilterCount);
 
     return new FilterManager(
-        blockchainQueries, transactionPool, filterIdGenerator, repository, filterTimeout);
+        blockchainQueries,
+        transactionPool,
+        filterIdGenerator,
+        repository,
+        filterTimeout,
+        maxLogRange);
   }
 }
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/jsonrpc/internal/methods/EthGetFilterLogs.java
```diff
@@ -27,6 +27,7 @@
 import org.hyperledger.besu.ethereum.core.LogWithMetadata;
 
 import java.util.List;
+import java.util.function.Supplier;
 
 public class EthGetFilterLogs implements JsonRpcMethod {
 
@@ -51,7 +52,9 @@ public JsonRpcResponse response(final JsonRpcRequestContext requestContext) {
           "Invalid filter ID parameter (index 0)", RpcErrorType.INVALID_FILTER_PARAMS, e);
     }
 
-    final List<LogWithMetadata> logs = filterManager.logs(filterId);
+    final Supplier<Boolean> isAlive = requestContext::isAlive;
+    final List<LogWithMetadata> logs = filterManager.logs(filterId, isAlive);
+
     if (logs != null) {
       return new JsonRpcSuccessResponse(requestContext.getRequest().getId(), new LogsResult(logs));
     }
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/jsonrpc/internal/methods/EthNewFilter.java
```diff
@@ -25,13 +25,21 @@
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.response.JsonRpcResponse;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.response.JsonRpcSuccessResponse;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.response.RpcErrorType;
+import org.hyperledger.besu.ethereum.api.query.BlockchainQueries;
 
 public class EthNewFilter implements JsonRpcMethod {
 
   private final FilterManager filterManager;
+  private final BlockchainQueries blockchainQueries;
+  private final long maxLogRange;
 
-  public EthNewFilter(final FilterManager filterManager) {
+  public EthNewFilter(
+      final FilterManager filterManager,
+      final BlockchainQueries blockchainQueries,
+      final long maxLogRange) {
     this.filterManager = filterManager;
+    this.blockchainQueries = blockchainQueries;
+    this.maxLogRange = maxLogRange;
   }
 
   @Override
@@ -54,6 +62,19 @@ public JsonRpcResponse response(final JsonRpcRequestContext requestContext) {
           requestContext.getRequest().getId(), RpcErrorType.INVALID_FILTER_PARAMS);
     }
 
+    if (maxLogRange > 0) {
+      final long headBlockNumber = blockchainQueries.headBlockNumber();
+      final long fromBlockNumber =
+          filter.getFromBlock().getBlockNumber(blockchainQueries).orElse(headBlockNumber);
+      final long toBlockNumber =
+          filter.getToBlock().getBlockNumber(blockchainQueries).orElse(headBlockNumber);
+      FilterParameter.validateBlockRange(fromBlockNumber, toBlockNumber, headBlockNumber);
+      if (toBlockNumber - fromBlockNumber > maxLogRange) {
+        return new JsonRpcErrorResponse(
+            requestContext.getRequest().getId(), RpcErrorType.EXCEEDS_RPC_MAX_BLOCK_RANGE);
+      }
+    }
+
     final String logFilterId;
     try {
       logFilterId =
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/jsonrpc/methods/EthJsonRpcMethods.java
```diff
@@ -157,7 +157,7 @@ protected Map<String, JsonRpcMethod> create() {
             new EthGetUncleByBlockHashAndIndex(blockchainQueries),
             new EthNewBlockFilter(filterManager),
             new EthNewPendingTransactionFilter(filterManager),
-            new EthNewFilter(filterManager),
+            new EthNewFilter(filterManager, blockchainQueries, apiConfiguration.getMaxLogsRange()),
             new EthGetTransactionByHash(blockchainQueries, transactionPool),
             new EthGetTransactionByBlockHashAndIndex(blockchainQueries),
             new EthGetTransactionByBlockNumberAndIndex(blockchainQueries),
```

### ethereum/api/src/test/java/org/hyperledger/besu/ethereum/api/jsonrpc/internal/filter/FilterManagerLogFilterTest.java
```diff
@@ -173,7 +173,7 @@ private List<BlockAddedEvent> recordBlockEvents(final int numEvents) {
 
   @Test
   public void getLogsForAbsentFilterReturnsNull() {
-    assertThat(filterManager.logs("NOTTHERE")).isNull();
+    assertThat(filterManager.logs("NOTTHERE", () -> true)).isNull();
   }
 
   @Test
@@ -184,7 +184,7 @@ public void getLogsForExistingFilterReturnsResults() {
         .thenReturn(singletonList(log));
 
     final String filterId = filterManager.installLogFilter(latest(), latest(), logsQuery());
-    final List<LogWithMetadata> retrievedLogs = filterManager.logs(filterId);
+    final List<LogWithMetadata> retrievedLogs = filterManager.logs(filterId, () -> true);
 
     assertThat(retrievedLogs).usingRecursiveComparison().isEqualTo(singletonList(log));
   }
@@ -206,7 +206,7 @@ public void getLogsShouldResetFilterExpireDate() {
         spy(new LogFilter("foo", latest(), latest(), logsQuery(), DEFAULT_FILTER_TIMEOUT));
     doReturn(Optional.of(filter)).when(filterRepository).getFilter(eq("foo"), eq(LogFilter.class));
 
-    filterManager.logs("foo");
+    filterManager.logs("foo", () -> true);
 
     verify(filter).resetExpireTime();
   }
```

### ethereum/api/src/test/java/org/hyperledger/besu/ethereum/api/jsonrpc/internal/filter/FilterManagerTest.java
```diff
@@ -15,6 +15,7 @@
 package org.hyperledger.besu.ethereum.api.jsonrpc.internal.filter;
 
 import static org.assertj.core.api.Assertions.assertThat;
+import static org.assertj.core.api.Assertions.assertThatThrownBy;
 import static org.hyperledger.besu.ethereum.api.ApiConfiguration.DEFAULT_FILTER_TIMEOUT;
 import static org.hyperledger.besu.ethereum.api.ApiConfiguration.DEFAULT_MAX_FILTER_COUNT;
 import static org.mockito.ArgumentMatchers.any;
@@ -27,6 +28,7 @@
 import static org.mockito.Mockito.when;
 
 import org.hyperledger.besu.datatypes.Hash;
+import org.hyperledger.besu.ethereum.api.jsonrpc.internal.exception.InvalidJsonRpcParameters;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.parameters.BlockParameter;
 import org.hyperledger.besu.ethereum.api.query.BlockchainQueries;
 import org.hyperledger.besu.ethereum.api.query.LogsQuery;
@@ -257,12 +259,39 @@ public void logsForLatestLatestFilterResolvesHeadOnce() {
     when(blockchainQueries.matchingLogs(anyLong(), anyLong(), any(LogsQuery.class), any()))
         .thenReturn(Collections.emptyList());
 
-    filterManager.logs(filterId);
+    filterManager.logs(filterId, () -> true);
 
     verify(blockchainQueries, times(1)).headBlockNumber();
     verify(blockchainQueries).matchingLogs(eq(100L), eq(100L), eq(logsQuery), any());
   }
 
+  // A filter installed within the range limit must be rejected by logs() if the head has
+  // advanced far enough that the range now exceeds maxLogRange (LATEST resolves at query time,
+  // not at install time).
+  @Test
+  public void logsThrowsWhenRangeExceedsLimitAfterHeadAdvances() {
+    final long maxLogRange = 5L;
+    final FilterManager rangedFilterManager =
+        new FilterManagerBuilder()
+            .blockchainQueries(blockchainQueries)
+            .transactionPool(transactionPool)
+            .filterRepository(new FilterRepository(DEFAULT_MAX_FILTER_COUNT))
+            .maxLogRange(maxLogRange)
+            .build();
+
+    // fromBlock = 100 (explicit), toBlock = LATEST — no range check at install time
+    final String filterId =
+        rangedFilterManager.installLogFilter(
+            new BlockParameter(100L), BlockParameter.LATEST, new LogsQuery.Builder().build());
+
+    // Head has advanced to 106: range = 106 - 100 = 6, which exceeds maxLogRange (5)
+    when(blockchainQueries.headBlockNumber()).thenReturn(106L);
+
+    assertThatThrownBy(() -> rangedFilterManager.logs(filterId, () -> true))
+        .isInstanceOf(InvalidJsonRpcParameters.class)
+        .hasMessageContaining("Requested range exceeds maximum range limit");
+  }
+
   private Hash appendBlockToBlockchain() {
     final long blockNumber = currentBlock.getHeader().getNumber() + 1;
     final Hash parentHash = currentBlock.getHash();
```

### ethereum/api/src/test/java/org/hyperledger/besu/ethereum/api/jsonrpc/internal/methods/EthGetFilterLogsTest.java
```diff
@@ -16,6 +16,7 @@
 
 import static org.assertj.core.api.Assertions.assertThat;
 import static org.assertj.core.api.Assertions.catchThrowable;
+import static org.mockito.ArgumentMatchers.any;
 import static org.mockito.ArgumentMatchers.eq;
 import static org.mockito.Mockito.verifyNoInteractions;
 import static org.mockito.Mockito.when;
@@ -92,7 +93,7 @@ public void shouldReturnFilterNotFoundWhenFilterManagerReturnsNull() {
     final JsonRpcRequestContext request = requestWithFilterId("NOT FOUND");
     final JsonRpcResponse expectedResponse =
         new JsonRpcErrorResponse(null, RpcErrorType.LOGS_FILTER_NOT_FOUND);
-    when(filterManager.logs(eq("NOT FOUND"))).thenReturn(null);
+    when(filterManager.logs(eq("NOT FOUND"), any())).thenReturn(null);
 
     final JsonRpcResponse response = method.response(request);
 
@@ -104,7 +105,7 @@ public void shouldReturnEmptyListWhenFilterManagerReturnsEmpty() {
     final JsonRpcRequestContext request = requestWithFilterId("0x1");
     final JsonRpcResponse expectedResponse =
         new JsonRpcSuccessResponse(null, new LogsResult(new ArrayList<>()));
-    when(filterManager.logs(eq("0x1"))).thenReturn(new ArrayList<>());
+    when(filterManager.logs(eq("0x1"), any())).thenReturn(new ArrayList<>());
 
     final JsonRpcResponse response = method.response(request);
 
@@ -116,7 +117,7 @@ public void shouldReturnExpectedLogsWhenFilterManagerReturnsLogs() {
     final JsonRpcRequestContext request = requestWithFilterId("0x1");
     final JsonRpcResponse expectedResponse =
         new JsonRpcSuccessResponse(null, new LogsResult(logs()));
-    when(filterManager.logs(eq("0x1"))).thenReturn(logs());
+    when(filterManager.logs(eq("0x1"), any())).thenReturn(logs());
 
     final JsonRpcResponse response = method.response(request);
 
```

### ethereum/api/src/test/java/org/hyperledger/besu/ethereum/api/jsonrpc/internal/methods/EthNewFilterTest.java
```diff
@@ -35,6 +35,7 @@
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.response.JsonRpcResponse;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.response.JsonRpcSuccessResponse;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.response.RpcErrorType;
+import org.hyperledger.besu.ethereum.api.query.BlockchainQueries;
 import org.hyperledger.besu.ethereum.api.query.LogsQuery;
 
 import java.util.Collections;
@@ -51,12 +52,13 @@
 public class EthNewFilterTest {
 
   @Mock private FilterManager filterManager;
+  @Mock private BlockchainQueries blockchainQueries;
   private EthNewFilter method;
   private final String ETH_METHOD = "eth_newFilter";
 
   @BeforeEach
   public void setUp() {
-    method = new EthNewFilter(filterManager);
+    method = new EthNewFilter(filterManager, blockchainQueries, 0);
   }
 
   @Test
@@ -165,6 +167,30 @@ public void newFilterWithAddressAndTopicsParamInstallsExpectedLogFilter() {
             refEq(BlockParameter.LATEST), refEq(BlockParameter.LATEST), eq(expectedLogsQuery));
   }
 
+  @Test
+  public void filterWithRangeExceedingMaxLogRangeReturnsError() {
+    when(blockchainQueries.headBlockNumber()).thenReturn(10000L);
+    final EthNewFilter methodWithLimit = new EthNewFilter(filterManager, blockchainQueries, 100);
+    final FilterParameter filterParameter =
+        new FilterParameter(
+            new BlockParameter(0L),
+            new BlockParameter(5000L),
+            null,
+            null,
+            null,
+            null,
+            null,
+            null,
+            null);
+    final JsonRpcRequestContext request = ethNewFilter(filterParameter);
+    final JsonRpcResponse expectedResponse =
+        new JsonRpcErrorResponse(null, RpcErrorType.EXCEEDS_RPC_MAX_BLOCK_RANGE);
+
+    final JsonRpcResponse response = methodWithLimit.response(request);
+
+    assertThat(response).usingRecursiveComparison().isEqualTo(expectedResponse);
+  }
+
   @Test
   public void filterWithInvalidParameters() {
     final FilterParameter invalidFilter =
```
