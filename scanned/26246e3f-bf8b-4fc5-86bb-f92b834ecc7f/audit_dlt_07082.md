# [?] fix(graphql): cap logs(filter) block range to prevent unauthenticated DoS (#114)

## Summary
Severity: Unknown
Chain: Ethereum
Component: hyperledger/besu
Published: 2026-08-28
Source: https://github.com/besu-eth/besu/commit/09c990476deb19163d2b21181d85e55e0a799996
Type: security-commit

## Details
fix(graphql): cap logs(filter) block range to prevent unauthenticated DoS (#114)

GraphQL logs(filter) accepted an unbounded toBlock, allowing a caller
to schedule O(toBlock) bloom-filter reads and receipt fetches per request,
exhausting the Vert.x worker pool without authentication.

Applies the same fromBlock < 0 and span cap checks already present in
getRangeBlockDataFetcher() (added for GHSA-8g2r-qvch-4c9j). The existing
maxBlockRange configuration wired through GraphQLDataFetchers is reused
with no new plumbing required.

Fixes: GHSA-g499-x5x3-8gjj
Closes #106

Signed-off-by: Sally MacFarlane <sally.macfarlane@consensys.net>
Signed-off-by: Sally MacFarlane <macfarla.github@gmail.com>
Co-authored-by: Justin Florentine <justin+github@florentine.us>
Signed-off-by: Sally MacFarlane <macfarla.github@gmail.com>

## Patch
### ethereum/api/src/main/java/org/hyperledger/besu/ethereum/api/graphql/GraphQLDataFetchers.java
```diff
@@ -380,9 +380,17 @@ DataFetcher<Optional<List<LogAdapter>>> getLogsDataFetcher() {
       final long fromBlock = (Long) filter.getOrDefault("fromBlock", currentBlock);
       final long toBlock = (Long) filter.getOrDefault("toBlock", currentBlock);
 
+      if (fromBlock < 0) {
+        throw new GraphQLException(GraphQLError.INVALID_PARAMS);
+      }
       if (fromBlock > toBlock) {
         throw new GraphQLException(GraphQLError.INVALID_PARAMS);
       }
+      // Checked on the caller-supplied (pre-clamp) span so an attacker can't sidestep the cap by
+      // supplying a `toBlock` far beyond the chain head, relying on matchingLogs to short-circuit.
+      if (maxBlockRange > 0 && (toBlock - fromBlock) > maxBlockRange) {
+        throw new GraphQLException(GraphQLError.INVALID_PARAMS);
+      }
 
       @SuppressWarnings("unchecked")
       final List<Address> addrs = (List<Address>) filter.get("addresses");
```

### ethereum/api/src/test/java/org/hyperledger/besu/ethereum/api/graphql/RangeLogsDataFetcherTest.java
```diff
@@ -0,0 +1,135 @@
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
+import static org.mockito.ArgumentMatchers.any;
+import static org.mockito.ArgumentMatchers.anyLong;
+import static org.mockito.Mockito.mock;
+import static org.mockito.Mockito.never;
+import static org.mockito.Mockito.verify;
+import static org.mockito.Mockito.when;
+
+import org.hyperledger.besu.ethereum.api.graphql.internal.pojoadapter.LogAdapter;
+import org.hyperledger.besu.ethereum.chain.Blockchain;
+
+import java.util.List;
+import java.util.Map;
+import java.util.Optional;
+
+import graphql.schema.DataFetcher;
+import org.junit.jupiter.api.BeforeEach;
+import org.junit.jupiter.api.Test;
+import org.junit.jupiter.api.extension.ExtendWith;
+import org.mockito.junit.jupiter.MockitoExtension;
+
+/**
+ * Regression coverage for GHSA-g499-x5x3-8gjj: {@code logs(filter)} previously accepted an
+ * unbounded block range with no span cap, letting a single query loop for an effectively unbounded
+ * number of iterations and pin a request-handling thread, unlike the sibling {@code
+ * blocks(from,to)} which already had a cap.
+ */
+@ExtendWith(MockitoExtension.class)
+class RangeLogsDataFetcherTest extends AbstractDataFetcherTest {
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
+  private DataFetcher<Optional<List<LogAdapter>>> fetcherWithMaxRange(final long maxBlockRange) {
+    return new GraphQLDataFetchers(supportedCapabilities, maxBlockRange).getLogsDataFetcher();
+  }
+
+  private void withFilter(final long fromBlock, final long toBlock) {
+    when(environment.getArgument("filter"))
+        .thenReturn(
+            Map.of(
+                "fromBlock",
+                fromBlock,
+                "toBlock",
+                toBlock,
+                "addresses",
+                List.of(),
+                "topics",
+                List.of()));
+  }
+
+  @Test
+  void rejectsNegativeFromThatWouldOverflowTheSpanCheck() {
+    withFilter(-1L, 10L);
+
+    assertThatThrownBy(() -> fetcherWithMaxRange(5000L).get(environment))
+        .isInstanceOf(GraphQLException.class);
+    verify(query, never()).matchingLogs(anyLong(), anyLong(), any(), any());
+  }
+
+  @Test
+  void rejectsFromBeyondTo() {
+    withFilter(10L, 5L);
+
+    assertThatThrownBy(() -> fetcherWithMaxRange(5000L).get(environment))
+        .isInstanceOf(GraphQLException.class);
+    verify(query, never()).matchingLogs(anyLong(), anyLong(), any(), any());
+  }
+
+  @Test
+  void rejectsSpanExceedingCapEvenFarBeyondChainHead() {
+    withFilter(1_000_000_000_000L, Long.MAX_VALUE - 1);
+
+    assertThatThrownBy(() -> fetcherWithMaxRange(5000L).get(environment))
+        .isInstanceOf(GraphQLException.class);
+    verify(query, never()).matchingLogs(anyLong(), anyLong(), any(), any());
+  }
+
+  @Test
+  void rejectsSpanExceedingCapOnAShortLegitimateLookingChain() {
+    withFilter(0L, 6000L);
+
+    assertThatThrownBy(() -> fetcherWithMaxRange(5000L).get(environment))
+        .isInstanceOf(GraphQLException.class);
+    verify(query, never()).matchingLogs(anyLong(), anyLong(), any(), any());
+  }
+
+  @Test
+  void allowsSpanWithinCap() throws Exception {
+    withFilter(0L, 10L);
+    when(query.matchingLogs(anyLong(), anyLong(), any(), any())).thenReturn(List.of());
+
+    final Optional<List<LogAdapter>> result = fetcherWithMaxRange(5000L).get(environment);
+
+    assertThat(result).isPresent();
+    assertThat(result.get()).isEmpty();
+  }
+
+  @Test
+  void zeroMaxBlockRangeMeansNoSpanCap() throws Exception {
+    withFilter(0L, 10_000L);
+    when(query.matchingLogs(anyLong(), anyLong(), any(), any())).thenReturn(List.of());
+
+    final Optional<List<LogAdapter>> result = fetcherWithMaxRange(0L).get(environment);
+
+    assertThat(result).isPresent();
+  }
+}
```
