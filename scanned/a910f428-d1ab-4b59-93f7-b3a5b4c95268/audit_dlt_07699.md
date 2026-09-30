# [?] Fixes: GHSA-xw6x-9526-6w9r Bound the DiscV4 inbound packet pipeline (#11105)

## Summary
Severity: Unknown
Chain: Ethereum
Component: besu-eth/besu
Published: 2026-08-20
Source: https://github.com/besu-eth/besu/commit/6d731706cb6d9046085af182beacf6ef93eb6888
Type: security-commit

## Details
Fixes: GHSA-xw6x-9526-6w9r Bound the DiscV4 inbound packet pipeline (#11105)

Signed-off-by: Sally MacFarlane <macfarla.github@gmail.com>

## Patch
### CHANGELOG.md
```diff
@@ -68,6 +68,7 @@
 - Removed the legacy `PANTHEON_` environment variable prefix for configuration options, everyone should already use the `BESU_` prefix at this time.
 
 ### Bug fixes
+- Bound the DiscV4 inbound packet pipeline with an admission gate (256 in-flight packets) and a bounded crypto executor queue, preventing a UDP flood from exhausting memory.
 - Cap the QBFT/IBFT round change number to prevent unbounded memory growth from malformed round-change messages.
 - Cap pre-STATUS RLPx connections and close them on eviction to prevent resource exhaustion.
 - Improve logging for malformed discv4 UDP packets.
```

### ethereum/p2p/src/main/java/org/hyperledger/besu/ethereum/p2p/discovery/discv4/NettyPeerDiscoveryAgent.java
```diff
@@ -33,15 +33,19 @@
 import org.hyperledger.besu.ethereum.p2p.permissions.PeerPermissions;
 import org.hyperledger.besu.ethereum.p2p.rlpx.RlpxAgent;
 import org.hyperledger.besu.plugin.services.MetricsSystem;
+import org.hyperledger.besu.plugin.services.metrics.Counter;
 
 import java.net.SocketException;
 import java.nio.channels.UnsupportedAddressTypeException;
+import java.util.concurrent.ArrayBlockingQueue;
 import java.util.concurrent.CompletableFuture;
 import java.util.concurrent.Executor;
 import java.util.concurrent.ExecutorService;
 import java.util.concurrent.Executors;
 import java.util.concurrent.ScheduledExecutorService;
 import java.util.concurrent.ThreadFactory;
+import java.util.concurrent.ThreadPoolExecutor;
+import java.util.concurrent.TimeUnit;
 import java.util.concurrent.atomic.AtomicInteger;
 import java.util.function.Predicate;
 
@@ -55,6 +59,9 @@ public class NettyPeerDiscoveryAgent extends PeerDiscoveryAgentV4 {
 
   private static final Logger LOG = LoggerFactory.getLogger(NettyPeerDiscoveryAgent.class);
 
+  // At most 2 signing tasks per admitted packet: a PONG response and a bonding PING.
+  static final int CRYPTO_QUEUE_CAPACITY = 2 * MAX_INFLIGHT_INBOUND_PACKETS;
+
   // Lazily created on first use (via prepareHandlers(), only reached when config.isEnabled()),
   // so a node running with discovery disabled doesn't pay for 3 permanently-idle threads.
   private ScheduledExecutorService timerScheduler;
@@ -133,6 +140,9 @@ protected AsyncExecutor createDecodeExecutor() {
    * Returns the same single-threaded scheduler that drives timers, so timer callbacks and
    * dispatched packet handling share a single thread (matching the Vert.x event-loop ordering the
    * migration to Netty otherwise loses).
+   *
+   * <p>Its queue is unbounded, but its depth is bounded by the ingress gate and {@link
+   * #CRYPTO_QUEUE_CAPACITY} that feed it. Preserve that when adding work here.
    */
   @Override
   protected Executor createDispatchExecutor() {
@@ -151,10 +161,19 @@ private synchronized ScheduledExecutorService timerScheduler() {
   private synchronized ExecutorService cryptoExecutor() {
     if (cryptoExecutor == null) {
       final AtomicInteger threadCount = new AtomicInteger(0);
+      final Counter dropped = droppedPacketCounter("crypto_capacity");
       cryptoExecutor =
-          Executors.newFixedThreadPool(
+          new ThreadPoolExecutor(
+              2,
               2,
-              (ThreadFactory) r -> new Thread(r, "discv4-crypto-" + threadCount.getAndIncrement()));
+              0L,
+              TimeUnit.MILLISECONDS,
+              new ArrayBlockingQueue<>(CRYPTO_QUEUE_CAPACITY),
+              (ThreadFactory) r -> new Thread(r, "discv4-crypto-" + threadCount.getAndIncrement()),
+              // Must not throw: createPacket logs at ERROR, so an attacker could trade the OOM for
+              // a log flood. A dropped task loses one send; the interaction retry timer recovers
+              // it.
+              (r, executor) -> dropped.inc());
     }
     return cryptoExecutor;
   }
```

### ethereum/p2p/src/main/java/org/hyperledger/besu/ethereum/p2p/discovery/discv4/PeerDiscoveryAgentV4.java
```diff
@@ -38,7 +38,10 @@
 import org.hyperledger.besu.ethereum.p2p.peers.PeerId;
 import org.hyperledger.besu.ethereum.p2p.permissions.PeerPermissions;
 import org.hyperledger.besu.ethereum.p2p.rlpx.RlpxAgent;
+import org.hyperledger.besu.metrics.BesuMetricCategory;
 import org.hyperledger.besu.plugin.services.MetricsSystem;
+import org.hyperledger.besu.plugin.services.metrics.Counter;
+import org.hyperledger.besu.plugin.services.metrics.LabelledMetric;
 import org.hyperledger.besu.util.NetworkUtility;
 
 import java.net.InetSocketAddress;
@@ -48,6 +51,8 @@
 import java.util.concurrent.CopyOnWriteArrayList;
 import java.util.concurrent.Executor;
 import java.util.concurrent.atomic.AtomicBoolean;
+import java.util.concurrent.atomic.AtomicInteger;
+import java.util.concurrent.atomic.AtomicLong;
 import java.util.stream.Collectors;
 import java.util.stream.Stream;
 
@@ -71,6 +76,15 @@ public abstract class PeerDiscoveryAgentV4 implements PeerDiscoveryAgent {
   // clients ignore that, so we add in a little extra padding. Also used by NettyTransport to
   // drop oversized datagrams before copying them off the channel's buffer.
   public static final int MAX_PACKET_SIZE_BYTES = 1600;
+
+  /**
+   * Maximum inbound packets in the decode and dispatch stages at once. Sized by latency rather than
+   * memory: a full gate adds ~130-260 ms at the ~1-2k packets/s the decode thread sustains.
+   */
+  public static final int MAX_INFLIGHT_INBOUND_PACKETS = 256;
+
+  private static final long SATURATION_LOG_INTERVAL_MS = 300_000L;
+
   protected final List<DiscoveryPeerV4> bootstrapPeers;
   private final List<PeerRequirement> peerRequirements = new CopyOnWriteArrayList<>();
   private final PeerPermissions peerPermissions;
@@ -116,6 +130,13 @@ public abstract class PeerDiscoveryAgentV4 implements PeerDiscoveryAgent {
   // No corresponding start gate at this level — see start() for rationale.
   protected final AtomicBoolean stopGate = new AtomicBoolean(false);
 
+  // Permits held by packets currently in the decode + dispatch stages.
+  private final AtomicInteger inflightInboundPackets = new AtomicInteger();
+  private final AtomicLong lastSaturationLogMs = new AtomicLong();
+  private final LabelledMetric<Counter> droppedPackets;
+  private final Counter admissionDropCounter;
+  private final Counter stoppedDropCounter;
+
   protected PeerDiscoveryAgentV4(
       final NodeKey nodeKey,
       final DiscoveryConfiguration config,
@@ -129,6 +150,19 @@ protected PeerDiscoveryAgentV4(
       final PacketSerializer packetSerializer,
       final PacketDeserializer packetDeserializer) {
     this.metricsSystem = metricsSystem;
+    this.droppedPackets =
+        metricsSystem.createLabelledCounter(
+            BesuMetricCategory.NETWORK,
+            "discovery_packets_dropped_total",
+            "Total number of inbound DiscV4 packets dropped before being handled",
+            "reason");
+    this.admissionDropCounter = droppedPackets.labels("admission_limit");
+    this.stoppedDropCounter = droppedPackets.labels("stopped");
+    metricsSystem.createIntegerGauge(
+        BesuMetricCategory.NETWORK,
+        "discovery_inflight_inbound_packets_current",
+        "Current number of inbound DiscV4 packets in the decode and dispatch stages",
+        inflightInboundPackets::get);
     checkArgument(nodeKey != null, "nodeKey cannot be null");
     checkArgument(config != null, "provided configuration cannot be null");
 
@@ -154,6 +188,10 @@ protected PeerDiscoveryAgentV4(
     this.packetDeserializer = packetDeserializer;
   }
 
+  protected Counter droppedPacketCounter(final String reason) {
+    return droppedPackets.labels(reason);
+  }
+
   protected abstract TimerUtil createTimer();
 
   protected abstract PeerDiscoveryController.AsyncExecutor createWorkerExecutor();
@@ -204,44 +242,70 @@ private void handleRawIncoming(final InetSocketAddress sender, final Bytes data)
     // After stop() is called, the transport may still deliver queued packets. Drop them quietly
     // instead of letting workerExecutor.submit throw RejectedExecutionException.
     if (stopGate.get()) {
+      stoppedDropCounter.inc();
       return;
     }
     if (!validatePacketSize(data.size())) {
       LOG.trace("Discarding over-sized packet. Actual size (bytes): {}", data.size());
       return;
     }
+    // Ingress is the only place dropping is free: an undelivered UDP datagram is indistinguishable
+    // from network loss, and DiscV4 peers retry.
+    if (inflightInboundPackets.incrementAndGet() > MAX_INFLIGHT_INBOUND_PACKETS) {
+      inflightInboundPackets.decrementAndGet();
+      admissionDropCounter.inc();
+      logSaturation();
+      return;
+    }
     decodeExecutor
         .<Packet>execute(() -> packetDeserializer.decode(data))
         .whenCompleteAsync(
             (packet, err) -> {
-              if (stopGate.get()) {
-                // stop() was called after this decode was already queued; drop the late
-                // completion instead of forwarding it into a PeerDiscoveryController that may
-                // already be stopped.
-                return;
-              }
-              if (err == null) {
-                final Endpoint endpoint =
-                    new Endpoint(sender.getHostString(), sender.getPort(), Optional.empty());
-                try {
-                  handleIncomingPacket(endpoint, packet);
-                } catch (final RuntimeException e) {
-                  LOG.error("Encountered error while handling packet", e);
+              try {
+                if (stopGate.get()) {
+                  // stop() was called after this decode was already queued; drop the late
+                  // completion instead of forwarding it into a PeerDiscoveryController that may
+                  // already be stopped.
+                  return;
                 }
-              } else {
-                if (err instanceof PeerDiscoveryPacketDecodingException
-                    || err instanceof DecodeException
-                    || err instanceof EndOfRLPException) {
-                  LOG.trace(
-                      "Discarding invalid peer discovery packet: {}, {}", err.getMessage(), err);
+                if (err == null) {
+                  final Endpoint endpoint =
+                      new Endpoint(sender.getHostString(), sender.getPort(), Optional.empty());
+                  try {
+                    handleIncomingPacket(endpoint, packet);
+                  } catch (final RuntimeException e) {
+                    LOG.error("Encountered error while handling packet", e);
+                  }
                 } else {
-                  LOG.error("Encountered error while handling packet", err);
+                  if (err instanceof PeerDiscoveryPacketDecodingException
+                      || err instanceof DecodeException
+                      || err instanceof EndOfRLPException) {
+                    LOG.trace(
+                        "Discarding invalid peer discovery packet: {}, {}", err.getMessage(), err);
+                  } else {
+                    LOG.error("Encountered error while handling packet", err);
+                  }
                 }
+              } finally {
+                // Must cover every exit: a leaked permit permanently shrinks capacity.
+                inflightInboundPackets.decrementAndGet();
               }
             },
             dispatchExecutor);
   }
 
+  /** Rate-limited so that a packet flood cannot become a log flood. */
+  private void logSaturation() {
+    final long now = System.currentTimeMillis();
+    final long last = lastSaturationLogMs.get();
+    if (now - last >= SATURATION_LOG_INTERVAL_MS && lastSaturationLogMs.compareAndSet(last, now)) {
+      LOG.warn(
+          "Dropping inbound discovery packets: {} already in flight. See the"
+              + " discovery_packets_dropped_total metric.",
+          MAX_INFLIGHT_INBOUND_PACKETS);
+    }
+  }
+
   @Override
   public CompletableFuture<Integer> start(final int rlpxTcpPort) {
     // Note: no idempotency guard at this level. Tests legitimately re-invoke start() with a
```

### ethereum/p2p/src/test/java/org/hyperledger/besu/ethereum/p2p/discovery/discv4/NettyPeerDiscoveryAgentTest.java
```diff
@@ -32,6 +32,7 @@
 import org.hyperledger.besu.ethereum.p2p.discovery.NodeRecordManager;
 import org.hyperledger.besu.ethereum.p2p.discovery.discv4.internal.DiscoveryPeerV4;
 import org.hyperledger.besu.ethereum.p2p.discovery.discv4.internal.PacketType;
+import org.hyperledger.besu.ethereum.p2p.discovery.discv4.internal.PeerDiscoveryController;
 import org.hyperledger.besu.ethereum.p2p.discovery.discv4.internal.packet.DaggerPacketPackage;
 import org.hyperledger.besu.ethereum.p2p.discovery.discv4.internal.packet.Packet;
 import org.hyperledger.besu.ethereum.p2p.discovery.discv4.internal.packet.PacketPackage;
@@ -41,6 +42,7 @@
 import org.hyperledger.besu.ethereum.p2p.permissions.PeerPermissions;
 import org.hyperledger.besu.ethereum.p2p.rlpx.ConnectSource;
 import org.hyperledger.besu.ethereum.p2p.rlpx.RlpxAgent;
+import org.hyperledger.besu.metrics.StubMetricsSystem;
 import org.hyperledger.besu.metrics.noop.NoOpMetricsSystem;
 import org.hyperledger.besu.nat.NatService;
 
@@ -278,6 +280,176 @@ void start_withEphemeralIpv6BindPort_advertisesTheTransportsResolvedPortNotZero(
     }
   }
 
+  private NettyPeerDiscoveryAgent agentWithMetrics(
+      final StubMetricsSystem metrics, final TrackingTransport agentTransport) {
+    final NodeKey agentNodeKey = NodeKeyUtils.generate();
+    final DiscoveryConfiguration config = new DiscoveryConfiguration();
+    config.setBindHost("127.0.0.1");
+    config.setAdvertisedHost("127.0.0.1");
+    config.setBindPort(0);
+    config.setEnodeBootnodes(Collections.emptyList());
+
+    final ForkIdManager forkIdManager = mock(ForkIdManager.class);
+    lenient()
+        .when(forkIdManager.getForkIdForChainHead())
+        .thenReturn(new ForkId(Bytes.EMPTY, Bytes.EMPTY));
+
+    final RlpxAgent agentRlpxAgent = mock(RlpxAgent.class);
+    lenient()
+        .when(agentRlpxAgent.connect(any(), any(ConnectSource.class)))
+        .thenReturn(CompletableFuture.failedFuture(new RuntimeException()));
+
+    return NettyPeerDiscoveryAgent.createWithTransport(
+        agentNodeKey,
+        config,
+        PeerPermissions.noop(),
+        metrics,
+        new NodeRecordManager(
+            new InMemoryKeyValueStorageProvider(),
+            agentNodeKey,
+            forkIdManager,
+            new NatService(Optional.empty())),
+        forkIdManager,
+        agentRlpxAgent,
+        agentTransport);
+  }
+
+  private static void drain(final Executor dispatchExecutor) throws Exception {
+    final CountDownLatch sentinelRan = new CountDownLatch(1);
+    dispatchExecutor.execute(sentinelRan::countDown);
+    assertThat(sentinelRan.await(5, TimeUnit.SECONDS)).isTrue();
+  }
+
+  @Test
+  void inboundAdmission_capsInflightPackets_andCountsDrops() throws Exception {
+    final StubMetricsSystem metrics = new StubMetricsSystem();
+    final TrackingTransport metricsTransport = new TrackingTransport();
+    final NettyPeerDiscoveryAgent metricsAgent = agentWithMetrics(metrics, metricsTransport);
+    try {
+      metricsAgent.start(30303).join();
+
+      // Submitting directly consumes no admission permit, so the gate stays at full capacity.
+      final CountDownLatch releaseDecodeThread = new CountDownLatch(1);
+      final CountDownLatch decodeThreadBusy = new CountDownLatch(1);
+      metricsAgent
+          .createDecodeExecutor()
+          .execute(
+              () -> {
+                decodeThreadBusy.countDown();
+                try {
+                  releaseDecodeThread.await(5, TimeUnit.SECONDS);
+                } catch (final InterruptedException e) {
+                  Thread.currentThread().interrupt();
+                }
+                return null;
+              });
+      assertThat(decodeThreadBusy.await(5, TimeUnit.SECONDS)).isTrue();
+
+      final int floodSize = 1000;
+      final InetSocketAddress sender =
+          new InetSocketAddress(InetAddress.getLoopbackAddress(), 30303);
+      final Bytes encoded = metricsAgent.packetSerializer.encode(packet);
+      for (int i = 0; i < floodSize; i++) {
+        metricsTransport.inboundHandler.onPacket(sender, encoded);
+      }
+
+      assertThat(metrics.getGaugeValue("discovery_inflight_inbound_packets_current"))
+          .isEqualTo(PeerDiscoveryAgentV4.MAX_INFLIGHT_INBOUND_PACKETS);
+      assertThat(metrics.getCounterValue("discovery_packets_dropped_total", "admission_limit"))
+          .isEqualTo(floodSize - PeerDiscoveryAgentV4.MAX_INFLIGHT_INBOUND_PACKETS);
+
+      releaseDecodeThread.countDown();
+    } finally {
+      metricsAgent.stop().join();
+    }
+  }
+
+  @Test
+  void admissionPermit_isReleased_afterDispatchCompletes() throws Exception {
+    final StubMetricsSystem metrics = new StubMetricsSystem();
+    final TrackingTransport metricsTransport = new TrackingTransport();
+    final NettyPeerDiscoveryAgent metricsAgent = agentWithMetrics(metrics, metricsTransport);
+    try {
+      metricsAgent.start(30303).join();
+
+      metricsTransport.inboundHandler.onPacket(
+          new InetSocketAddress(InetAddress.getLoopbackAddress(), 30303),
+          metricsAgent.packetSerializer.encode(packet));
+
+      // Decode is single-threaded and FIFO, so a no-op queued after the real decode completes only
+      // once that decode has posted its continuation to the dispatch thread.
+      metricsAgent.createDecodeExecutor().execute(() -> null).get(5, TimeUnit.SECONDS);
+      drain(metricsAgent.createDispatchExecutor());
+
+      assertThat(metrics.getGaugeValue("discovery_inflight_inbound_packets_current")).isZero();
+    } finally {
+      metricsAgent.stop().join();
+    }
+  }
+
+  @Test
+  void admissionPermit_isReleased_whenDecodeFails() throws Exception {
+    final StubMetricsSystem metrics = new StubMetricsSystem();
+    final TrackingTransport metricsTransport = new TrackingTransport();
+    final NettyPeerDiscoveryAgent metricsAgent = agentWithMetrics(metrics, metricsTransport);
+    try {
+      metricsAgent.start(30303).join();
+
+      // Size-valid but undecodable: exercises the error branch of the dispatch continuation.
+      metricsTransport.inboundHandler.onPacket(
+          new InetSocketAddress(InetAddress.getLoopbackAddress(), 30303),
+          Bytes.repeat((byte) 0x2a, 200));
+
+      metricsAgent.createDecodeExecutor().execute(() -> null).get(5, TimeUnit.SECONDS);
+      drain(metricsAgent.createDispatchExecutor());
+
+      assertThat(metrics.getGaugeValue("discovery_inflight_inbound_packets_current")).isZero();
+    } finally {
+      metricsAgent.stop().join();
+    }
+  }
+
+  @Test
+  void cryptoQueue_dropsExcess_andCountsDrops() throws Exception {
+    final StubMetricsSystem metrics = new StubMetricsSystem();
+    final NettyPeerDiscoveryAgent metricsAgent = agentWithMetrics(metrics, new TrackingTransport());
+    try {
+      final PeerDiscoveryController.AsyncExecutor workerExecutor =
+          metricsAgent.createWorkerExecutor();
+
+      final CountDownLatch releaseCryptoThreads = new CountDownLatch(1);
+      final CountDownLatch cryptoThreadsBusy = new CountDownLatch(2);
+      for (int i = 0; i < 2; i++) {
+        workerExecutor.execute(
+            () -> {
+              cryptoThreadsBusy.countDown();
+              try {
+                releaseCryptoThreads.await(5, TimeUnit.SECONDS);
+              } catch (final InterruptedException e) {
+                Thread.currentThread().interrupt();
+              }
+              return null;
+            });
+      }
+      assertThat(cryptoThreadsBusy.await(5, TimeUnit.SECONDS)).isTrue();
+
+      for (int i = 0; i < NettyPeerDiscoveryAgent.CRYPTO_QUEUE_CAPACITY; i++) {
+        workerExecutor.execute(() -> null);
+      }
+
+      // Must not throw: ScheduledExecutorAsyncExecutor catches RuntimeException into the returned
+      // future, so an AbortPolicy would complete it exceptionally and log an ERROR per drop.
+      final CompletableFuture<Object> dropped = workerExecutor.execute(() -> null);
+      assertThat(dropped).isNotCompleted();
+      assertThat(metrics.getCounterValue("discovery_packets_dropped_total", "crypto_capacity"))
+          .isEqualTo(1);
+
+      releaseCryptoThreads.countDown();
+    } finally {
+      metricsAgent.stop().join();
+    }
+  }
+
   private static class TrackingTransport implements Transport {
     final AtomicInteger sendCallCount = new AtomicInteger(0);
     volatile InboundV4Handler inboundHandler;
```
