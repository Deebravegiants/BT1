# [?] Merge pull request from GHSA-4cpw-7xvx-2pf8

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys/teku
Published: 2020-12-22
Source: https://github.com/Consensys-Incorporated/teku/commit/e66336f14e839d1468941baf4bf64e329e82a719
Type: security-commit

## Details
Merge pull request from GHSA-4cpw-7xvx-2pf8

* Filter libp2p gossip topics to ones relevant to Eth2.

* Use more generic type.

* Add list limits

* Fix peers limit

* Tweak limits

* Derive PreparedPubsubMessage from AbstractPubsubMessage to have secure hashCode()

* Make fast messageID secure on hashCode() collisions

* Run spotless

* Add missing import

* Use new param

* Update jvm-libp2p version

Co-authored-by: Adrian Sutton <adrian.sutton@consensys.net>
Co-authored-by: Anton Nashatyrev <anton.nashatyrev@gmail.com>

## Patch
### gradle/versions.gradle
```diff
@@ -38,7 +38,7 @@ dependencyManagement {
     dependency 'io.protostuff:protostuff-core:1.6.2'
     dependency 'io.protostuff:protostuff-runtime:1.6.2'
 
-    dependency 'io.libp2p:jvm-libp2p-minimal:0.6.3-RELEASE'
+    dependency 'io.libp2p:jvm-libp2p-minimal:0.6.4-RELEASE'
     dependency 'tech.pegasys:jblst:0.2.0-RELEASE'
 
     dependency 'org.hdrhistogram:HdrHistogram:2.1.12'
```

### networking/eth2/src/main/java/tech/pegasys/teku/networking/eth2/Eth2NetworkBuilder.java
```diff
@@ -36,6 +36,7 @@
 import tech.pegasys.teku.networking.eth2.gossip.encoding.GossipEncoding;
 import tech.pegasys.teku.networking.eth2.gossip.subnets.AttestationSubnetTopicProvider;
 import tech.pegasys.teku.networking.eth2.gossip.subnets.PeerSubnetSubscriptions;
+import tech.pegasys.teku.networking.eth2.gossip.topics.Eth2GossipTopicFilter;
 import tech.pegasys.teku.networking.eth2.gossip.topics.OperationProcessor;
 import tech.pegasys.teku.networking.eth2.gossip.topics.ProcessedAttestationSubscriptionProvider;
 import tech.pegasys.teku.networking.eth2.peers.Eth2PeerManager;
@@ -44,6 +45,7 @@
 import tech.pegasys.teku.networking.p2p.DiscoveryNetwork;
 import tech.pegasys.teku.networking.p2p.gossip.PreparedGossipMessageFactory;
 import tech.pegasys.teku.networking.p2p.libp2p.LibP2PNetwork;
+import tech.pegasys.teku.networking.p2p.libp2p.gossip.GossipTopicFilter;
 import tech.pegasys.teku.networking.p2p.network.NetworkConfig;
 import tech.pegasys.teku.networking.p2p.network.PeerHandler;
 import tech.pegasys.teku.networking.p2p.reputation.ReputationManager;
@@ -74,14 +76,14 @@ public class Eth2NetworkBuilder {
   private ProcessedAttestationSubscriptionProvider processedAttestationSubscriptionProvider;
   private StorageQueryChannel historicalChainData;
   private MetricsSystem metricsSystem;
-  private List<RpcMethod> rpcMethods = new ArrayList<>();
-  private List<PeerHandler> peerHandlers = new ArrayList<>();
+  private final List<RpcMethod> rpcMethods = new ArrayList<>();
+  private final List<PeerHandler> peerHandlers = new ArrayList<>();
   private TimeProvider timeProvider;
   private AsyncRunner asyncRunner;
   private KeyValueStore<String, Bytes> keyValueStore;
   private Duration eth2RpcPingInterval = DEFAULT_ETH2_RPC_PING_INTERVAL;
   private int eth2RpcOutstandingPingThreshold = DEFAULT_ETH2_RPC_OUTSTANDING_PING_THRESHOLD;
-  private Duration eth2StatusUpdateInterval = DEFAULT_ETH2_STATUS_UPDATE_INTERVAL;
+  private final Duration eth2StatusUpdateInterval = DEFAULT_ETH2_STATUS_UPDATE_INTERVAL;
   private int peerRateLimit = Constants.MAX_BLOCKS_PER_MINUTE;
   private int peerRequestLimit = 50;
 
@@ -146,6 +148,8 @@ protected DiscoveryNetwork<?> buildNetwork(final GossipEncoding gossipEncoding)
         new ReputationManager(metricsSystem, timeProvider, Constants.REPUTATION_MANAGER_CAPACITY);
     PreparedGossipMessageFactory defaultMessageFactory =
         (__, msg) -> gossipEncoding.prepareUnknownMessage(msg);
+    final GossipTopicFilter gossipTopicsFilter =
+        new Eth2GossipTopicFilter(recentChainData, gossipEncoding);
     final LibP2PNetwork p2pNetwork =
         new LibP2PNetwork(
             asyncRunner,
@@ -154,7 +158,8 @@ protected DiscoveryNetwork<?> buildNetwork(final GossipEncoding gossipEncoding)
             metricsSystem,
             rpcMethods,
             peerHandlers,
-            defaultMessageFactory);
+            defaultMessageFactory,
+            gossipTopicsFilter);
     final AttestationSubnetTopicProvider subnetTopicProvider =
         new AttestationSubnetTopicProvider(recentChainData, gossipEncoding);
     return DiscoveryNetwork.create(
```

### networking/eth2/src/main/java/tech/pegasys/teku/networking/eth2/gossip/topics/Eth2GossipTopicFilter.java
```diff
@@ -0,0 +1,90 @@
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
+package tech.pegasys.teku.networking.eth2.gossip.topics;
+
+import static tech.pegasys.teku.datastructures.util.BeaconStateUtil.compute_fork_digest;
+import static tech.pegasys.teku.networking.eth2.gossip.topics.TopicNames.getAttestationSubnetTopic;
+
+import com.google.common.base.Suppliers;
+import java.util.HashSet;
+import java.util.List;
+import java.util.Set;
+import java.util.function.Supplier;
+import org.apache.logging.log4j.LogManager;
+import org.apache.logging.log4j.Logger;
+import tech.pegasys.teku.datastructures.state.ForkInfo;
+import tech.pegasys.teku.networking.eth2.gossip.AggregateGossipManager;
+import tech.pegasys.teku.networking.eth2.gossip.AttesterSlashingGossipManager;
+import tech.pegasys.teku.networking.eth2.gossip.BlockGossipManager;
+import tech.pegasys.teku.networking.eth2.gossip.ProposerSlashingGossipManager;
+import tech.pegasys.teku.networking.eth2.gossip.VoluntaryExitGossipManager;
+import tech.pegasys.teku.networking.eth2.gossip.encoding.GossipEncoding;
+import tech.pegasys.teku.networking.p2p.libp2p.gossip.GossipTopicFilter;
+import tech.pegasys.teku.ssz.SSZTypes.Bytes4;
+import tech.pegasys.teku.storage.client.RecentChainData;
+import tech.pegasys.teku.util.config.Constants;
+
+public class Eth2GossipTopicFilter implements GossipTopicFilter {
+  private static final Logger LOG = LogManager.getLogger();
+  private final Supplier<Set<String>> relevantTopics;
+
+  public Eth2GossipTopicFilter(
+      final RecentChainData recentChainData, final GossipEncoding gossipEncoding) {
+    relevantTopics =
+        Suppliers.memoize(() -> computeRelevantTopics(recentChainData, gossipEncoding));
+  }
+
+  @Override
+  public boolean isRelevantTopic(final String topic) {
+    final boolean allowed = relevantTopics.get().contains(topic);
+    if (!allowed) {
+      LOG.debug("Ignoring subscription request for topic {}", topic);
+    }
+    return allowed;
+  }
+
+  private Set<String> computeRelevantTopics(
+      final RecentChainData recentChainData, final GossipEncoding gossipEncoding) {
+    final ForkInfo forkInfo = recentChainData.getHeadForkInfo().orElseThrow();
+    final Bytes4 forkDigest = forkInfo.getForkDigest();
+    final Set<String> topics = new HashSet<>();
+    addTopicsForForkDigest(gossipEncoding, forkDigest, topics);
+    recentChainData
+        .getNextFork()
+        .map(
+            nextFork ->
+                compute_fork_digest(
+                    nextFork.getCurrent_version(), forkInfo.getGenesisValidatorsRoot()))
+        .ifPresent(
+            nextForkDigest -> addTopicsForForkDigest(gossipEncoding, nextForkDigest, topics));
+    return topics;
+  }
+
+  private void addTopicsForForkDigest(
+      final GossipEncoding gossipEncoding, final Bytes4 forkDigest, final Set<String> topics) {
+    for (int i = 0; i < Constants.ATTESTATION_SUBNET_COUNT; i++) {
+      topics.add(getAttestationSubnetTopic(forkDigest, i, gossipEncoding));
+    }
+
+    for (String topicName :
+        List.of(
+            BlockGossipManager.TOPIC_NAME,
+            AggregateGossipManager.TOPIC_NAME,
+            AttesterSlashingGossipManager.TOPIC_NAME,
+            ProposerSlashingGossipManager.TOPIC_NAME,
+            VoluntaryExitGossipManager.TOPIC_NAME)) {
+      topics.add(TopicNames.getTopic(forkDigest, topicName, gossipEncoding));
+    }
+  }
+}
```

### networking/eth2/src/test/java/tech/pegasys/teku/networking/eth2/gossip/topics/Eth2GossipTopicFilterTest.java
```diff
@@ -0,0 +1,92 @@
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
+package tech.pegasys.teku.networking.eth2.gossip.topics;
+
+import static org.assertj.core.api.Assertions.assertThat;
+import static org.mockito.Mockito.mock;
+import static org.mockito.Mockito.when;
+import static tech.pegasys.teku.datastructures.util.BeaconStateUtil.compute_fork_digest;
+import static tech.pegasys.teku.networking.eth2.gossip.encoding.GossipEncoding.SSZ_SNAPPY;
+import static tech.pegasys.teku.networking.eth2.gossip.topics.TopicNames.getAttestationSubnetTopicName;
+
+import java.util.Optional;
+import org.junit.jupiter.api.BeforeEach;
+import org.junit.jupiter.api.Test;
+import tech.pegasys.teku.datastructures.state.Fork;
+import tech.pegasys.teku.datastructures.state.ForkInfo;
+import tech.pegasys.teku.datastructures.util.DataStructureUtil;
+import tech.pegasys.teku.networking.eth2.gossip.BlockGossipManager;
+import tech.pegasys.teku.ssz.SSZTypes.Bytes4;
+import tech.pegasys.teku.storage.client.RecentChainData;
+import tech.pegasys.teku.util.config.Constants;
+
+class Eth2GossipTopicFilterTest {
+  private final DataStructureUtil dataStructureUtil = new DataStructureUtil();
+  private final ForkInfo forkInfo = dataStructureUtil.randomForkInfo();
+  private final Fork nextFork = dataStructureUtil.randomFork();
+  private final RecentChainData recentChainData = mock(RecentChainData.class);
+  private final Bytes4 nextForkDigest =
+      compute_fork_digest(nextFork.getCurrent_version(), forkInfo.getGenesisValidatorsRoot());
+
+  private final Eth2GossipTopicFilter filter =
+      new Eth2GossipTopicFilter(recentChainData, SSZ_SNAPPY);
+
+  @BeforeEach
+  void setUp() {
+    when(recentChainData.getHeadForkInfo()).thenReturn(Optional.of(forkInfo));
+    when(recentChainData.getNextFork()).thenReturn(Optional.of(nextFork));
+  }
+
+  @Test
+  void shouldNotAllowIrrelevantTopics() {
+    assertThat(filter.isRelevantTopic("abc")).isFalse();
+  }
+
+  @Test
+  void shouldNotRequireNextForkToBePresent() {
+    when(recentChainData.getNextFork()).thenReturn(Optional.empty());
+    assertThat(filter.isRelevantTopic(getTopicName(BlockGossipManager.TOPIC_NAME))).isTrue();
+  }
+
+  @Test
+  void shouldConsiderTopicsForNextForkRelevant() {
+    assertThat(filter.isRelevantTopic(getNextForkTopicName(BlockGossipManager.TOPIC_NAME)))
+        .isTrue();
+  }
+
+  @Test
+  void shouldConsiderAllAttestationSubnetsRelevant() {
+    for (int i = 0; i < Constants.ATTESTATION_SUBNET_COUNT; i++) {
+      assertThat(filter.isRelevantTopic(getTopicName(getAttestationSubnetTopicName(i)))).isTrue();
+      assertThat(filter.isRelevantTopic(getNextForkTopicName(getAttestationSubnetTopicName(i))))
+          .isTrue();
+    }
+  }
+
+  @Test
+  void shouldNotAllowTopicsWithUnknownForkDigest() {
+    final String irrelevantTopic =
+        TopicNames.getTopic(
+            Bytes4.fromHexString("0x11223344"), BlockGossipManager.TOPIC_NAME, SSZ_SNAPPY);
+    assertThat(filter.isRelevantTopic(irrelevantTopic)).isFalse();
+  }
+
+  private String getTopicName(final String name) {
+    return TopicNames.getTopic(forkInfo.getForkDigest(), name, SSZ_SNAPPY);
+  }
+
+  private String getNextForkTopicName(final String name) {
+    return TopicNames.getTopic(nextForkDigest, name, SSZ_SNAPPY);
+  }
+}
```

### networking/eth2/src/testFixtures/java/tech/pegasys/teku/networking/eth2/Eth2NetworkFactory.java
```diff
@@ -57,6 +57,7 @@
 import tech.pegasys.teku.networking.eth2.gossip.encoding.GossipEncoding;
 import tech.pegasys.teku.networking.eth2.gossip.subnets.AttestationSubnetTopicProvider;
 import tech.pegasys.teku.networking.eth2.gossip.subnets.PeerSubnetSubscriptions;
+import tech.pegasys.teku.networking.eth2.gossip.topics.Eth2GossipTopicFilter;
 import tech.pegasys.teku.networking.eth2.gossip.topics.OperationProcessor;
 import tech.pegasys.teku.networking.eth2.gossip.topics.ProcessedAttestationSubscriptionProvider;
 import tech.pegasys.teku.networking.eth2.gossip.topics.VerifiedBlockAttestationsSubscriptionProvider;
@@ -66,6 +67,7 @@
 import tech.pegasys.teku.networking.p2p.DiscoveryNetwork;
 import tech.pegasys.teku.networking.p2p.connection.TargetPeerRange;
 import tech.pegasys.teku.networking.p2p.libp2p.LibP2PNetwork;
+import tech.pegasys.teku.networking.p2p.libp2p.gossip.GossipTopicFilter;
 import tech.pegasys.teku.networking.p2p.network.GossipConfig;
 import tech.pegasys.teku.networking.p2p.network.NetworkConfig;
 import tech.pegasys.teku.networking.p2p.network.P2PNetwork;
@@ -198,6 +200,8 @@ protected Eth2Network buildNetwork(final NetworkConfig config) {
                 Constants.REPUTATION_MANAGER_CAPACITY);
         final AttestationSubnetTopicProvider subnetTopicProvider =
             new AttestationSubnetTopicProvider(recentChainData, gossipEncoding);
+        final GossipTopicFilter gossipTopicsFilter =
+            new Eth2GossipTopicFilter(recentChainData, gossipEncoding);
         final KeyValueStore<String, Bytes> keyValueStore = new MemKeyValueStore<>();
         final DiscoveryNetwork<?> network =
             DiscoveryNetwork.create(
@@ -211,7 +215,8 @@ protected Eth2Network buildNetwork(final NetworkConfig config) {
                     METRICS_SYSTEM,
                     new ArrayList<>(rpcMethods),
                     peerHandlers,
-                    (__, msg) -> gossipEncoding.prepareUnknownMessage(msg)),
+                    (__, msg) -> gossipEncoding.prepareUnknownMessage(msg),
+                    gossipTopicsFilter),
                 new Eth2PeerSelectionStrategy(
                     config.getTargetPeerRange(),
                     gossipNetwork ->
```

### networking/p2p/src/main/java/tech/pegasys/teku/networking/p2p/libp2p/LibP2PNetwork.java
```diff
@@ -53,6 +53,7 @@
 import tech.pegasys.teku.networking.p2p.gossip.PreparedGossipMessageFactory;
 import tech.pegasys.teku.networking.p2p.gossip.TopicChannel;
 import tech.pegasys.teku.networking.p2p.gossip.TopicHandler;
+import tech.pegasys.teku.networking.p2p.libp2p.gossip.GossipTopicFilter;
 import tech.pegasys.teku.networking.p2p.libp2p.gossip.LibP2PGossipNetwork;
 import tech.pegasys.teku.networking.p2p.libp2p.rpc.RpcHandler;
 import tech.pegasys.teku.networking.p2p.network.NetworkConfig;
@@ -89,7 +90,8 @@ public LibP2PNetwork(
       final MetricsSystem metricsSystem,
       final List<RpcMethod> rpcMethods,
       final List<PeerHandler> peerHandlers,
-      final PreparedGossipMessageFactory defaultMessageFactory) {
+      final PreparedGossipMessageFactory defaultMessageFactory,
+      final GossipTopicFilter gossipTopicFilter) {
     this.privKey = config.getPrivateKey();
     this.nodeId = new LibP2PNodeId(PeerId.fromPubKey(privKey.publicKey()));
 
@@ -104,6 +106,7 @@ public LibP2PNetwork(
             metricsSystem,
             config.getGossipConfig(),
             defaultMessageFactory,
+            gossipTopicFilter,
             config.getWireLogsConfig().isLogWireGossip());
 
     // Setup rpc methods
```

### networking/p2p/src/main/java/tech/pegasys/teku/networking/p2p/libp2p/gossip/GossipTopicFilter.java
```diff
@@ -0,0 +1,19 @@
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
+package tech.pegasys.teku.networking.p2p.libp2p.gossip;
+
+@FunctionalInterface
+public interface GossipTopicFilter {
+  boolean isRelevantTopic(String topic);
+}
```

### networking/p2p/src/main/java/tech/pegasys/teku/networking/p2p/libp2p/gossip/LibP2PGossipNetwork.java
```diff
@@ -22,12 +22,16 @@
 import io.libp2p.core.pubsub.Topic;
 import io.libp2p.core.pubsub.ValidationResult;
 import io.libp2p.pubsub.FastIdSeenCache;
+import io.libp2p.pubsub.MaxCountTopicSubscriptionFilter;
+import io.libp2p.pubsub.PubsubProtocol;
 import io.libp2p.pubsub.PubsubRouterMessageValidator;
 import io.libp2p.pubsub.SeenCache;
 import io.libp2p.pubsub.TTLSeenCache;
+import io.libp2p.pubsub.TopicSubscriptionFilter;
 import io.libp2p.pubsub.gossip.Gossip;
 import io.libp2p.pubsub.gossip.GossipParams;
 import io.libp2p.pubsub.gossip.GossipRouter;
+import io.libp2p.pubsub.gossip.GossipScoreParams;
 import io.netty.buffer.Unpooled;
 import io.netty.channel.ChannelHandler;
 import io.netty.handler.logging.LogLevel;
@@ -43,6 +47,7 @@
 import org.apache.logging.log4j.LogManager;
 import org.apache.logging.log4j.Logger;
 import org.apache.tuweni.bytes.Bytes;
+import org.apache.tuweni.crypto.Hash;
 import org.hyperledger.besu.plugin.services.MetricsSystem;
 import org.jetbrains.annotations.NotNull;
 import tech.pegasys.teku.infrastructure.async.SafeFuture;
@@ -72,10 +77,13 @@ public static LibP2PGossipNetwork create(
       MetricsSystem metricsSystem,
       GossipConfig gossipConfig,
       PreparedGossipMessageFactory defaultMessageFactory,
+      GossipTopicFilter gossipTopicFilter,
       boolean logWireGossip) {
 
     TopicHandlers topicHandlers = new TopicHandlers();
-    Gossip gossip = createGossip(gossipConfig, logWireGossip, defaultMessageFactory, topicHandlers);
+    Gossip gossip =
+        createGossip(
+            gossipConfig, logWireGossip, defaultMessageFactory, gossipTopicFilter, topicHandlers);
     PubsubPublisherApi publisher = gossip.createPublisher(null, NULL_SEQNO_GENERATOR);
 
     return new LibP2PGossipNetwork(metricsSystem, gossip, publisher, topicHandlers);
@@ -85,6 +93,7 @@ private static Gossip createGossip(
       GossipConfig gossipConfig,
       boolean gossipLogsEnabled,
       PreparedGossipMessageFactory defaultMessageFactory,
+      GossipTopicFilter gossipTopicFilter,
       TopicHandlers topicHandlers) {
     GossipParams gossipParams =
         GossipParams.builder()
@@ -98,14 +107,31 @@ private static Gossip createGossip(
             .heartbeatInterval(gossipConfig.getHeartbeatInterval())
             .floodPublish(true)
             .seenTTL(gossipConfig.getSeenTTL())
+            .maxPublishedMessages(1000)
+            .maxTopicsPerPublishedMessage(1)
+            .maxSubscriptions(200)
+            .maxGraftMessages(200)
+            .maxPruneMessages(200)
+            .maxPeersPerPruneMessage(1000)
+            .maxIHaveLength(5000)
+            .maxIWantMessageIds(5000)
             .build();
 
+    final TopicSubscriptionFilter subscriptionFilter =
+        new MaxCountTopicSubscriptionFilter(100, 200, gossipTopicFilter::isRelevantTopic);
     GossipRouter router =
-        new GossipRouter(gossipParams) {
+        new GossipRouter(
+            gossipParams,
+            new GossipScoreParams(),
+            PubsubProtocol.Gossip_V_1_1,
+            subscriptionFilter) {
 
           final SeenCache<Optional<ValidationResult>> seenCache =
               new TTLSeenCache<>(
-                  new FastIdSeenCache<>(msg -> msg.getProtobufMessage().getData()),
+                  new FastIdSeenCache<>(
+                      msg ->
+                          Bytes.wrap(
+                              Hash.sha2_256(msg.getProtobufMessage().getData().toByteArray()))),
                   gossipParams.getSeenTTL(),
                   getCurTimeMillis());
 
```

### networking/p2p/src/main/java/tech/pegasys/teku/networking/p2p/libp2p/gossip/PreparedPubsubMessage.java
```diff
@@ -17,6 +17,7 @@
 import com.google.common.base.Suppliers;
 import io.libp2p.core.pubsub.MessageApi;
 import io.libp2p.etc.types.WBytes;
+import io.libp2p.pubsub.AbstractPubsubMessage;
 import io.libp2p.pubsub.PubsubMessage;
 import io.libp2p.pubsub.gossip.GossipRouter;
 import org.jetbrains.annotations.NotNull;
@@ -31,7 +32,7 @@
  * GossipRouter#getMessageFactory()} invocation can later be accessed when the gossip message is
  * handled: {@link MessageApi#getOriginalMessage()}
  */
-public class PreparedPubsubMessage implements PubsubMessage {
+public class PreparedPubsubMessage extends AbstractPubsubMessage {
 
   private final Message protobufMessage;
   private final PreparedGossipMessage preparedMessage;
```

### networking/p2p/src/testFixtures/java/tech/pegasys/teku/network/p2p/DiscoveryNetworkFactory.java
```diff
@@ -114,7 +114,8 @@ public DiscoveryNetwork<Peer> buildAndStart() throws Exception {
                     Collections.emptyList(),
                     (__1, __2) -> {
                       throw new UnsupportedOperationException();
-                    }),
+                    },
+                    topic -> true),
                 new SimplePeerSelectionStrategy(config.getTargetPeerRange()),
                 config);
         try {
```
