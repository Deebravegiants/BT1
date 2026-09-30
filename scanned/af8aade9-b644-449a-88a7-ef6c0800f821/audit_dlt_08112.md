# [?] Fix race condition in router tests (#1392)

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ACINQ/eclair
Published: 2020-04-27
Source: https://github.com/ACINQ/eclair/commit/6aced1bf1cd0359ffc7db1ab03efad8c26123516
Type: security-commit

## Details
Fix race condition in router tests (#1392)

Caused by the automated generation of node announcement following
c9f94eec6f43b1ab1f2ae9a2f3c198f09dde4a94.

## Patch
### eclair-core/src/test/scala/fr/acinq/eclair/router/BaseRouterSpec.scala
```diff
@@ -24,10 +24,10 @@ import fr.acinq.bitcoin.{Block, ByteVector32, Transaction, TxOut}
 import fr.acinq.eclair.TestConstants.Alice
 import fr.acinq.eclair.blockchain.{UtxoStatus, ValidateRequest, ValidateResult, WatchSpentBasic}
 import fr.acinq.eclair.channel.{CommitmentsSpec, LocalChannelUpdate}
-import fr.acinq.eclair.crypto.LocalKeyManager
+import fr.acinq.eclair.crypto.{LocalKeyManager, TransportHandler}
 import fr.acinq.eclair.io.Peer.PeerRoutingMessage
 import fr.acinq.eclair.router.Announcements._
-import fr.acinq.eclair.router.Router.{ChannelDesc, ChannelMeta, PrivateChannel}
+import fr.acinq.eclair.router.Router.{ChannelDesc, ChannelMeta, GossipDecision, PrivateChannel}
 import fr.acinq.eclair.transactions.Scripts
 import fr.acinq.eclair.wire._
 import fr.acinq.eclair.{TestkitBaseClass, randomKey, _}
@@ -54,12 +54,12 @@ abstract class BaseRouterSpec extends TestkitBaseClass {
   val testKeyManager = new LocalKeyManager(seed, Block.RegtestGenesisBlock.hash)
 
   val (priv_a, priv_b, priv_c, priv_d, priv_e, priv_f, priv_g, priv_h) = (testKeyManager.nodeKey.privateKey, randomKey, randomKey, randomKey, randomKey, randomKey, randomKey, randomKey)
-  val (a, b, c, d, e, f, g, h) = (testKeyManager.nodeId, priv_b.publicKey, priv_c.publicKey, priv_d.publicKey, priv_e.publicKey, priv_f.publicKey, priv_g.publicKey, priv_h.publicKey)
+  val (a, b, c, d, e, f, g, h) = (priv_a.publicKey, priv_b.publicKey, priv_c.publicKey, priv_d.publicKey, priv_e.publicKey, priv_f.publicKey, priv_g.publicKey, priv_h.publicKey)
 
   val (priv_funding_a, priv_funding_b, priv_funding_c, priv_funding_d, priv_funding_e, priv_funding_f, priv_funding_g, priv_funding_h) = (randomKey, randomKey, randomKey, randomKey, randomKey, randomKey, randomKey, randomKey)
   val (funding_a, funding_b, funding_c, funding_d, funding_e, funding_f, funding_g, funding_h) = (priv_funding_a.publicKey, priv_funding_b.publicKey, priv_funding_c.publicKey, priv_funding_d.publicKey, priv_funding_e.publicKey, priv_funding_f.publicKey, priv_funding_g.publicKey, priv_funding_h.publicKey)
 
-  val node_a = makeNodeAnnouncement(priv_a, "node-A", Color(15, 10, -70), Nil, hex"0200")
+  // in the tests we are 'a', we don't define a node_a, it will be generated automatically when the router validates the first channel
   val node_b = makeNodeAnnouncement(priv_b, "node-B", Color(50, 99, -80), Nil, hex"")
   val node_c = makeNodeAnnouncement(priv_c, "node-C", Color(123, 100, -40), Nil, hex"0200")
   val node_d = makeNodeAnnouncement(priv_d, "node-D", Color(-120, -20, 60), Nil, hex"00")
@@ -118,6 +118,7 @@ abstract class BaseRouterSpec extends TestkitBaseClass {
       // let's set up the router
       val sender = TestProbe()
       val peerConnection = TestProbe()
+      peerConnection.ignoreMsg { case _: TransportHandler.ReadAck => true }
       val watcher = TestProbe()
       import com.softwaremill.quicklens._
       val nodeParams = Alice.nodeParams
@@ -131,7 +132,6 @@ abstract class BaseRouterSpec extends TestkitBaseClass {
       peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, chan_ef))
       peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, chan_gh))
       // then nodes
-      peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, node_a))
       peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, node_b))
       peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, node_c))
       peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, node_d))
@@ -170,13 +170,37 @@ abstract class BaseRouterSpec extends TestkitBaseClass {
       watcher.expectMsgType[WatchSpentBasic]
       watcher.expectMsgType[WatchSpentBasic]
       watcher.expectMsgType[WatchSpentBasic]
-
+      // all messages are acked
+      peerConnection.expectMsgAllOf(
+        GossipDecision.Accepted(chan_ab),
+        GossipDecision.Accepted(chan_bc),
+        GossipDecision.Accepted(chan_cd),
+        GossipDecision.Accepted(chan_ef),
+        GossipDecision.Accepted(chan_gh),
+        GossipDecision.Accepted(update_ab),
+        GossipDecision.Accepted(update_ba),
+        GossipDecision.Accepted(update_bc),
+        GossipDecision.Accepted(update_cb),
+        GossipDecision.Accepted(update_cd),
+        GossipDecision.Accepted(update_dc),
+        GossipDecision.Accepted(update_ef),
+        GossipDecision.Accepted(update_fe),
+        GossipDecision.Accepted(update_gh),
+        GossipDecision.Accepted(update_hg),
+        GossipDecision.Accepted(node_b),
+        GossipDecision.Accepted(node_c),
+        GossipDecision.Accepted(node_d),
+        GossipDecision.Accepted(node_e),
+        GossipDecision.Accepted(node_f),
+        GossipDecision.Accepted(node_g),
+        GossipDecision.Accepted(node_h))
+      peerConnection.expectNoMsg()
       awaitCond({
-        sender.send(router, 'nodes)
+        sender.send(router, Symbol("nodes"))
         val nodes = sender.expectMsgType[Iterable[NodeAnnouncement]]
-        sender.send(router, 'channels)
+        sender.send(router, Symbol("channels"))
         val channels = sender.expectMsgType[Iterable[ChannelAnnouncement]]
-        sender.send(router, 'updates)
+        sender.send(router, Symbol("updates"))
         val updates = sender.expectMsgType[Iterable[ChannelUpdate]]
         nodes.size === 8 && channels.size === 5 && updates.size === 11
       }, max = 10 seconds, interval = 1 second)
```

### eclair-core/src/test/scala/fr/acinq/eclair/router/RouterSpec.scala
```diff
@@ -57,18 +57,18 @@ class RouterSpec extends BaseRouterSpec {
       val chan_ac = channelAnnouncement(ShortChannelId(420000, 5, 0), priv_a, priv_c, priv_funding_a, priv_funding_c)
       val update_ac = makeChannelUpdate(Block.RegtestGenesisBlock.hash, priv_a, c, chan_ac.shortChannelId, CltvExpiryDelta(7), 0 msat, 766000 msat, 10, htlcMaximum)
       val node_c = makeNodeAnnouncement(priv_c, "node-C", Color(123, 100, -40), Nil, hex"0200", timestamp = Platform.currentTime.milliseconds.toSeconds + 1)
-      router ! PeerRoutingMessage(peerConnection.ref, remoteNodeId, chan_ac)
+      peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, chan_ac))
       peerConnection.expectNoMsg(100 millis) // we don't immediately acknowledge the announcement (back pressure)
       watcher.expectMsg(ValidateRequest(chan_ac))
       watcher.send(router, ValidateResult(chan_ac, Right(Transaction(version = 0, txIn = Nil, txOut = TxOut(1000000 sat, write(pay2wsh(Scripts.multiSig2of2(funding_a, funding_c)))) :: Nil, lockTime = 0), UtxoStatus.Unspent)))
       peerConnection.expectMsg(TransportHandler.ReadAck(chan_ac))
       peerConnection.expectMsg(GossipDecision.Accepted(chan_ac))
       assert(peerConnection.sender() == router)
       watcher.expectMsgType[WatchSpentBasic]
-      router ! PeerRoutingMessage(peerConnection.ref, remoteNodeId, update_ac)
+      peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, update_ac))
       peerConnection.expectMsg(TransportHandler.ReadAck(update_ac))
       peerConnection.expectMsg(GossipDecision.Accepted(update_ac))
-      router ! PeerRoutingMessage(peerConnection.ref, remoteNodeId, node_c)
+      peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, node_c))
       peerConnection.expectMsg(TransportHandler.ReadAck(node_c))
       peerConnection.expectMsg(GossipDecision.Accepted(node_c))
       eventListener.expectMsg(ChannelsDiscovered(SingleChannelDiscovered(chan_ac, 1000000 sat, None, None) :: Nil))
@@ -87,12 +87,12 @@ class RouterSpec extends BaseRouterSpec {
       val chan_uc = channelAnnouncement(ShortChannelId(420000, 100, 0), priv_u, priv_c, priv_funding_u, priv_funding_c)
       val update_uc = makeChannelUpdate(Block.RegtestGenesisBlock.hash, priv_u, c, chan_uc.shortChannelId, CltvExpiryDelta(7), 0 msat, 766000 msat, 10, htlcMaximum)
       val node_u = makeNodeAnnouncement(priv_u, "node-U", Color(-120, -20, 60), Nil, hex"00")
-      router ! PeerRoutingMessage(peerConnection.ref, remoteNodeId, chan_uc)
+      peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, chan_uc))
       peerConnection.expectNoMsg(200 millis) // we don't immediately acknowledge the announcement (back pressure)
       watcher.expectMsg(ValidateRequest(chan_uc))
-      router ! PeerRoutingMessage(peerConnection.ref, remoteNodeId, update_uc)
+      peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, update_uc))
       peerConnection.expectMsg(TransportHandler.ReadAck(update_uc))
-      router ! PeerRoutingMessage(peerConnection.ref, remoteNodeId, node_u)
+      peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, node_u))
       peerConnection.expectMsg(TransportHandler.ReadAck(node_u))
       watcher.send(router, ValidateResult(chan_uc, Right(Transaction(version = 0, txIn = Nil, txOut = TxOut(2000000 sat, write(pay2wsh(Scripts.multiSig2of2(priv_funding_u.publicKey, funding_c)))) :: Nil, lockTime = 0), UtxoStatus.Unspent)))
       peerConnection.expectMsg(TransportHandler.ReadAck(chan_uc))
@@ -112,13 +112,13 @@ class RouterSpec extends BaseRouterSpec {
 
     {
       // duplicates
-      router ! PeerRoutingMessage(peerConnection.ref, remoteNodeId, node_a)
-      peerConnection.expectMsg(TransportHandler.ReadAck(node_a))
-      peerConnection.expectMsg(GossipDecision.Duplicate(node_a))
-      router ! PeerRoutingMessage(peerConnection.ref, remoteNodeId, chan_ab)
+      peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, node_b))
+      peerConnection.expectMsg(TransportHandler.ReadAck(node_b))
+      peerConnection.expectMsg(GossipDecision.Duplicate(node_b))
+      peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, chan_ab))
       peerConnection.expectMsg(TransportHandler.ReadAck(chan_ab))
       peerConnection.expectMsg(GossipDecision.Duplicate(chan_ab))
-      router ! PeerRoutingMessage(peerConnection.ref, remoteNodeId, update_ab)
+      peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, update_ab))
       peerConnection.expectMsg(TransportHandler.ReadAck(update_ab))
       peerConnection.expectMsg(GossipDecision.Duplicate(update_ab))
       peerConnection.expectNoMsg(100 millis)
@@ -128,16 +128,16 @@ class RouterSpec extends BaseRouterSpec {
 
     {
       // invalid signatures
-      val invalid_node_a = node_a.copy(timestamp = node_a.timestamp + 10)
-      val invalid_chan_a = channelAnnouncement(ShortChannelId(420000, 101, 1), priv_a, priv_c, priv_funding_a, priv_funding_c).copy(nodeId1 = randomKey.publicKey)
+      val invalid_node_b = node_b.copy(timestamp = node_b.timestamp + 10)
+      val invalid_chan_ac = channelAnnouncement(ShortChannelId(420000, 101, 1), priv_a, priv_c, priv_funding_a, priv_funding_c).copy(nodeId1 = randomKey.publicKey)
       val invalid_update_ab = update_ab.copy(cltvExpiryDelta = CltvExpiryDelta(21), timestamp = update_ab.timestamp + 1)
-      router ! PeerRoutingMessage(peerConnection.ref, remoteNodeId, invalid_node_a)
-      peerConnection.expectMsg(TransportHandler.ReadAck(invalid_node_a))
-      peerConnection.expectMsg(GossipDecision.InvalidSignature(invalid_node_a))
-      router ! PeerRoutingMessage(peerConnection.ref, remoteNodeId, invalid_chan_a)
-      peerConnection.expectMsg(TransportHandler.ReadAck(invalid_chan_a))
-      peerConnection.expectMsg(GossipDecision.InvalidSignature(invalid_chan_a))
-      router ! PeerRoutingMessage(peerConnection.ref, remoteNodeId, invalid_update_ab)
+      peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, invalid_node_b))
+      peerConnection.expectMsg(TransportHandler.ReadAck(invalid_node_b))
+      peerConnection.expectMsg(GossipDecision.InvalidSignature(invalid_node_b))
+      peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, invalid_chan_ac))
+      peerConnection.expectMsg(TransportHandler.ReadAck(invalid_chan_ac))
+      peerConnection.expectMsg(GossipDecision.InvalidSignature(invalid_chan_ac))
+      peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, invalid_update_ab))
       peerConnection.expectMsg(TransportHandler.ReadAck(invalid_update_ab))
       peerConnection.expectMsg(GossipDecision.InvalidSignature(invalid_update_ab))
       peerConnection.expectNoMsg(100 millis)
@@ -151,7 +151,7 @@ class RouterSpec extends BaseRouterSpec {
       val priv_funding_v = randomKey
       val chan_vc = channelAnnouncement(ShortChannelId(420000, 102, 0), priv_v, priv_c, priv_funding_v, priv_funding_c)
       nodeParams.db.network.addToPruned(chan_vc.shortChannelId :: Nil)
-      router ! PeerRoutingMessage(peerConnection.ref, remoteNodeId, chan_vc)
+      peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, chan_vc))
       peerConnection.expectMsg(TransportHandler.ReadAck(chan_vc))
       peerConnection.expectMsg(GossipDecision.ChannelPruned(chan_vc))
       peerConnection.expectNoMsg(100 millis)
@@ -175,10 +175,10 @@ class RouterSpec extends BaseRouterSpec {
       val priv_y = randomKey
       val update_ay = makeChannelUpdate(Block.RegtestGenesisBlock.hash, priv_a, priv_y.publicKey, ShortChannelId(4646464), CltvExpiryDelta(7), 0 msat, 766000 msat, 10, htlcMaximum)
       val node_y = makeNodeAnnouncement(priv_y, "node-Y", Color(123, 100, -40), Nil, hex"0200")
-      router ! PeerRoutingMessage(peerConnection.ref, remoteNodeId, update_ay)
+      peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, update_ay))
       peerConnection.expectMsg(TransportHandler.ReadAck(update_ay))
       peerConnection.expectMsg(GossipDecision.NoRelatedChannel(update_ay))
-      router ! PeerRoutingMessage(peerConnection.ref, remoteNodeId, node_y)
+      peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, node_y))
       peerConnection.expectMsg(TransportHandler.ReadAck(node_y))
       peerConnection.expectMsg(GossipDecision.NoKnownChannel(node_y))
       peerConnection.expectNoMsg(100 millis)
@@ -193,11 +193,11 @@ class RouterSpec extends BaseRouterSpec {
       val chan_ay = channelAnnouncement(ShortChannelId(42002), priv_a, priv_y, priv_funding_a, priv_funding_y)
       val update_ay = makeChannelUpdate(Block.RegtestGenesisBlock.hash, priv_a, priv_y.publicKey, chan_ay.shortChannelId, CltvExpiryDelta(7), 0 msat, 766000 msat, 10, htlcMaximum)
       val node_y = makeNodeAnnouncement(priv_y, "node-Y", Color(123, 100, -40), Nil, hex"0200")
-      router ! PeerRoutingMessage(peerConnection.ref, remoteNodeId, chan_ay)
+      peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, chan_ay))
       watcher.expectMsg(ValidateRequest(chan_ay))
-      router ! PeerRoutingMessage(peerConnection.ref, remoteNodeId, update_ay)
+      peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, update_ay))
       peerConnection.expectMsg(TransportHandler.ReadAck(update_ay))
-      router ! PeerRoutingMessage(peerConnection.ref, remoteNodeId, node_y)
+      peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, node_y))
       peerConnection.expectMsg(TransportHandler.ReadAck(node_y))
       watcher.send(router, ValidateResult(chan_ay, Right(Transaction(version = 0, txIn = Nil, txOut = TxOut(1000000 sat, write(pay2wsh(Scripts.multiSig2of2(funding_a, randomKey.publicKey)))) :: Nil, lockTime = 0), UtxoStatus.Unspent)))
       peerConnection.expectMsg(TransportHandler.ReadAck(chan_ay))
@@ -213,7 +213,7 @@ class RouterSpec extends BaseRouterSpec {
       // validation failure
       val priv_x = randomKey
       val chan_ax = channelAnnouncement(ShortChannelId(42001), priv_a, priv_x, priv_funding_a, randomKey)
-      router ! PeerRoutingMessage(peerConnection.ref, remoteNodeId, chan_ax)
+      peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, chan_ax))
       watcher.expectMsg(ValidateRequest(chan_ax))
       watcher.send(router, ValidateResult(chan_ax, Left(new RuntimeException("funding tx not found"))))
       peerConnection.expectMsg(TransportHandler.ReadAck(chan_ax))
@@ -228,7 +228,7 @@ class RouterSpec extends BaseRouterSpec {
       val priv_z = randomKey
       val priv_funding_z = randomKey
       val chan_az = channelAnnouncement(ShortChannelId(42003), priv_a, priv_z, priv_funding_a, priv_funding_z)
-      router ! PeerRoutingMessage(peerConnection.ref, remoteNodeId, chan_az)
+      peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, chan_az))
       watcher.expectMsg(ValidateRequest(chan_az))
       watcher.send(router, ValidateResult(chan_az, Right(Transaction(version = 0, txIn = Nil, txOut = TxOut(1000000 sat, write(pay2wsh(Scripts.multiSig2of2(funding_a, priv_funding_z.publicKey)))) :: Nil, lockTime = 0), UtxoStatus.Spent(spendingTxConfirmed = false))))
       peerConnection.expectMsg(TransportHandler.ReadAck(chan_az))
@@ -243,7 +243,7 @@ class RouterSpec extends BaseRouterSpec {
       val priv_z = randomKey
       val priv_funding_z = randomKey
       val chan_az = channelAnnouncement(ShortChannelId(42003), priv_a, priv_z, priv_funding_a, priv_funding_z)
-      router ! PeerRoutingMessage(peerConnection.ref, remoteNodeId, chan_az)
+      peerConnection.send(router, PeerRoutingMessage(peerConnection.ref, remoteNodeId, chan_az))
       watcher.expectMsg(ValidateRequest(chan_az))
       watcher.send(router, ValidateResult(chan_az, Right(Transaction(version = 0, txIn = Nil, txOut = TxOut(1000000 sat, write(pay2wsh(Scripts.multiSig2of2(funding_a, priv_funding_z.publicKey)))) :: Nil, lockTime = 0), UtxoStatus.Spent(spendingTxConfirmed = true))))
       peerConnection.expectMsg(TransportHandler.ReadAck(chan_az))
```
