# [?] Fixes: GHSA-p6f8-q9mp-7mj9 Cap log filter addresses and apply bloom pre-filter on block import (#104)

## Summary
Severity: Unknown
Chain: Ethereum
Component: hyperledger/besu
Published: 2026-08-28
Source: https://github.com/besu-eth/besu/commit/dc62887182c51d186df2dca031618e8b1a460331
Type: security-commit

## Details
Fixes: GHSA-p6f8-q9mp-7mj9 Cap log filter addresses and apply bloom pre-filter on block import (#104)

* Fixes: GHSA-p6f8-q9mp-7mj9 Cap log filter addresses and apply bloom pre-filter on block import

Three changes to address unbounded address cardinality in log filters causing
CPU-exhaustion on the block-import thread:

1. Apply existing bloom pre-filter (LogsQuery.couldMatch) in
   FilterManager.recordBlockEvent before scanning logs per-filter. This matches
   the optimization already used by eth_getLogs and skips non-matching filters
   in O(bloom-size) rather than O(logs * addresses).

2. Cap the number of addresses per log filter/subscription at 1000 by default
   (--rpc-max-log-filter-addresses, 0 = no limit). Validated at filter-creation
   time in EthNewFilter and EthSubscribe; exceeding the cap returns -32005.

3. Store filter addresses in a HashSet rather than ArrayList so membership
   tests are O(1) instead of O(n), and duplicate addresses are deduplicated.

---------

Signed-off-by: Sally MacFarlane <macfarla.github@gmail.com>
Co-authored-by: Claude Sonnet 4.6 <noreply@anthropic.com>
Co-authored-by: Justin Florentine <justin+github@florentine.us>
Signed-off-by: Sally MacFarlane <macfarla.github@gmail.com>

## Patch
### app/src/main/java/org/hyperledger/besu/RunnerBuilder.java
```diff
@@ -1032,7 +1032,8 @@ public Runner build() {
               : WebSocketConfiguration.createEngineDefault();
 
       final WebSocketMethodsFactory websocketMethodsFactory =
-          new WebSocketMethodsFactory(subscriptionManager, engineMethods);
+          new WebSocketMethodsFactory(
+              subscriptionManager, engineMethods, apiConfiguration.getMaxFilterAddresses());
 
       engineJsonRpcService =
           Optional.of(
@@ -1182,7 +1183,8 @@ public Runner build() {
               besuController.getProtocolManager().ethContext().getScheduler());
 
       final WebSocketMethodsFactory ipcMethodsFactory =
-          new WebSocketMethodsFactory(subscriptionManager, ipcMethods);
+          new WebSocketMethodsFactory(
+              subscriptionManager, ipcMethods, apiConfiguration.getMaxFilterAddresses());
 
       jsonRpcIpcService =
           Optional.of(
@@ -1510,7 +1512,8 @@ private WebSocketService createWebsocketService(
       final ObservableMetricsSystem metricsSystem) {
 
     final WebSocketMethodsFactory websocketMethodsFactory =
-        new WebSocketMethodsFactory(subscriptionManager, jsonRpcMethods);
+        new WebSocketMethodsFactory(
+            subscriptionManager, jsonRpcMethods, apiConfiguration.getMaxFilterAddresses());
 
     rpcEndpointServiceImpl
         .getPluginMethods(configuration.getRpcApis())
```

### app/src/main/java/org/hyperledger/besu/cli/options/ApiConfigurationOptions.java
```diff
@@ -119,6 +119,13 @@ public ApiConfigurationOptions() {}
           "Server-side cap on EVM steps captured per debug_trace*/trace_call request. Callers may request fewer steps but not more. Must be >=0. 0 disables the cap (default: ${DEFAULT-VALUE})")
   private final Long rpcMaxTraceSteps = ApiConfiguration.DEFAULT_DEBUG_TRACE_STEP_LIMIT;
 
+  @CommandLine.Option(
+      names = {"--rpc-max-log-filter-addresses"},
+      description =
+          "Maximum number of addresses permitted in a single eth_newFilter or eth_subscribe logs "
+              + "request. Must be >=0. 0 specifies no limit (default: ${DEFAULT-VALUE})")
+  private final Integer rpcMaxLogFilterAddresses = ApiConfiguration.DEFAULT_MAX_FILTER_ADDRESSES;
+
   /**
    * Validates the API options.
    *
@@ -137,6 +144,10 @@ public void validate(final CommandLine commandLine, final Logger logger) {
       throw new CommandLine.ParameterException(
           commandLine, "--rpc-max-active-filters must be >= 0 (0 specifies no limit)");
     }
+    if (rpcMaxLogFilterAddresses < 0) {
+      throw new CommandLine.ParameterException(
+          commandLine, "--rpc-max-log-filter-addresses must be >= 0 (0 specifies no limit)");
+    }
     if (rpcFilterTimeoutSeconds <= 0) {
       throw new CommandLine.ParameterException(
           commandLine, "--rpc-filter-timeout-seconds must be > 0");
@@ -173,7 +184,8 @@ public ApiConfiguration apiConfiguration() {
             .maxTraceFilterRange(maxTraceFilterRange)
             .maxFilterCount(rpcMaxActiveFilters)
             .filterTimeout(Duration.ofSeconds(rpcFilterTimeoutSeconds))
-            .debugTraceStepLimit(rpcMaxTraceSteps);
+            .debugTraceStepLimit(rpcMaxTraceSteps)
+            .maxFilterAddresses(rpcMaxLogFilterAddresses);
     if (apiGasAndPriorityFeeLimitingEnabled) {
       builder
           .lowerBoundGasAndPriorityFeeCoefficient(apiGasAndPriorityFeeLowerBoundCoefficient)
```

### app/src/test/resources/everything_config.toml
```diff
@@ -112,6 +112,7 @@ rpc-max-trace-filter-range=100
 rpc-max-active-filters=1000
 rpc-filter-timeout-seconds=60
 rpc-max-trace-steps=2000
+rpc-max-log-filter-addresses=500
 
 # GRAPHQL HTTP
 graphql-http-enabled=false
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/ApiConfiguration.java
```diff
@@ -60,6 +60,9 @@ public abstract class ApiConfiguration {
   /** The default maximum block range for log filter queries. */
   public static final long DEFAULT_MAX_LOGS_RANGE = 5000L;
 
+  /** The default maximum number of addresses allowed per log filter or log subscription. */
+  public static final int DEFAULT_MAX_FILTER_ADDRESSES = 1000;
+
   /** Constructs a new ApiConfiguration with default values. */
   protected ApiConfiguration() {}
 
@@ -209,4 +212,15 @@ public Duration getFilterTimeout() {
   public Long getDebugTraceStepLimit() {
     return DEFAULT_DEBUG_TRACE_STEP_LIMIT;
   }
+
+  /**
+   * Returns the maximum number of addresses permitted per log filter or log subscription. Zero
+   * means uncapped (operator opt-out).
+   *
+   * @return the maximum address count per filter, or 0 for unlimited
+   */
+  @Value.Default
+  public Integer getMaxFilterAddresses() {
+    return DEFAULT_MAX_FILTER_ADDRESSES;
+  }
 }
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/jsonrpc/internal/filter/FilterManager.java
```diff
@@ -18,6 +18,7 @@
 import static java.util.stream.Collectors.toUnmodifiableList;
 
 import org.hyperledger.besu.datatypes.Hash;
+import org.hyperledger.besu.datatypes.LogsBloomFilter;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.exception.InvalidJsonRpcParameters;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.parameters.BlockParameter;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.response.RpcErrorType;
@@ -146,6 +147,7 @@ public void recordBlockEvent(final BlockAddedEvent event) {
         });
 
     final List<LogWithMetadata> logsWithMetadata = event.getLogsWithMetadata();
+    final LogsBloomFilter blockBloom = event.getHeader().getLogsBloom();
     filterRepository.getFiltersOfType(LogFilter.class).stream()
         .filter(
             // Only keep filters where the "to" block could include the block in the event
@@ -154,6 +156,7 @@ public void recordBlockEvent(final BlockAddedEvent event) {
               return maybeToBlockNumber.isEmpty()
                   || maybeToBlockNumber.get() >= event.getHeader().getNumber();
             })
+        .filter(filter -> filter.getLogsQuery().couldMatch(blockBloom))
         .forEach(
             filter -> {
               final LogsQuery logsQuery = filter.getLogsQuery();
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/jsonrpc/internal/methods/EthNewFilter.java
```diff
@@ -32,14 +32,17 @@ public class EthNewFilter implements JsonRpcMethod {
   private final FilterManager filterManager;
   private final BlockchainQueries blockchainQueries;
   private final long maxLogRange;
+  private final int maxFilterAddresses;
 
   public EthNewFilter(
       final FilterManager filterManager,
       final BlockchainQueries blockchainQueries,
-      final long maxLogRange) {
+      final long maxLogRange,
+      final int maxFilterAddresses) {
     this.filterManager = filterManager;
     this.blockchainQueries = blockchainQueries;
     this.maxLogRange = maxLogRange;
+    this.maxFilterAddresses = maxFilterAddresses;
   }
 
   @Override
@@ -62,6 +65,11 @@ public JsonRpcResponse response(final JsonRpcRequestContext requestContext) {
           requestContext.getRequest().getId(), RpcErrorType.INVALID_FILTER_PARAMS);
     }
 
+    if (maxFilterAddresses > 0 && filter.getAddresses().size() > maxFilterAddresses) {
+      return new JsonRpcErrorResponse(
+          requestContext.getRequest().getId(), RpcErrorType.EXCEEDS_RPC_MAX_FILTER_ADDRESSES);
+    }
+
     if (maxLogRange > 0) {
       final long headBlockNumber = blockchainQueries.headBlockNumber();
       final long fromBlockNumber =
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/jsonrpc/internal/response/RpcErrorType.java
```diff
@@ -162,6 +162,7 @@ public enum RpcErrorType implements RpcMethodError {
   EXCEEDS_RPC_MAX_BLOCK_RANGE(-32005, "Requested range exceeds maximum RPC range limit"),
   EXCEEDS_RPC_MAX_BATCH_SIZE(-32005, "Number of requests exceeds max batch size"),
   EXCEEDS_RPC_MAX_ACTIVE_FILTERS(-32005, "Maximum number of active filters exceeded"),
+  EXCEEDS_RPC_MAX_FILTER_ADDRESSES(-32005, "Filter address count exceeds limit"),
   NONCE_TOO_HIGH(-32006, "Nonce too high"),
   TX_SENDER_NOT_AUTHORIZED(-32007, "Sender account not authorized to send transactions"),
   CHAIN_HEAD_WORLD_STATE_NOT_AVAILABLE(-32008, "Initial sync is still in progress"),
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/jsonrpc/methods/EthJsonRpcMethods.java
```diff
@@ -157,7 +157,11 @@ protected Map<String, JsonRpcMethod> create() {
             new EthGetUncleByBlockHashAndIndex(blockchainQueries),
             new EthNewBlockFilter(filterManager),
             new EthNewPendingTransactionFilter(filterManager),
-            new EthNewFilter(filterManager, blockchainQueries, apiConfiguration.getMaxLogsRange()),
+            new EthNewFilter(
+                filterManager,
+                blockchainQueries,
+                apiConfiguration.getMaxLogsRange(),
+                apiConfiguration.getMaxFilterAddresses()),
             new EthGetTransactionByHash(blockchainQueries, transactionPool),
             new EthGetTransactionByBlockHashAndIndex(blockchainQueries),
             new EthGetTransactionByBlockNumberAndIndex(blockchainQueries),
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/jsonrpc/websocket/methods/EthSubscribe.java
```diff
@@ -16,6 +16,7 @@
 
 import org.hyperledger.besu.ethereum.api.jsonrpc.RpcMethod;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.JsonRpcRequestContext;
+import org.hyperledger.besu.ethereum.api.jsonrpc.internal.parameters.FilterParameter;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.response.JsonRpcErrorResponse;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.response.JsonRpcResponse;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.response.JsonRpcSuccessResponse;
@@ -26,12 +27,18 @@
 import org.hyperledger.besu.ethereum.api.jsonrpc.websocket.subscription.request.InvalidSubscriptionRequestException;
 import org.hyperledger.besu.ethereum.api.jsonrpc.websocket.subscription.request.SubscribeRequest;
 import org.hyperledger.besu.ethereum.api.jsonrpc.websocket.subscription.request.SubscriptionRequestMapper;
+import org.hyperledger.besu.ethereum.api.jsonrpc.websocket.subscription.request.SubscriptionType;
 
 public class EthSubscribe extends AbstractSubscriptionMethod {
 
+  private final int maxFilterAddresses;
+
   EthSubscribe(
-      final SubscriptionManager subscriptionManager, final SubscriptionRequestMapper mapper) {
+      final SubscriptionManager subscriptionManager,
+      final SubscriptionRequestMapper mapper,
+      final int maxFilterAddresses) {
     super(subscriptionManager, mapper);
+    this.maxFilterAddresses = maxFilterAddresses;
   }
 
   @Override
@@ -43,6 +50,16 @@ public String getName() {
   public JsonRpcResponse response(final JsonRpcRequestContext requestContext) {
     try {
       final SubscribeRequest subscribeRequest = getMapper().mapSubscribeRequest(requestContext);
+
+      if (maxFilterAddresses > 0
+          && subscribeRequest.getSubscriptionType() == SubscriptionType.LOGS) {
+        final FilterParameter fp = subscribeRequest.getFilterParameter();
+        if (fp != null && fp.getAddresses().size() > maxFilterAddresses) {
+          return new JsonRpcErrorResponse(
+              requestContext.getRequest().getId(), RpcErrorType.EXCEEDS_RPC_MAX_FILTER_ADDRESSES);
+        }
+      }
+
       final Long subscriptionId = subscriptionManager().subscribe(subscribeRequest);
 
       return new JsonRpcSuccessResponse(
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/jsonrpc/websocket/methods/WebSocketMethodsFactory.java
```diff
@@ -27,14 +27,16 @@ public class WebSocketMethodsFactory {
 
   public WebSocketMethodsFactory(
       final SubscriptionManager subscriptionManager,
-      final Map<String, JsonRpcMethod> jsonRpcMethods) {
+      final Map<String, JsonRpcMethod> jsonRpcMethods,
+      final int maxFilterAddresses) {
     this.methods.putAll(jsonRpcMethods);
-    buildWebsocketMethods(subscriptionManager);
+    buildWebsocketMethods(subscriptionManager, maxFilterAddresses);
   }
 
-  private void buildWebsocketMethods(final SubscriptionManager subscriptionManager) {
+  private void buildWebsocketMethods(
+      final SubscriptionManager subscriptionManager, final int maxFilterAddresses) {
     addMethods(
-        new EthSubscribe(subscriptionManager, new SubscriptionRequestMapper()),
+        new EthSubscribe(subscriptionManager, new SubscriptionRequestMapper(), maxFilterAddresses),
         new EthUnsubscribe(subscriptionManager, new SubscriptionRequestMapper()));
   }
 
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/query/LogsQuery.java
```diff
@@ -25,8 +25,10 @@
 
 import java.util.ArrayList;
 import java.util.Arrays;
+import java.util.HashSet;
 import java.util.List;
 import java.util.Objects;
+import java.util.Set;
 import java.util.stream.Collectors;
 import java.util.stream.IntStream;
 
@@ -38,7 +40,7 @@
 
 public class LogsQuery {
 
-  private final List<Address> addresses;
+  private final Set<Address> addresses;
   private final List<List<LogTopic>> topics;
   private final List<LogsBloomFilter> addressBlooms;
   private final List<List<LogsBloomFilter>> topicsBlooms;
@@ -55,7 +57,7 @@ public LogsQuery(
     // that won't throw a null pointer exception when checking to see if the list contains null.
     // List.of(...) is one of the lists that reacts poorly to null member checks and is something
     // that we should expect to see passed in. So we must copy into a null-tolerant list.
-    this.addresses = addresses != null ? new ArrayList<>(addresses) : emptyList();
+    this.addresses = addresses != null ? new HashSet<>(addresses) : Set.of();
     this.topics =
         topics != null
             ? topics.stream().map(ArrayList::new).collect(Collectors.toList())
```

### ethereum/api/src/test/java/org/hyperledger/besu/ethereum/api/jsonrpc/internal/methods/EthNewFilterTest.java
```diff
@@ -38,9 +38,12 @@
 import org.hyperledger.besu.ethereum.api.query.BlockchainQueries;
 import org.hyperledger.besu.ethereum.api.query.LogsQuery;
 
+import java.util.ArrayList;
 import java.util.Collections;
 import java.util.List;
 import java.util.Optional;
+import java.util.stream.Collectors;
+import java.util.stream.IntStream;
 
 import org.junit.jupiter.api.BeforeEach;
 import org.junit.jupiter.api.Test;
@@ -58,7 +61,7 @@ public class EthNewFilterTest {
 
   @BeforeEach
   public void setUp() {
-    method = new EthNewFilter(filterManager, blockchainQueries, 0);
+    method = new EthNewFilter(filterManager, blockchainQueries, 0, 0);
   }
 
   @Test
@@ -170,7 +173,7 @@ public void newFilterWithAddressAndTopicsParamInstallsExpectedLogFilter() {
   @Test
   public void filterWithRangeExceedingMaxLogRangeReturnsError() {
     when(blockchainQueries.headBlockNumber()).thenReturn(10000L);
-    final EthNewFilter methodWithLimit = new EthNewFilter(filterManager, blockchainQueries, 100);
+    final EthNewFilter methodWithLimit = new EthNewFilter(filterManager, blockchainQueries, 100, 0);
     final FilterParameter filterParameter =
         new FilterParameter(
             new BlockParameter(0L),
@@ -191,6 +194,85 @@ public void filterWithRangeExceedingMaxLogRangeReturnsError() {
     assertThat(response).usingRecursiveComparison().isEqualTo(expectedResponse);
   }
 
+  @Test
+  public void filterWithAddressCountExceedingCapReturnsError() {
+    final EthNewFilter methodWithCap = new EthNewFilter(filterManager, blockchainQueries, 0, 1000);
+    final List<Address> addresses =
+        IntStream.range(0, 1001)
+            .mapToObj(i -> Address.fromHexString(String.format("0x%040x", i)))
+            .collect(Collectors.toCollection(ArrayList::new));
+    final FilterParameter filterParameter =
+        new FilterParameter(
+            BlockParameter.LATEST,
+            BlockParameter.LATEST,
+            null,
+            null,
+            addresses,
+            null,
+            null,
+            null,
+            null);
+    final JsonRpcRequestContext request = ethNewFilter(filterParameter);
+    final JsonRpcResponse expectedResponse =
+        new JsonRpcErrorResponse(null, RpcErrorType.EXCEEDS_RPC_MAX_FILTER_ADDRESSES);
+
+    final JsonRpcResponse response = methodWithCap.response(request);
+
+    assertThat(response).usingRecursiveComparison().isEqualTo(expectedResponse);
+  }
+
+  @Test
+  public void filterWithAddressCountAtCapIsAccepted() {
+    final EthNewFilter methodWithCap = new EthNewFilter(filterManager, blockchainQueries, 0, 1000);
+    final List<Address> addresses =
+        IntStream.range(0, 1000)
+            .mapToObj(i -> Address.fromHexString(String.format("0x%040x", i)))
+            .collect(Collectors.toCollection(ArrayList::new));
+    final FilterParameter filterParameter =
+        new FilterParameter(
+            BlockParameter.LATEST,
+            BlockParameter.LATEST,
+            null,
+            null,
+            addresses,
+            null,
+            null,
+            null,
+            null);
+    final JsonRpcRequestContext request = ethNewFilter(filterParameter);
+    when(filterManager.installLogFilter(any(), any(), any())).thenReturn("0x1");
+
+    final JsonRpcResponse response = methodWithCap.response(request);
+
+    assertThat(response).isInstanceOf(JsonRpcSuccessResponse.class);
+  }
+
+  @Test
+  public void filterWithAddressesAndNoCap() {
+    final List<Address> addresses =
+        IntStream.range(0, 5000)
+            .mapToObj(i -> Address.fromHexString(String.format("0x%040x", i)))
+            .collect(Collectors.toCollection(ArrayList::new));
+    final FilterParameter filterParameter =
+        new FilterParameter(
+            BlockParameter.LATEST,
+            BlockParameter.LATEST,
+            null,
+            null,
+            addresses,
+            null,
+            null,
+            null,
+            null);
+    final JsonRpcRequestContext request = ethNewFilter(filterParameter);
+    when(filterManager.installLogFilter(any(), any(), any())).thenReturn("0x1");
+
+    // default method has maxFilterAddresses=0 (no limit)
+    final JsonRpcResponse response = method.response(request);
+
+    assertThat(response).isInstanceOf(JsonRpcSuccessResponse.class);
+  }
+
   @Test
   public void filterWithInvalidParameters() {
     final FilterParameter invalidFilter =
```
