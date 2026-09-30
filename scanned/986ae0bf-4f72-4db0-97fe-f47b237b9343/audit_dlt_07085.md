# [?] Fixes: GHSA-4776-8c3f-fx7g Added server side limit for steps in debug_traceCall (#11100)

## Summary
Severity: Unknown
Chain: Ethereum
Component: hyperledger/besu
Published: 2026-08-24
Source: https://github.com/besu-eth/besu/commit/47398b0e32c07fb7447087280abe955349da1d85
Type: security-commit

## Details
Fixes: GHSA-4776-8c3f-fx7g Added server side limit for steps in debug_traceCall (#11100)

* Fixes: GHSA-4776-8c3f-fx7g Added server side limit for steps in debug_traceCall

Signed-off-by: Sally MacFarlane <macfarla.github@gmail.com>

---------

Signed-off-by: Sally MacFarlane <macfarla.github@gmail.com>

## Patch
### CHANGELOG.md
```diff
@@ -85,6 +85,7 @@
 - Added a configurable range cap (--graphql-max-blocks-range, default 5000) for GraphQL blocks(from, to) range queries; queries exceeding the cap are cancelled.
 - Bound secp256k1 signature r and s values to [1, n) on signature recovery, fixing a consensus divergence with EIP-7702 code delegations.
 - Reject RLP-wrapped typed transactions in block-body opaque decoding, preventing a potential consensus divergence.
+- Add a server-side cap on EVM steps captured per debug_traceCall, debug_traceTransaction, and related trace methods to prevent unbounded execution.
 - Remove `System.out`/`System.err` logging from `P256VerifyPrecompiledContract` and `BlockchainQueries` — these could leak sensitive data to stdout/stderr in production.
 - EIP-1459 DNS discovery now rejoins TXT records split across multiple `<character-string>`s. Records longer than 255 bytes were truncated, so Besu silently discarded most of every tree, resolving 832 of 3000 nodes from the mainnet tree. [#10985](https://github.com/besu-eth/besu/pull/10985)
 - Queue backward-sync targets received before peer readiness and retry when a peer connects. [#10843](https://github.com/besu-eth/besu/pull/10843)
```

### app/src/main/java/org/hyperledger/besu/cli/options/ApiConfigurationOptions.java
```diff
@@ -113,6 +113,12 @@ public ApiConfigurationOptions() {}
               + "before it is removed. Must be >0  (default: ${DEFAULT-VALUE})")
   private final Long rpcFilterTimeoutSeconds = ApiConfiguration.DEFAULT_FILTER_TIMEOUT.toSeconds();
 
+  @CommandLine.Option(
+      names = {"--rpc-max-trace-steps"},
+      description =
+          "Server-side cap on EVM steps captured per debug_trace*/trace_call request. Callers may request fewer steps but not more. Must be >=0. 0 disables the cap (default: ${DEFAULT-VALUE})")
+  private final Long rpcMaxTraceSteps = ApiConfiguration.DEFAULT_DEBUG_TRACE_STEP_LIMIT;
+
   /**
    * Validates the API options.
    *
@@ -166,7 +172,8 @@ public ApiConfiguration apiConfiguration() {
             .isGasAndPriorityFeeLimitingEnabled(apiGasAndPriorityFeeLimitingEnabled)
             .maxTraceFilterRange(maxTraceFilterRange)
             .maxFilterCount(rpcMaxActiveFilters)
-            .filterTimeout(Duration.ofSeconds(rpcFilterTimeoutSeconds));
+            .filterTimeout(Duration.ofSeconds(rpcFilterTimeoutSeconds))
+            .debugTraceStepLimit(rpcMaxTraceSteps);
     if (apiGasAndPriorityFeeLimitingEnabled) {
       builder
           .lowerBoundGasAndPriorityFeeCoefficient(apiGasAndPriorityFeeLowerBoundCoefficient)
```

### app/src/test/resources/everything_config.toml
```diff
@@ -111,6 +111,7 @@ rpc-gas-cap = 50000000
 rpc-max-trace-filter-range=100
 rpc-max-active-filters=1000
 rpc-filter-timeout-seconds=60
+rpc-max-trace-steps=2000
 
 # GRAPHQL HTTP
 graphql-http-enabled=false
```

### ethereum/api/src/integration-test/java/org/hyperledger/besu/ethereum/api/jsonrpc/JsonRpcTestMethodsFactory.java
```diff
@@ -166,6 +166,14 @@ public BigInteger getChainId() {
     return protocolSchedule.getChainId().get();
   }
 
+  public ProtocolSchedule getProtocolSchedule() {
+    return protocolSchedule;
+  }
+
+  public TransactionSimulator getTransactionSimulator() {
+    return transactionSimulator;
+  }
+
   public Map<String, JsonRpcMethod> methods() {
     final P2PNetwork peerDiscovery = mock(P2PNetwork.class);
     final EthPeers ethPeers = mock(EthPeers.class);
```

### ethereum/api/src/integration-test/java/org/hyperledger/besu/ethereum/api/jsonrpc/methods/DebugTraceCallStepLimitIntegrationTest.java
```diff
@@ -0,0 +1,143 @@
+/*
+ * Copyright contributors to Besu.
+ *
+ * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
+ * the License. You may obtain a copy of the License at
+ *
+ * http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
+ * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
+ * specific language governing permissions and limitations under the License.
+ *
+ * SPDX-License-Identifier: Apache-2.0
+ */
+package org.hyperledger.besu.ethereum.api.jsonrpc.methods;
+
+import static org.assertj.core.api.Assertions.assertThat;
+
+import org.hyperledger.besu.datatypes.Address;
+import org.hyperledger.besu.datatypes.StateOverride;
+import org.hyperledger.besu.datatypes.StateOverrideMap;
+import org.hyperledger.besu.ethereum.api.ImmutableApiConfiguration;
+import org.hyperledger.besu.ethereum.api.jsonrpc.BlockchainImporter;
+import org.hyperledger.besu.ethereum.api.jsonrpc.JsonRpcTestMethodsFactory;
+import org.hyperledger.besu.ethereum.api.jsonrpc.internal.JsonRpcRequest;
+import org.hyperledger.besu.ethereum.api.jsonrpc.internal.JsonRpcRequestContext;
+import org.hyperledger.besu.ethereum.api.jsonrpc.internal.methods.DebugTraceCall;
+import org.hyperledger.besu.ethereum.api.jsonrpc.internal.parameters.ImmutableTransactionTraceParams;
+import org.hyperledger.besu.ethereum.api.jsonrpc.internal.response.JsonRpcSuccessResponse;
+import org.hyperledger.besu.ethereum.api.jsonrpc.internal.results.OpCodeLoggerTracerResult;
+import org.hyperledger.besu.ethereum.transaction.ImmutableCallParameter;
+import org.hyperledger.besu.testutil.BlockTestUtil;
+
+import java.nio.charset.StandardCharsets;
+
+import com.google.common.io.Resources;
+import org.junit.jupiter.api.BeforeAll;
+import org.junit.jupiter.api.Test;
+
+/**
+ * Integration test verifying that the server-side step limit (--rpc-max-trace-steps) prevents
+ * debug_traceCall from accumulating an unbounded number of structLog frames.
+ *
+ * <p>The PoC bytecode (0x600062000400525b600756) expands memory to ~1 KB then loops forever.
+ * Without a cap this fills the heap. With the cap, tracing stops at the configured limit and the
+ * response carries {@code "truncated": true}.
+ */
+public class DebugTraceCallStepLimitIntegrationTest {
+
+  // Bytecode: PUSH1 0x00, PUSH3 0x000400, MSTORE, JUMPDEST (PC=7), PUSH1 0x07, JUMP
+  // Expands EVM memory to ~1 KB then loops until gas is exhausted.
+  private static final String LOOP_BYTECODE = "0x600062000400525b600756";
+
+  private static final Address TARGET =
+      Address.fromHexString("0x0000000000000000000000000000000000009999");
+  private static final long SERVER_STEP_LIMIT = 5L;
+
+  private static JsonRpcTestMethodsFactory blockchain;
+
+  @BeforeAll
+  static void setUpOnce() throws Exception {
+    final String genesisJson =
+        Resources.toString(BlockTestUtil.getTestGenesisUrl(), StandardCharsets.UTF_8);
+    blockchain =
+        new JsonRpcTestMethodsFactory(
+            new BlockchainImporter(BlockTestUtil.getTestBlockchainUrl(), genesisJson));
+  }
+
+  private DebugTraceCall methodWithLimit(final long limit) {
+    final var apiConfig = ImmutableApiConfiguration.builder().debugTraceStepLimit(limit).build();
+    return new DebugTraceCall(
+        blockchain.getBlockchainQueries(),
+        blockchain.getProtocolSchedule(),
+        blockchain.getTransactionSimulator(),
+        apiConfig);
+  }
+
+  private JsonRpcRequestContext buildRequest(final ImmutableTransactionTraceParams traceParams) {
+    final var callParams = ImmutableCallParameter.builder().to(TARGET).build();
+    final Object[] params = new Object[] {callParams, "latest", traceParams};
+    return new JsonRpcRequestContext(new JsonRpcRequest("2.0", "debug_traceCall", params));
+  }
+
+  private StateOverrideMap loopOverride() {
+    final StateOverrideMap overrides = new StateOverrideMap();
+    overrides.put(TARGET, new StateOverride.Builder().withCode(LOOP_BYTECODE).build());
+    return overrides;
+  }
+
+  @Test
+  void serverStepLimitTruncatesStructLogs() {
+    final var traceParams =
+        ImmutableTransactionTraceParams.builder()
+            .enableMemoryNullable(true)
+            .stateOverrides(loopOverride())
+            .build();
+
+    final var response =
+        (JsonRpcSuccessResponse)
+            methodWithLimit(SERVER_STEP_LIMIT).response(buildRequest(traceParams));
+    final var result = (OpCodeLoggerTracerResult) response.getResult();
+
+    assertThat(result.getStructLogs()).hasSize((int) SERVER_STEP_LIMIT);
+    assertThat(result.truncated()).isTrue();
+  }
+
+  @Test
+  void callerLimitBelowServerLimitIsHonoured() {
+    // Caller requests only 3 steps; server cap is 100 — caller's lower value should win
+    final var traceParams =
+        ImmutableTransactionTraceParams.builder()
+            .enableMemoryNullable(true)
+            .limit(3)
+            .stateOverrides(loopOverride())
+            .build();
+
+    final var response =
+        (JsonRpcSuccessResponse) methodWithLimit(100L).response(buildRequest(traceParams));
+    final var result = (OpCodeLoggerTracerResult) response.getResult();
+
+    assertThat(result.getStructLogs()).hasSize(3);
+    assertThat(result.truncated()).isTrue();
+  }
+
+  @Test
+  void callerCannotExceedServerLimit() {
+    // Caller requests 50000 steps but server allows only SERVER_STEP_LIMIT
+    final var traceParams =
+        ImmutableTransactionTraceParams.builder()
+            .enableMemoryNullable(true)
+            .limit(50_000)
+            .stateOverrides(loopOverride())
+            .build();
+
+    final var response =
+        (JsonRpcSuccessResponse)
+            methodWithLimit(SERVER_STEP_LIMIT).response(buildRequest(traceParams));
+    final var result = (OpCodeLoggerTracerResult) response.getResult();
+
+    assertThat(result.getStructLogs()).hasSize((int) SERVER_STEP_LIMIT);
+    assertThat(result.truncated()).isTrue();
+  }
+}
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/ApiConfiguration.java
```diff
@@ -50,6 +50,16 @@ public abstract class ApiConfiguration {
   /** The default duration a JSON-RPC filter stays active without being polled. */
   public static final Duration DEFAULT_FILTER_TIMEOUT = Duration.ofMinutes(2);
 
+  /**
+   * Default maximum number of EVM steps captured per debug_trace* / trace_call request. Prevents
+   * unbounded heap growth when a caller uses enableMemory + an infinite-loop contract. Set to 0 to
+   * disable the cap (operator opt-out).
+   */
+  public static final long DEFAULT_DEBUG_TRACE_STEP_LIMIT = 1_000_000L;
+
+  /** The default maximum block range for log filter queries. */
+  public static final long DEFAULT_MAX_LOGS_RANGE = 5000L;
+
   /** Constructs a new ApiConfiguration with default values. */
   protected ApiConfiguration() {}
 
@@ -188,4 +198,15 @@ public Integer getMaxFilterCount() {
   public Duration getFilterTimeout() {
     return DEFAULT_FILTER_TIMEOUT;
   }
+
+  /**
+   * Returns the server-side step cap for debug_trace* and trace_call requests. The caller may
+   * specify a lower limit, but never a higher one. Zero means uncapped (operator opt-out).
+   *
+   * @return the maximum number of EVM steps to capture, or 0 for unlimited
+   */
+  @Value.Default
+  public Long getDebugTraceStepLimit() {
+    return DEFAULT_DEBUG_TRACE_STEP_LIMIT;
+  }
 }
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/jsonrpc/internal/methods/AbstractTraceCall.java
```diff
@@ -17,6 +17,7 @@
 import static org.hyperledger.besu.ethereum.api.jsonrpc.internal.response.RpcErrorType.BLOCK_NOT_FOUND;
 import static org.hyperledger.besu.ethereum.api.jsonrpc.internal.response.RpcErrorType.INTERNAL_ERROR;
 
+import org.hyperledger.besu.ethereum.api.ApiConfiguration;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.JsonRpcRequestContext;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.response.JsonRpcErrorResponse;
 import org.hyperledger.besu.ethereum.api.query.BlockchainQueries;
@@ -28,6 +29,7 @@
 import org.hyperledger.besu.ethereum.transaction.PreCloseStateHandler;
 import org.hyperledger.besu.ethereum.transaction.TransactionSimulator;
 import org.hyperledger.besu.ethereum.vm.DebugOperationTracer;
+import org.hyperledger.besu.evm.tracing.OpCodeTracerConfigBuilder;
 
 import java.util.Optional;
 
@@ -44,13 +46,26 @@ public abstract class AbstractTraceCall extends AbstractTraceByBlock {
    */
   private final boolean recordChildCallGas;
 
+  private final long serverStepLimit;
+
   protected AbstractTraceCall(
       final BlockchainQueries blockchainQueries,
       final ProtocolSchedule protocolSchedule,
       final TransactionSimulator transactionSimulator,
       final boolean recordChildCallGas) {
+    this(blockchainQueries, protocolSchedule, transactionSimulator, recordChildCallGas, null);
+  }
+
+  protected AbstractTraceCall(
+      final BlockchainQueries blockchainQueries,
+      final ProtocolSchedule protocolSchedule,
+      final TransactionSimulator transactionSimulator,
+      final boolean recordChildCallGas,
+      final ApiConfiguration apiConfiguration) {
     super(blockchainQueries, protocolSchedule, transactionSimulator);
     this.recordChildCallGas = recordChildCallGas;
+    this.serverStepLimit =
+        apiConfiguration != null ? apiConfiguration.getDebugTraceStepLimit() : 0L;
   }
 
   @Override
@@ -76,12 +91,13 @@ protected Object resultByBlockNumber(
 
     final ProtocolSpec protocolSpec = protocolSchedule.getByBlockHeader(maybeBlockHeader.get());
 
+    final TraceOptions effectiveTraceOptions = applyServerStepLimit(traceOptions);
     final DebugOperationTracer tracer =
-        new DebugOperationTracer(traceOptions.opCodeTracerConfig(), recordChildCallGas);
+        new DebugOperationTracer(effectiveTraceOptions.opCodeTracerConfig(), recordChildCallGas);
     return transactionSimulator
         .process(
             callParams,
-            Optional.ofNullable(traceOptions.stateOverrides()),
+            Optional.ofNullable(effectiveTraceOptions.stateOverrides()),
             buildTransactionValidationParams(),
             tracer,
             getSimulatorResultHandler(requestContext, tracer, protocolSpec),
@@ -90,6 +106,34 @@ protected Object resultByBlockNumber(
             () -> new JsonRpcErrorResponse(requestContext.getRequest().getId(), INTERNAL_ERROR));
   }
 
+  /**
+   * Clamps the caller-supplied step limit to the operator-configured server ceiling. If the server
+   * limit is 0 (operator opt-out), the caller's value is used as-is. If the caller supplies 0
+   * (unlimited), the server ceiling is applied. Otherwise the minimum of the two is used.
+   */
+  private TraceOptions applyServerStepLimit(final TraceOptions traceOptions) {
+    if (serverStepLimit <= 0) {
+      return traceOptions;
+    }
+    final int callerLimit = traceOptions.opCodeTracerConfig().limit();
+    final int effectiveLimit =
+        callerLimit > 0
+            ? (int) Math.min(callerLimit, Math.min(serverStepLimit, Integer.MAX_VALUE))
+            : (int) Math.min(serverStepLimit, Integer.MAX_VALUE);
+    if (effectiveLimit == callerLimit) {
+      return traceOptions;
+    }
+    final var newConfig =
+        OpCodeTracerConfigBuilder.createFrom(traceOptions.opCodeTracerConfig())
+            .limit(effectiveLimit)
+            .build();
+    return new TraceOptions(
+        traceOptions.tracerType(),
+        newConfig,
+        traceOptions.tracerConfig(),
+        traceOptions.stateOverrides());
+  }
+
   protected abstract TraceOptions getTraceOptions(final JsonRpcRequestContext requestContext);
 
   protected abstract PreCloseStateHandler<Object> getSimulatorResultHandler(
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/jsonrpc/internal/methods/DebugTraceCall.java
```diff
@@ -16,6 +16,7 @@
 
 import static org.hyperledger.besu.ethereum.api.jsonrpc.internal.response.RpcErrorType.INTERNAL_ERROR;
 
+import org.hyperledger.besu.ethereum.api.ApiConfiguration;
 import org.hyperledger.besu.ethereum.api.jsonrpc.RpcMethod;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.JsonRpcRequestContext;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.exception.InvalidJsonRpcParameters;
@@ -26,8 +27,10 @@
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.response.JsonRpcError;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.response.JsonRpcErrorResponse;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.response.RpcErrorType;
+import org.hyperledger.besu.ethereum.api.jsonrpc.internal.results.OpCodeLoggerTracerResult;
 import org.hyperledger.besu.ethereum.api.query.BlockchainQueries;
 import org.hyperledger.besu.ethereum.debug.TraceOptions;
+import org.hyperledger.besu.ethereum.debug.TracerType;
 import org.hyperledger.besu.ethereum.mainnet.ImmutableTransactionValidationParams;
 import org.hyperledger.besu.ethereum.mainnet.ProtocolSchedule;
 import org.hyperledger.besu.ethereum.mainnet.ProtocolSpec;
@@ -51,7 +54,15 @@ public DebugTraceCall(
       final BlockchainQueries blockchainQueries,
       final ProtocolSchedule protocolSchedule,
       final TransactionSimulator transactionSimulator) {
-    super(blockchainQueries, protocolSchedule, transactionSimulator, true);
+    this(blockchainQueries, protocolSchedule, transactionSimulator, null);
+  }
+
+  public DebugTraceCall(
+      final BlockchainQueries blockchainQueries,
+      final ProtocolSchedule protocolSchedule,
+      final TransactionSimulator transactionSimulator,
+      final ApiConfiguration apiConfiguration) {
+    super(blockchainQueries, protocolSchedule, transactionSimulator, true, apiConfiguration);
   }
 
   @Override
@@ -109,8 +120,11 @@ protected PreCloseStateHandler<Object> getSimulatorResultHandler(
               final TransactionTrace transactionTrace =
                   new TransactionTrace(
                       result.transaction(), result.result(), tracer.getTraceFrames());
-              return DebugTraceTransactionStepFactory.create(
-                      getTraceOptions(requestContext), protocolSpec)
+              final TraceOptions opts = getTraceOptions(requestContext);
+              if (opts.tracerType() == TracerType.OPCODE_TRACER) {
+                return new OpCodeLoggerTracerResult(transactionTrace, tracer.isLimitReached());
+              }
+              return DebugTraceTransactionStepFactory.create(opts, protocolSpec)
                   .apply(transactionTrace)
                   .getResult();
             });
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/jsonrpc/internal/methods/TraceCall.java
```diff
@@ -16,6 +16,7 @@
 
 import static org.hyperledger.besu.ethereum.api.jsonrpc.internal.response.RpcErrorType.INTERNAL_ERROR;
 
+import org.hyperledger.besu.ethereum.api.ApiConfiguration;
 import org.hyperledger.besu.ethereum.api.jsonrpc.RpcMethod;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.JsonRpcRequestContext;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.exception.InvalidJsonRpcParameters;
@@ -45,7 +46,15 @@ public TraceCall(
       final BlockchainQueries blockchainQueries,
       final ProtocolSchedule protocolSchedule,
       final TransactionSimulator transactionSimulator) {
-    super(blockchainQueries, protocolSchedule, transactionSimulator, false);
+    this(blockchainQueries, protocolSchedule, transactionSimulator, null);
+  }
+
+  public TraceCall(
+      final BlockchainQueries blockchainQueries,
+      final ProtocolSchedule protocolSchedule,
+      final TransactionSimulator transactionSimulator,
+      final ApiConfiguration apiConfiguration) {
+    super(blockchainQueries, protocolSchedule, transactionSimulator, false, apiConfiguration);
   }
 
   @Override
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/jsonrpc/internal/results/OpCodeLoggerTracerResult.java
```diff
@@ -23,18 +23,25 @@
 import java.util.List;
 
 import com.fasterxml.jackson.annotation.JsonGetter;
+import com.fasterxml.jackson.annotation.JsonInclude;
 import com.fasterxml.jackson.annotation.JsonPropertyOrder;
 import org.apache.tuweni.bytes.Bytes;
 
-@JsonPropertyOrder({"gas", "failed", "returnValue", "structLogs"})
+@JsonPropertyOrder({"gas", "failed", "returnValue", "structLogs", "truncated"})
 public class OpCodeLoggerTracerResult {
 
   private final List<StructLog> structLogs;
   private final String returnValue;
   private final long gas;
   private final boolean failed;
+  private final boolean truncated;
 
   public OpCodeLoggerTracerResult(final TransactionTrace transactionTrace) {
+    this(transactionTrace, false);
+  }
+
+  public OpCodeLoggerTracerResult(
+      final TransactionTrace transactionTrace, final boolean truncated) {
     gas = transactionTrace.getGas();
     final Bytes output = transactionTrace.getResult().getOutput();
     returnValue = output.toHexString();
@@ -44,6 +51,7 @@ public OpCodeLoggerTracerResult(final TransactionTrace transactionTrace) {
         .map(OpCodeLoggerTracerResult::createStructLog)
         .forEachOrdered(structLogs::add);
     failed = !transactionTrace.getResult().isSuccessful();
+    this.truncated = truncated;
   }
 
   public static Collection<DebugTraceTransactionResult> of(
@@ -84,4 +92,10 @@ public long getGas() {
   public boolean failed() {
     return failed;
   }
+
+  @JsonGetter(value = "truncated")
+  @JsonInclude(JsonInclude.Include.NON_DEFAULT)
+  public boolean truncated() {
+    return truncated;
+  }
 }
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/jsonrpc/methods/DebugJsonRpcMethods.java
```diff
@@ -15,6 +15,7 @@
 package org.hyperledger.besu.ethereum.api.jsonrpc.methods;
 
 import org.hyperledger.besu.ethereum.ProtocolContext;
+import org.hyperledger.besu.ethereum.api.ApiConfiguration;
 import org.hyperledger.besu.ethereum.api.jsonrpc.RpcApis;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.DebugReplayBlock;
 import org.hyperledger.besu.ethereum.api.jsonrpc.internal.methods.DebugAccountAt;
@@ -64,6 +65,7 @@ public class DebugJsonRpcMethods extends ApiGroupJsonRpcMethods {
   private final Synchronizer synchronizer;
   private final Path dataDir;
   private final TransactionSimulator transactionSimulator;
+  private final ApiConfiguration apiConfiguration;
 
   DebugJsonRpcMethods(
       final BlockchainQueries blockchainQueries,
@@ -73,7 +75,8 @@ public class DebugJsonRpcMethods extends ApiGroupJsonRpcMethods {
       final TransactionPool transactionPool,
       final Synchronizer synchronizer,
       final Path dataDir,
-      final TransactionSimulator transactionSimulator) {
+      final TransactionSimulator transactionSimulator,
+      final ApiConfiguration apiConfiguration) {
     this.blockchainQueries = blockchainQueries;
     this.protocolContext = protocolContext;
     this.protocolSchedule = protocolSchedule;
@@ -82,6 +85,7 @@ public class DebugJsonRpcMethods extends ApiGroupJsonRpcMethods {
     this.synchronizer = synchronizer;
     this.dataDir = dataDir;
     this.transactionSimulator = transactionSimulator;
+    this.apiConfiguration = apiConfiguration;
   }
 
   @Override
@@ -118,6 +122,7 @@ blockchainQueries, new TransactionTracer(blockReplay), protocolSchedule),
         new DebugGetRawReceipts(blockchainQueries),
         new DebugGetRawBlockAccessList(blockchainQueries),
         new DebugGetRawTransaction(blockchainQueries),
-        new DebugTraceCall(blockchainQueries, protocolSchedule, transactionSimulator));
+        new DebugTraceCall(
+            blockchainQueries, protocolSchedule, transactionSimulator, apiConfiguration));
   }
 }
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/jsonrpc/methods/JsonRpcMethodsFactory.java
```diff
@@ -113,7 +113,8 @@ public Map<String, JsonRpcMethod> methods(
                   transactionPool,
                   synchronizer,
                   dataDir,
-                  transactionSimulator),
+                  transactionSimulator,
+                  apiConfiguration),
               new ExecutionEngineJsonRpcMethods(
                   miningCoordinator,
                   protocolSchedule,
```
