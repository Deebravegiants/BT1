# [?] Fixes: GHSA-8g2r-qvch-4c9j Bound and cancel GraphQL blocks(from,to) range queries (#11095)

## Summary
Severity: Unknown
Chain: Ethereum
Component: besu-eth/besu
Published: 2026-08-20
Source: https://github.com/besu-eth/besu/commit/46c2331986daab68bff97266da503efaf8ba19ad
Type: security-commit

## Details
Fixes: GHSA-8g2r-qvch-4c9j Bound and cancel GraphQL blocks(from,to) range queries (#11095)

Signed-off-by: Sally MacFarlane <macfarla.github@gmail.com>

## Patch
### CHANGELOG.md
```diff
@@ -70,6 +70,7 @@
 ### Bug fixes
 - Improve logging for malformed discv4 UDP packets.
 - Bound the snap sync storage sub-range split count to prevent unbounded memory growth under a malformed snap response.
+- Added a configurable range cap (--graphql-max-blocks-range, default 5000) for GraphQL blocks(from, to) range queries; queries exceeding the cap are cancelled.
 - Remove `System.out`/`System.err` logging from `P256VerifyPrecompiledContract` and `BlockchainQueries` — these could leak sensitive data to stdout/stderr in production.
 - EIP-1459 DNS discovery now rejoins TXT records split across multiple `<character-string>`s. Records longer than 255 bytes were truncated, so Besu silently discarded most of every tree, resolving 832 of 3000 nodes from the mainnet tree. [#10985](https://github.com/besu-eth/besu/pull/10985)
 - Queue backward-sync targets received before peer readiness and retry when a peer connects. [#10843](https://github.com/besu-eth/besu/pull/10843)
```

### app/src/main/java/org/hyperledger/besu/RunnerBuilder.java
```diff
@@ -1040,7 +1040,8 @@ public Runner build() {
 
     Optional<GraphQLHttpService> graphQLHttpService = Optional.empty();
     if (graphQLConfiguration.isEnabled()) {
-      final GraphQLDataFetchers fetchers = new GraphQLDataFetchers(supportedCapabilities);
+      final GraphQLDataFetchers fetchers =
+          new GraphQLDataFetchers(supportedCapabilities, graphQLConfiguration.getMaxBlockRange());
       final Map<GraphQLContextType, Object> graphQlContextMap = new ConcurrentHashMap<>();
       graphQlContextMap.putIfAbsent(GraphQLContextType.BLOCKCHAIN_QUERIES, blockchainQueries);
       graphQlContextMap.putIfAbsent(GraphQLContextType.PROTOCOL_SCHEDULE, protocolSchedule);
```

### app/src/main/java/org/hyperledger/besu/cli/options/GraphQlOptions.java
```diff
@@ -85,6 +85,13 @@ public class GraphQlOptions {
       description = "Path to the file containing the password for the TLS truststore")
   private String graphqlTlsTruststorePasswordFile;
 
+  @CommandLine.Option(
+      names = {"--graphql-max-blocks-range"},
+      description =
+          "Specifies the maximum number of blocks that can be retrieved by a single GraphQL "
+              + "blocks(from,to) query. Must be >=0. 0 specifies no limit (default: ${DEFAULT-VALUE})")
+  private final Long graphQLMaxBlockRange = GraphQLConfiguration.DEFAULT_MAX_BLOCK_RANGE;
+
   /** Default constructor */
   public GraphQlOptions() {}
 
@@ -95,6 +102,10 @@ public GraphQlOptions() {}
    * @param commandLine CommandLine instance
    */
   public void validate(final Logger logger, final CommandLine commandLine) {
+    if (graphQLMaxBlockRange < 0) {
+      throw new CommandLine.ParameterException(
+          commandLine, "--graphql-max-blocks-range must be >= 0 (0 specifies no limit)");
+    }
     CommandLineUtils.checkOptionDependencies(
         logger,
         commandLine,
@@ -148,6 +159,7 @@ public GraphQLConfiguration graphQLConfiguration(
     graphQLConfiguration.setMtlsEnabled(graphqlMtlsEnabled);
     graphQLConfiguration.setTlsTrustStorePath(graphqlTlsTruststoreFile);
     graphQLConfiguration.setTlsTrustStorePasswordFile(graphqlTlsTruststorePasswordFile);
+    graphQLConfiguration.setMaxBlockRange(graphQLMaxBlockRange);
 
     return graphQLConfiguration;
   }
```

### app/src/test/java/org/hyperledger/besu/cli/options/GraphQlOptionsTest.java
```diff
@@ -22,6 +22,7 @@
 
 import org.junit.jupiter.api.Test;
 import org.junit.jupiter.api.extension.ExtendWith;
+import org.mockito.Mockito;
 import org.mockito.junit.jupiter.MockitoExtension;
 
 @ExtendWith(MockitoExtension.class)
@@ -90,4 +91,40 @@ public void graphQLHttpHostMayBeIPv6() {
     assertThat(commandOutput.toString(UTF_8)).isEmpty();
     assertThat(commandErrorOutput.toString(UTF_8)).isEmpty();
   }
+
+  @Test
+  public void graphQLMaxBlockRangeDefaultsToFiveThousand() {
+    parseCommand("--graphql-http-enabled");
+
+    verify(mockRunnerBuilder).graphQLConfiguration(graphQLConfigArgumentCaptor.capture());
+    verify(mockRunnerBuilder).build();
+
+    assertThat(graphQLConfigArgumentCaptor.getValue().getMaxBlockRange()).isEqualTo(5000L);
+
+    assertThat(commandOutput.toString(UTF_8)).isEmpty();
+    assertThat(commandErrorOutput.toString(UTF_8)).isEmpty();
+  }
+
+  @Test
+  public void graphQLMaxBlockRangeOptionMustBeUsed() {
+    parseCommand("--graphql-http-enabled", "--graphql-max-blocks-range", "42");
+
+    verify(mockRunnerBuilder).graphQLConfiguration(graphQLConfigArgumentCaptor.capture());
+    verify(mockRunnerBuilder).build();
+
+    assertThat(graphQLConfigArgumentCaptor.getValue().getMaxBlockRange()).isEqualTo(42L);
+
+    assertThat(commandOutput.toString(UTF_8)).isEmpty();
+    assertThat(commandErrorOutput.toString(UTF_8)).isEmpty();
+  }
+
+  @Test
+  public void graphQLMaxBlockRangeRejectsNegativeValue() {
+    parseCommand("--graphql-http-enabled", "--graphql-max-blocks-range", "-1");
+
+    Mockito.verifyNoInteractions(mockRunnerBuilder);
+    assertThat(commandOutput.toString(UTF_8)).isEmpty();
+    assertThat(commandErrorOutput.toString(UTF_8))
+        .contains("--graphql-max-blocks-range must be >= 0 (0 specifies no limit)");
+  }
 }
```

### app/src/test/resources/everything_config.toml
```diff
@@ -123,6 +123,7 @@ graphql-tls-keystore-password-file="none.passwd"
 graphql-mtls-enabled=false
 graphql-tls-truststore-file="none.pfx"
 graphql-tls-truststore-password-file="none.passwd"
+graphql-max-blocks-range=100
 
 # WebSockets API
 rpc-ws-enabled=false
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/graphql/GraphQLConfiguration.java
```diff
@@ -40,12 +40,19 @@ public class GraphQLConfiguration {
   /** The default port number for the GraphQL HTTP server. */
   public static final int DEFAULT_GRAPHQL_HTTP_PORT = 8547;
 
+  /**
+   * The default maximum number of blocks a single {@code blocks(from,to)} GraphQL query may span,
+   * mirroring the JSON-RPC {@code --rpc-max-logs-range} default.
+   */
+  public static final long DEFAULT_MAX_BLOCK_RANGE = 5000L;
+
   private boolean enabled;
   private int port;
   private String host;
   private List<String> corsAllowedDomains = Collections.emptyList();
   private List<String> hostsAllowlist = Arrays.asList("localhost", DEFAULT_GRAPHQL_HTTP_HOST);
   private long httpTimeoutSec = TimeoutOptions.defaultOptions().getTimeoutSeconds();
+  private long maxBlockRange = DEFAULT_MAX_BLOCK_RANGE;
 
   private String tlsKeyStorePath;
   private String tlsKeyStorePasswordFile;
@@ -69,6 +76,7 @@ public static GraphQLConfiguration createDefault() {
     config.setPort(DEFAULT_GRAPHQL_HTTP_PORT);
     config.setHost(DEFAULT_GRAPHQL_HTTP_HOST);
     config.setHttpTimeoutSec(TimeoutOptions.defaultOptions().getTimeoutSeconds());
+    config.setMaxBlockRange(DEFAULT_MAX_BLOCK_RANGE);
     return config;
   }
 
@@ -184,6 +192,24 @@ public void setHttpTimeoutSec(final long httpTimeoutSec) {
     this.httpTimeoutSec = httpTimeoutSec;
   }
 
+  /**
+   * Retrieves the maximum number of blocks a single {@code blocks(from,to)} query may span.
+   *
+   * @return the maximum block range, or 0 for no limit
+   */
+  public long getMaxBlockRange() {
+    return maxBlockRange;
+  }
+
+  /**
+   * Sets the maximum number of blocks a single {@code blocks(from,to)} query may span.
+   *
+   * @param maxBlockRange the maximum block range to set; 0 means no limit
+   */
+  public void setMaxBlockRange(final long maxBlockRange) {
+    this.maxBlockRange = maxBlockRange;
+  }
+
   /**
    * Retrieves the TLS key store path.
    *
@@ -307,6 +333,7 @@ public String toString() {
         .add("corsAllowedDomains", corsAllowedDomains)
         .add("hostsAllowlist", hostsAllowlist)
         .add("httpTimeoutSec", httpTimeoutSec)
+        .add("maxBlockRange", maxBlockRange)
         .toString();
   }
 
```

### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/graphql/GraphQLDataFetchers.java
```diff
@@ -28,6 +28,7 @@
 import org.hyperledger.besu.ethereum.api.graphql.internal.pojoadapter.SyncStateAdapter;
 import org.hyperledger.besu.ethereum.api.graphql.internal.pojoadapter.TransactionAdapter;
 import org.hyperledger.besu.ethereum.api.graphql.internal.response.GraphQLError;
+import org.hyperledger.besu.ethereum.api.query.BackendQuery;
 import org.hyperledger.besu.ethereum.api.query.BlockWithMetadata;
 import org.hyperledger.besu.ethereum.api.query.BlockchainQueries;
 import org.hyperledger.besu.ethereum.api.query.LogsQuery;
@@ -53,6 +54,7 @@
 import java.util.Optional;
 import java.util.OptionalInt;
 import java.util.Set;
+import java.util.function.Supplier;
 
 import com.google.common.base.Preconditions;
 import graphql.GraphQLContext;
@@ -77,7 +79,15 @@
  */
 public class GraphQLDataFetchers {
 
+  /**
+   * Default maximum number of blocks a single {@code blocks(from,to)} query may span, used when no
+   * explicit limit is supplied (e.g. by test call sites). Mirrors {@link
+   * GraphQLConfiguration#DEFAULT_MAX_BLOCK_RANGE}.
+   */
+  public static final long DEFAULT_MAX_BLOCK_RANGE = GraphQLConfiguration.DEFAULT_MAX_BLOCK_RANGE;
+
   private final Integer highestEthVersion;
+  private final long maxBlockRange;
 
   /**
    * Constructs a new GraphQLDataFetchers instance.
@@ -89,12 +99,26 @@ public class GraphQLDataFetchers {
    * @param supportedCapabilities a set of capabilities supported by the Ethereum node
    */
   public GraphQLDataFetchers(final Set<Capability> supportedCapabilities) {
+    this(supportedCapabilities, DEFAULT_MAX_BLOCK_RANGE);
+  }
+
+  /**
+   * Constructs a new GraphQLDataFetchers instance with an explicit cap on the span of a single
+   * {@code blocks(from,to)} range query.
+   *
+   * @param supportedCapabilities a set of capabilities supported by the Ethereum node
+   * @param maxBlockRange the maximum number of blocks a single {@code blocks(from,to)} query may
+   *     span; 0 means no limit
+   */
+  public GraphQLDataFetchers(
+      final Set<Capability> supportedCapabilities, final long maxBlockRange) {
     final OptionalInt version =
         supportedCapabilities.stream()
             .filter(cap -> EthProtocol.NAME.equals(cap.getName()))
             .mapToInt(Capability::getVersion)
             .max();
     highestEthVersion = version.isPresent() ? version.getAsInt() : null;
+    this.maxBlockRange = maxBlockRange;
   }
 
   /**
@@ -219,20 +243,42 @@ DataFetcher<List<NormalBlockAdapter>> getRangeBlockDataFetcher() {
     return dataFetchingEnvironment -> {
       final BlockchainQueries blockchainQuery =
           dataFetchingEnvironment.getGraphQlContext().get(GraphQLContextType.BLOCKCHAIN_QUERIES);
+      final Supplier<Boolean> isAlive =
+          dataFetchingEnvironment.getGraphQlContext().get(GraphQLContextType.IS_ALIVE_HANDLER);
 
-      final long from = dataFetchingEnvironment.getArgument("from");
-      final long to;
+      final long chainHeadBlockNumber = blockchainQuery.getBlockchain().getChainHeadBlockNumber();
+      long from;
+      if (dataFetchingEnvironment.containsArgument("from")) {
+        from = dataFetchingEnvironment.getArgument("from");
+      } else {
+        from = chainHeadBlockNumber;
+      }
+      long to;
       if (dataFetchingEnvironment.containsArgument("to")) {
         to = dataFetchingEnvironment.getArgument("to");
       } else {
-        to = blockchainQuery.latestBlock().map(block -> block.getHeader().getNumber()).orElse(0L);
+        to = chainHeadBlockNumber;
       }
-      if (from > to) {
+      if (from < 0 || from > to) {
         throw new GraphQLException(GraphQLError.INVALID_PARAMS);
       }
+      // Checked on the caller-supplied (pre-clamp) span so an attacker can't sidestep the cap by
+      // supplying a `to` far beyond the chain head, relying on the clamp below to shrink it first.
+      if (maxBlockRange > 0 && (to - from) > maxBlockRange) {
+        throw new GraphQLException(GraphQLError.INVALID_PARAMS);
+      }
+      // A supplied `to` beyond the chain head only ever shrinks the loop below, so clamping here
+      // (after the span check above) can only reduce work, never let more through.
+      to = Math.min(to, chainHeadBlockNumber);
 
       final List<NormalBlockAdapter> results = new ArrayList<>();
       for (long i = from; i <= to; i++) {
+        // IS_ALIVE_HANDLER is always populated for real HTTP requests (GraphQLHttpService), but
+        // any call site that builds a GraphQlContext without it (tests, future callers) should
+        // fail open here rather than NPE inside the loop.
+        if (isAlive != null) {
+          BackendQuery.stopIfExpired(isAlive);
+        }
         final Optional<BlockWithMetadata<TransactionWithMetadata, Hash>> block =
             blockchainQuery.blockByNumber(i);
         block.ifPresent(e -> results.add(new NormalBlockAdapter(e)));
```

### ethereum/api/src/test/java/org/hyperledger/besu/ethereum/api/graphql/RangeBlockDataFetcherTest.java
```diff
@@ -0,0 +1,230 @@
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
+package org.hyperledger.besu.ethereum.api.graphql;
+
+import static org.assertj.core.api.Assertions.assertThat;
+import static org.assertj.core.api.Assertions.assertThatThrownBy;
+import static org.mockito.ArgumentMatchers.anyLong;
+import static org.mockito.Mockito.mock;
+import static org.mockito.Mockito.never;
+import static org.mockito.Mockito.times;
+import static org.mockito.Mockito.verify;
+import static org.mockito.Mockito.when;
+
+import org.hyperledger.besu.ethereum.api.graphql.internal.pojoadapter.NormalBlockAdapter;
+import org.hyperledger.besu.ethereum.api.query.BlockWithMetadata;
+import org.hyperledger.besu.ethereum.chain.Blockchain;
+
+import java.util.List;
+import java.util.Optional;
+import java.util.function.Supplier;
+
+import graphql.schema.DataFetcher;
+import org.junit.jupiter.api.BeforeEach;
+import org.junit.jupiter.api.Test;
+import org.junit.jupiter.api.extension.ExtendWith;
+import org.mockito.junit.jupiter.MockitoExtension;
+
+/**
+ * Regression coverage for HYB-07: {@code blocks(from,to)} previously accepted an unbounded {@code
+ * to} (up to {@code Long.MAX_VALUE}) with no span cap and no liveness check, letting a single query
+ * loop for an effectively unbounded number of iterations and pin a request-handling thread
+ * indefinitely, uncancellable even after the caller disconnected.
+ */
+@ExtendWith(MockitoExtension.class)
+class RangeBlockDataFetcherTest extends AbstractDataFetcherTest {
+
+  private static final long CHAIN_HEAD = 100L;
+
+  private final Blockchain blockchain = mock(Blockchain.class);
+
+  @BeforeEach
+  @Override
+  public void before() {
+    super.before();
+    when(graphQLContext.get(GraphQLContextType.BLOCKCHAIN_QUERIES)).thenReturn(query);
+    when(query.getBlockchain()).thenReturn(blockchain);
+    when(blockchain.getChainHeadBlockNumber()).thenReturn(CHAIN_HEAD);
+  }
+
+  private DataFetcher<List<NormalBlockAdapter>> fetcherWithMaxRange(final long maxBlockRange) {
+    return new GraphQLDataFetchers(supportedCapabilities, maxBlockRange).getRangeBlockDataFetcher();
+  }
+
+  private void stubBlockByNumberPresent() {
+    when(query.blockByNumber(anyLong()))
+        .thenReturn(Optional.of(new BlockWithMetadata<>(null, null, null, null, 0)));
+  }
+
+  @Test
+  void rejectsFromBeyondTo() {
+    when(environment.containsArgument("from")).thenReturn(true);
+    when(environment.getArgument("from")).thenReturn(10L);
+    when(environment.containsArgument("to")).thenReturn(true);
+    when(environment.getArgument("to")).thenReturn(5L);
+
+    assertThatThrownBy(() -> fetcherWithMaxRange(5000L).get(environment))
+        .isInstanceOf(GraphQLException.class);
+  }
+
+  @Test
+  void rejectsNegativeFrom() {
+    when(environment.containsArgument("from")).thenReturn(true);
+    when(environment.getArgument("from")).thenReturn(-1L);
+    when(environment.containsArgument("to")).thenReturn(true);
+    when(environment.getArgument("to")).thenReturn(10L);
+
+    assertThatThrownBy(() -> fetcherWithMaxRange(5000L).get(environment))
+        .isInstanceOf(GraphQLException.class);
+  }
+
+  @Test
+  void rejectsSpanExceedingCapEvenFarBeyondChainHead() {
+    // The reported attack: a `to` far beyond both the chain head and Long-range sanity
+    // (Long.MAX_VALUE - 1) must be rejected outright by the span cap, without ever touching
+    // the per-block loop - not "clamped then looped".
+    when(environment.containsArgument("from")).thenReturn(true);
+    when(environment.getArgument("from")).thenReturn(1_000_000_000_000L);
+    when(environment.containsArgument("to")).thenReturn(true);
+    when(environment.getArgument("to")).thenReturn(Long.MAX_VALUE - 1);
+
+    assertThatThrownBy(() -> fetcherWithMaxRange(5000L).get(environment))
+        .isInstanceOf(GraphQLException.class);
+    verify(query, never()).blockByNumber(anyLong());
+  }
+
+  @Test
+  void rejectsSpanExceedingCapOnAShortLegitimateLookingChain() {
+    // Span cap must trigger on the raw caller-supplied range, independent of chain height - both
+    // from/to here are individually unremarkable, only their span (6000) exceeds the cap.
+    when(environment.containsArgument("from")).thenReturn(true);
+    when(environment.getArgument("from")).thenReturn(0L);
+    when(environment.containsArgument("to")).thenReturn(true);
+    when(environment.getArgument("to")).thenReturn(6000L);
+
+    assertThatThrownBy(() -> fetcherWithMaxRange(5000L).get(environment))
+        .isInstanceOf(GraphQLException.class);
+  }
+
+  @Test
+  void allowsSpanWithinCap() throws Exception {
+    when(environment.containsArgument("from")).thenReturn(true);
+    when(environment.getArgument("from")).thenReturn(0L);
+    when(environment.containsArgument("to")).thenReturn(true);
+    when(environment.getArgument("to")).thenReturn(10L);
+    when(graphQLContext.<Supplier<Boolean>>get(GraphQLContextType.IS_ALIVE_HANDLER))
+        .thenReturn(() -> true);
+    stubBlockByNumberPresent();
+
+    final List<NormalBlockAdapter> results = fetcherWithMaxRange(5000L).get(environment);
+
+    assertThat(results).hasSize(11);
+  }
+
+  @Test
+  void zeroMaxBlockRangeMeansNoSpanCap() throws Exception {
+    when(environment.containsArgument("from")).thenReturn(true);
+    when(environment.getArgument("from")).thenReturn(0L);
+    when(environment.containsArgument("to")).thenReturn(true);
+    when(environment.getArgument("to")).thenReturn(10_000L);
+    when(graphQLContext.<Supplier<Boolean>>get(GraphQLContextType.IS_ALIVE_HANDLER))
+        .thenReturn(() -> true);
+    stubBlockByNumberPresent();
+
+    // No span-cap rejection - but the chain-head clamp (below) still bounds the actual loop.
+    final List<NormalBlockAdapter> results = fetcherWithMaxRange(0L).get(environment);
+
+    assertThat(results).hasSize((int) CHAIN_HEAD + 1);
+  }
+
+  @Test
+  void clampsToChainHeadEvenWithNoSpanCapConfigured() throws Exception {
+    // With the span cap disabled (0 = no limit), the chain-head clamp is the ONLY thing standing
+    // between a caller-supplied Long.MAX_VALUE-ish `to` and an effectively infinite loop. Confirm
+    // it alone still bounds the loop to real chain height.
+    when(environment.containsArgument("from")).thenReturn(true);
+    when(environment.getArgument("from")).thenReturn(0L);
+    when(environment.containsArgument("to")).thenReturn(true);
+    when(environment.getArgument("to")).thenReturn(Long.MAX_VALUE - 1);
+    when(graphQLContext.<Supplier<Boolean>>get(GraphQLContextType.IS_ALIVE_HANDLER))
+        .thenReturn(() -> true);
+    stubBlockByNumberPresent();
+
+    fetcherWithMaxRange(0L).get(environment);
+
+    verify(query, times((int) CHAIN_HEAD + 1)).blockByNumber(anyLong());
+  }
+
+  @Test
+  void omittedToDefaultsToChainHeadAndIsStillCapped() throws Exception {
+    when(environment.containsArgument("from")).thenReturn(true);
+    when(environment.getArgument("from")).thenReturn(0L);
+    when(environment.containsArgument("to")).thenReturn(false);
+    when(graphQLContext.<Supplier<Boolean>>get(GraphQLContextType.IS_ALIVE_HANDLER))
+        .thenReturn(() -> true);
+    stubBlockByNumberPresent();
+
+    final List<NormalBlockAdapter> results = fetcherWithMaxRange(5000L).get(environment);
+
+    assertThat(results).hasSize((int) CHAIN_HEAD + 1);
+  }
+
+  @Test
+  void omittedFromDefaultsToChainHeadInsteadOfNpeing() throws Exception {
+    // blocks(to: 100) with no `from` at all: `from` is a nullable Long in the GraphQL schema, so
+    // this must not unbox a null into a primitive long. Mirrors the existing to-omitted default.
+    when(environment.containsArgument("from")).thenReturn(false);
+    when(environment.containsArgument("to")).thenReturn(true);
+    when(environment.getArgument("to")).thenReturn(CHAIN_HEAD);
+    when(graphQLContext.<Supplier<Boolean>>get(GraphQLContextType.IS_ALIVE_HANDLER))
+        .thenReturn(() -> true);
+    stubBlockByNumberPresent();
+
+    final List<NormalBlockAdapter> results = fetcherWithMaxRange(5000L).get(environment);
+
+    assertThat(results).hasSize(1);
+  }
+
+  @Test
+  void abortsAsSoonAsCallerIsGone() {
+    when(environment.containsArgument("from")).thenReturn(true);
+    when(environment.getArgument("from")).thenReturn(0L);
+    when(environment.containsArgument("to")).thenReturn(true);
+    when(environment.getArgument("to")).thenReturn(10L);
+    when(graphQLContext.<Supplier<Boolean>>get(GraphQLContextType.IS_ALIVE_HANDLER))
+        .thenReturn(() -> false);
+
+    assertThatThrownBy(() -> fetcherWithMaxRange(5000L).get(environment))
+        .isInstanceOf(RuntimeException.class);
+    verify(query, never()).blockByNumber(anyLong());
+  }
+
+  @Test
+  void nullIsAliveHandlerDoesNotThrowInsteadOfAborting() throws Exception {
+    // IS_ALIVE_HANDLER is always populated for real HTTP requests, but a GraphQlContext built
+    // without it (e.g. a hand-built test context) must fail open, not NPE inside the loop.
+    when(environment.containsArgument("from")).thenReturn(true);
+    when(environment.getArgument("from")).thenReturn(0L);
+    when(environment.containsArgument("to")).thenReturn(true);
+    when(environment.getArgument("to")).thenReturn(10L);
+    when(graphQLContext.<Supplier<Boolean>>get(GraphQLContextType.IS_ALIVE_HANDLER))
+        .thenReturn(null);
+    stubBlockByNumberPresent();
+
+    final List<NormalBlockAdapter> results = fetcherWithMaxRange(5000L).get(environment);
+
+    assertThat(results).hasSize(11);
+  }
+}
```

### ethereum/api/src/test/resources/org/hyperledger/besu/ethereum/api/graphql/graphql_blocks_byRange_exceedsMax.json
```diff
@@ -0,0 +1,26 @@
+{
+  "request": "{blocks (from : \"0x0\", to: \"0x1389\") { number }} ",
+  "response": {
+    "errors": [
+      {
+        "message": "Exception while fetching data (/blocks) : Invalid params",
+        "locations": [
+          {
+            "line": 1,
+            "column": 2
+          }
+        ],
+        "path": [
+          "blocks"
+        ],
+        "extensions": {
+          "errorCode": -32602,
+          "errorMessage": "Invalid params",
+          "classification": "DataFetchingException"
+        }
+      }
+    ],
+    "data": null
+  },
+  "statusCode": 400
+}
```
