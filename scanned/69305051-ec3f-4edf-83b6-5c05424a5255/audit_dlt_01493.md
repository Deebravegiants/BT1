# [?] Fix race condition on early connection failure (#1430)

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ACINQ/eclair
Published: 2020-05-19
Source: https://github.com/ACINQ/eclair/commit/c01031708dfce49dbde79f42c01f18a2a5dd324a
Type: security-commit

## Details
Fix race condition on early connection failure (#1430)

Both `Client` and `TransportHandler` were watching the connection actor,
which resulted in undeterministic behavior during termination of
`PeerConnection`.

We now always return a message when a connection fails during
authentication.

Took the opportunity to add more typing (insert
deathtoallthestring.jpg).

## Patch
### eclair-core/src/main/scala/fr/acinq/eclair/Eclair.scala
```diff
@@ -29,7 +29,7 @@ import fr.acinq.eclair.channel.Register.{Forward, ForwardShortId}
 import fr.acinq.eclair.channel._
 import fr.acinq.eclair.db.{IncomingPayment, NetworkFee, OutgoingPayment, Stats}
 import fr.acinq.eclair.io.Peer.{GetPeerInfo, PeerInfo}
-import fr.acinq.eclair.io.{NodeURI, Peer}
+import fr.acinq.eclair.io.{NodeURI, Peer, PeerConnection}
 import fr.acinq.eclair.payment._
 import fr.acinq.eclair.payment.receive.MultiPartHandler.ReceivePayment
 import fr.acinq.eclair.payment.relay.Relayer.{GetOutgoingChannels, OutgoingChannels, UsableBalance}
@@ -128,8 +128,8 @@ class EclairImpl(appKit: Kit) extends Eclair {
   private val externalIdMaxLength = 66
 
   override def connect(target: Either[NodeURI, PublicKey])(implicit timeout: Timeout): Future[String] = target match {
-    case Left(uri) => (appKit.switchboard ? Peer.Connect(uri)).mapTo[String]
-    case Right(pubKey) => (appKit.switchboard ? Peer.Connect(pubKey, None)).mapTo[String]
+    case Left(uri) => (appKit.switchboard ? Peer.Connect(uri)).mapTo[PeerConnection.ConnectionResult].map(_.toString)
+    case Right(pubKey) => (appKit.switchboard ? Peer.Connect(pubKey, None)).mapTo[PeerConnection.ConnectionResult].map(_.toString)
   }
 
   override def disconnect(nodeId: PublicKey)(implicit timeout: Timeout): Future[String] = {
```

### eclair-core/src/main/scala/fr/acinq/eclair/crypto/TransportHandler.scala
```diff
@@ -268,7 +268,10 @@ class TransportHandler[T: ClassTag](keyPair: KeyPair, rs: Option[ByteVector], co
     }
   }
 
-  override def aroundPostStop(): Unit = connection ! Tcp.Close // attempts to gracefully close the connection when dying
+  onTermination {
+    case _: StopEvent =>
+      connection ! Tcp.Close // attempts to gracefully close the connection when dying
+  }
 
   initialize()
 
```

### eclair-core/src/main/scala/fr/acinq/eclair/io/Client.scala
```diff
@@ -24,7 +24,6 @@ import akka.io.Tcp.SO.KeepAlive
 import akka.io.{IO, Tcp}
 import fr.acinq.bitcoin.Crypto.PublicKey
 import fr.acinq.eclair.Logs.LogCategory
-import fr.acinq.eclair.io.Client.ConnectionFailed
 import fr.acinq.eclair.tor.Socks5Connection.{Socks5Connect, Socks5Connected, Socks5Error}
 import fr.acinq.eclair.tor.{Socks5Connection, Socks5ProxyParams}
 import fr.acinq.eclair.{Logs, NodeParams}
@@ -60,7 +59,7 @@ class Client(nodeParams: NodeParams, switchboard: ActorRef, router: ActorRef, re
     case Tcp.CommandFailed(c: Tcp.Connect) =>
       val peerOrProxyAddress = c.remoteAddress
       log.info(s"connection failed to ${str(peerOrProxyAddress)}")
-      origin_opt.foreach(_ ! Status.Failure(ConnectionFailed(remoteAddress)))
+      origin_opt.foreach(_ ! PeerConnection.ConnectionResult.ConnectionFailed(remoteAddress))
       context stop self
 
     case Tcp.Connected(peerOrProxyAddress, _) =>
@@ -75,32 +74,36 @@ class Client(nodeParams: NodeParams, switchboard: ActorRef, router: ActorRef, re
           context become {
             case Tcp.CommandFailed(_: Socks5Connect) =>
               log.info(s"connection failed to ${str(remoteAddress)} via SOCKS5 ${str(proxyAddress)}")
-              origin_opt.foreach(_ ! Status.Failure(ConnectionFailed(remoteAddress)))
+              origin_opt.foreach(_ ! PeerConnection.ConnectionResult.ConnectionFailed(remoteAddress))
               context stop self
             case Socks5Connected(_) =>
               log.info(s"connected to ${str(remoteAddress)} via SOCKS5 proxy ${str(proxyAddress)}")
-              auth(proxy)
-              context become connected(proxy)
+              context unwatch proxy
+              val peerConnection = auth(proxy)
+              context watch peerConnection
+              context become connected(peerConnection)
+            case Terminated(actor) if actor == proxy =>
+              context stop self
           }
         case None =>
           val peerAddress = peerOrProxyAddress
           log.info(s"connected to ${str(peerAddress)}")
-          auth(connection)
-          context watch connection
-          context become connected(connection)
+          val peerConnection = auth(connection)
+          context watch peerConnection
+          context become connected(peerConnection)
       }
   }
 
-  def connected(connection: ActorRef): Receive = {
-    case Terminated(actor) if actor == connection =>
+  def connected(peerConnection: ActorRef): Receive = {
+    case Terminated(actor) if actor == peerConnection =>
       context stop self
   }
 
   override def unhandled(message: Any): Unit = {
     log.warning(s"unhandled message=$message")
   }
 
-  // we should not restart a failing socks client
+  // we should not restart a failing socks client or transport handler
   override val supervisorStrategy = OneForOneStrategy(loggingEnabled = false) {
     case t =>
       Logs.withMdc(log)(Logs.mdc(remoteNodeId_opt = Some(remoteNodeId))) {
@@ -116,20 +119,19 @@ class Client(nodeParams: NodeParams, switchboard: ActorRef, router: ActorRef, re
 
   private def str(address: InetSocketAddress): String = s"${address.getHostString}:${address.getPort}"
 
-  def auth(connection: ActorRef) = {
+  def auth(connection: ActorRef): ActorRef = {
     val peerConnection = context.actorOf(PeerConnection.props(
       nodeParams = nodeParams,
       switchboard = switchboard,
       router = router
     ))
     peerConnection ! PeerConnection.PendingAuth(connection, remoteNodeId_opt = Some(remoteNodeId), address = remoteAddress, origin_opt = origin_opt)
+    peerConnection
   }
 }
 
 object Client {
 
   def props(nodeParams: NodeParams, switchboard: ActorRef, router: ActorRef, address: InetSocketAddress, remoteNodeId: PublicKey, origin_opt: Option[ActorRef]): Props = Props(new Client(nodeParams, switchboard, router, address, remoteNodeId, origin_opt))
 
-  case class ConnectionFailed(address: InetSocketAddress) extends RuntimeException(s"connection failed to $address")
-
 }
```

### eclair-core/src/main/scala/fr/acinq/eclair/io/Peer.scala
```diff
@@ -86,7 +86,7 @@ class Peer(val nodeParams: NodeParams, remoteNodeId: PublicKey, watcher: ActorRe
   when(CONNECTED) {
     dropStaleMessages {
       case Event(_: Peer.Connect, _) =>
-        sender ! "already connected"
+        sender ! PeerConnection.ConnectionResult.AlreadyConnected
         stay
 
       case Event(Channel.OutgoingMessage(msg, peerConnection), d: ConnectedData) if peerConnection == d.peerConnection => // this is an outgoing message, but we need to make sure that this is for the current active connection
```

### eclair-core/src/main/scala/fr/acinq/eclair/io/PeerConnection.scala
```diff
@@ -89,8 +89,9 @@ class PeerConnection(nodeParams: NodeParams, switchboard: ActorRef, router: Acto
       switchboard ! Authenticated(self, remoteNodeId)
       goto(BEFORE_INIT) using BeforeInitData(remoteNodeId, d.pendingAuth, d.transport)
 
-    case Event(AuthTimeout, _) =>
+    case Event(AuthTimeout, d: AuthenticatingData) =>
       log.warning(s"authentication timed out after ${nodeParams.authTimeout}")
+      d.pendingAuth.origin_opt.foreach(_ ! ConnectionResult.AuthenticationFailed("authentication timed out"))
       stop(FSM.Normal)
   }
 
@@ -133,19 +134,19 @@ class PeerConnection(nodeParams: NodeParams, switchboard: ActorRef, router: Acto
 
         if (remoteInit.networks.nonEmpty && !remoteInit.networks.contains(d.nodeParams.chainHash)) {
           log.warning(s"incompatible networks (${remoteInit.networks}), disconnecting")
-          d.pendingAuth.origin_opt.foreach(origin => origin ! Status.Failure(new RuntimeException("incompatible networks")))
+          d.pendingAuth.origin_opt.foreach(_ ! ConnectionResult.InitializationFailed("incompatible networks"))
           d.transport ! PoisonPill
           stay
         } else if (!Features.areSupported(remoteInit.features)) {
           log.warning("incompatible features, disconnecting")
-          d.pendingAuth.origin_opt.foreach(origin => origin ! Status.Failure(new RuntimeException("incompatible features")))
+          d.pendingAuth.origin_opt.foreach(_ ! ConnectionResult.InitializationFailed("incompatible features"))
           d.transport ! PoisonPill
           stay
         } else {
           Metrics.PeerConnectionsConnecting.withTag(Tags.ConnectionState, Tags.ConnectionStates.Initialized).increment()
           d.peer ! ConnectionReady(self, d.remoteNodeId, d.pendingAuth.address, d.pendingAuth.outgoing, d.localInit, remoteInit)
 
-          d.pendingAuth.origin_opt.foreach(origin => origin ! "connected")
+          d.pendingAuth.origin_opt.foreach(_ ! ConnectionResult.Connected)
 
           def localHasFeature(f: Feature): Boolean = Features.hasFeature(d.localInit.features, f)
 
@@ -177,8 +178,9 @@ class PeerConnection(nodeParams: NodeParams, switchboard: ActorRef, router: Acto
           goto(CONNECTED) using ConnectedData(d.nodeParams, d.remoteNodeId, d.transport, d.peer, d.localInit, remoteInit, rebroadcastDelay)
         }
 
-      case Event(InitTimeout, _) =>
+      case Event(InitTimeout, d: InitializingData) =>
         log.warning(s"initialization timed out after ${nodeParams.initTimeout}")
+        d.pendingAuth.origin_opt.foreach(_ ! ConnectionResult.InitializationFailed("initialization timed out"))
         stop(FSM.Normal)
     }
   }
@@ -382,6 +384,12 @@ class PeerConnection(nodeParams: NodeParams, switchboard: ActorRef, router: Acto
       Logs.withMdc(diagLog)(Logs.mdc(category_opt = Some(Logs.LogCategory.CONNECTION))) {
         log.info("transport died, stopping")
       }
+      d match {
+        case a: AuthenticatingData => a.pendingAuth.origin_opt.foreach(_ ! ConnectionResult.AuthenticationFailed("connection aborted while authenticating"))
+        case a: BeforeInitData => a.pendingAuth.origin_opt.foreach(_ ! ConnectionResult.InitializationFailed("connection aborted while initializing"))
+        case a: InitializingData => a.pendingAuth.origin_opt.foreach(_ ! ConnectionResult.InitializationFailed("connection aborted while initializing"))
+        case _ => ()
+      }
       stop(FSM.Normal)
 
     case Event(_: GossipDecision.Accepted, _) => stay // for now we don't do anything with those events
@@ -500,6 +508,19 @@ object PeerConnection {
   case class InitializeConnection(peer: ActorRef)
   case class ConnectionReady(peerConnection: ActorRef, remoteNodeId: PublicKey, address: InetSocketAddress, outgoing: Boolean, localInit: wire.Init, remoteInit: wire.Init)
 
+  sealed trait ConnectionResult
+  object ConnectionResult {
+    sealed trait Success extends ConnectionResult
+    sealed trait Failure extends ConnectionResult
+
+    case object NoAddressFound extends ConnectionResult.Failure { override def toString: String = "no address found" }
+    case class ConnectionFailed(address: InetSocketAddress) extends ConnectionResult.Failure { override def toString: String = s"connection failed to $address" }
+    case class AuthenticationFailed(reason: String) extends ConnectionResult.Failure { override def toString: String = reason }
+    case class InitializationFailed(reason: String) extends ConnectionResult.Failure { override def toString: String = reason }
+    case object AlreadyConnected extends ConnectionResult.Failure { override def toString: String = "already connected" }
+    case object Connected extends ConnectionResult.Success { override def toString: String = "connected" }
+  }
+
   case class DelayedRebroadcast(rebroadcast: Rebroadcast)
 
   case class Behavior(fundingTxAlreadySpentCount: Int = 0, ignoreNetworkAnnouncement: Boolean = false)
```

### eclair-core/src/main/scala/fr/acinq/eclair/io/ReconnectionTask.scala
```diff
@@ -50,7 +50,7 @@ class ReconnectionTask(nodeParams: NodeParams, remoteNodeId: PublicKey) extends
   startWith(IDLE, IdleData(Nothing))
 
   when(CONNECTING) {
-    case Event(Status.Failure(_: Client.ConnectionFailed), d: ConnectingData) =>
+    case Event(_: PeerConnection.ConnectionResult.ConnectionFailed, d: ConnectingData) =>
       log.info(s"connection failed, next reconnection in ${d.nextReconnectionDelay.toSeconds} seconds")
       setReconnectTimer(d.nextReconnectionDelay)
       goto(WAITING) using WaitingData(nextReconnectionDelay(d.nextReconnectionDelay, nodeParams.maxReconnectInterval))
@@ -121,9 +121,7 @@ class ReconnectionTask(nodeParams: NodeParams, remoteNodeId: PublicKey) extends
   }
 
   whenUnhandled {
-    case Event("connected", _) => stay
-
-    case Event(Status.Failure(_: Client.ConnectionFailed), _) => stay
+    case Event(_: PeerConnection.ConnectionResult, _) => stay
 
     case Event(TickReconnect, _) => stay
 
@@ -135,7 +133,7 @@ class ReconnectionTask(nodeParams: NodeParams, remoteNodeId: PublicKey) extends
         .map(hostAndPort2InetSocketAddress)
         .orElse(getPeerAddressFromDb(nodeParams.db.peers, nodeParams.db.network, remoteNodeId)) match {
         case Some(address) => connect(address, origin = sender)
-        case None => sender ! "no address found"
+        case None => sender ! PeerConnection.ConnectionResult.NoAddressFound
       }
       stay
   }
```

### eclair-core/src/test/scala/fr/acinq/eclair/integration/IntegrationSpec.scala
```diff
@@ -36,7 +36,7 @@ import fr.acinq.eclair.channel._
 import fr.acinq.eclair.crypto.Sphinx.DecryptedFailurePacket
 import fr.acinq.eclair.crypto.TransportHandler
 import fr.acinq.eclair.db._
-import fr.acinq.eclair.io.Peer
+import fr.acinq.eclair.io.{Peer, PeerConnection}
 import fr.acinq.eclair.io.Peer.{Disconnect, PeerRoutingMessage}
 import fr.acinq.eclair.payment.PaymentRequest.ExtraHop
 import fr.acinq.eclair.payment._
@@ -172,7 +172,7 @@ class IntegrationSpec extends TestKitBaseClass with BitcoindService with AnyFunS
       nodeId = node2.nodeParams.nodeId,
       address_opt = Some(HostAndPort.fromParts(address.socketAddress.getHostString, address.socketAddress.getPort))
     ))
-    sender.expectMsgAnyOf(10 seconds, "connected", "already connected")
+    sender.expectMsgAnyOf(10 seconds, PeerConnection.ConnectionResult.Connected, PeerConnection.ConnectionResult.AlreadyConnected)
     sender.send(node1.switchboard, Peer.OpenChannel(
       remoteNodeId = node2.nodeParams.nodeId,
       fundingSatoshis = fundingSatoshis,
@@ -318,7 +318,7 @@ class IntegrationSpec extends TestKitBaseClass with BitcoindService with AnyFunS
         nodeId = funder.nodeParams.nodeId,
         address_opt = Some(HostAndPort.fromParts(funder.nodeParams.publicAddresses.head.socketAddress.getHostString, funder.nodeParams.publicAddresses.head.socketAddress.getPort))
       ))
-      sender.expectMsgAnyOf(10 seconds, "connected", "already connected", "reconnection in progress")
+      sender.expectMsgAnyOf(10 seconds, PeerConnection.ConnectionResult.Connected, PeerConnection.ConnectionResult.AlreadyConnected)
 
       sender.send(fundee.register, Forward(channelId, CMD_GETSTATE))
       val fundeeState = sender.expectMsgType[State](max = 30 seconds)
```

### eclair-core/src/test/scala/fr/acinq/eclair/io/PeerConnectionSpec.scala
```diff
@@ -107,47 +107,55 @@ class PeerConnectionSpec extends TestKitBaseClass with FixtureAnyFunSuiteLike wi
   test("disconnect if authentication timeout") { f =>
     import f._
     val probe = TestProbe()
+    val origin = TestProbe()
     probe.watch(peerConnection)
-    probe.send(peerConnection, PeerConnection.PendingAuth(connection.ref, Some(remoteNodeId), address, origin_opt = None, transport_opt = Some(transport.ref)))
+    probe.send(peerConnection, PeerConnection.PendingAuth(connection.ref, Some(remoteNodeId), address, origin_opt = Some(origin.ref), transport_opt = Some(transport.ref)))
     probe.expectTerminated(peerConnection, nodeParams.authTimeout / transport.testKitSettings.TestTimeFactor  + 1.second) // we don't want dilated time here
+    origin.expectMsg(PeerConnection.ConnectionResult.AuthenticationFailed("authentication timed out"))
   }
 
   test("disconnect if init timeout") { f =>
     import f._
     val probe = TestProbe()
+    val origin = TestProbe()
     probe.watch(peerConnection)
-    probe.send(peerConnection, PeerConnection.PendingAuth(connection.ref, Some(remoteNodeId), address, origin_opt = None, transport_opt = Some(transport.ref)))
+    probe.send(peerConnection, PeerConnection.PendingAuth(connection.ref, Some(remoteNodeId), address, origin_opt = Some(origin.ref), transport_opt = Some(transport.ref)))
     transport.send(peerConnection, TransportHandler.HandshakeCompleted(remoteNodeId))
     probe.send(peerConnection, PeerConnection.InitializeConnection(peer.ref))
     probe.expectTerminated(peerConnection, nodeParams.initTimeout / transport.testKitSettings.TestTimeFactor  + 1.second) // we don't want dilated time here
+    origin.expectMsg(PeerConnection.ConnectionResult.InitializationFailed("initialization timed out"))
   }
 
   test("disconnect if incompatible local features") { f =>
     import f._
     val probe = TestProbe()
+    val origin = TestProbe()
     probe.watch(transport.ref)
-    probe.send(peerConnection, PeerConnection.PendingAuth(connection.ref, Some(remoteNodeId), address, origin_opt = None, transport_opt = Some(transport.ref)))
+    probe.send(peerConnection, PeerConnection.PendingAuth(connection.ref, Some(remoteNodeId), address, origin_opt = Some(origin.ref), transport_opt = Some(transport.ref)))
     transport.send(peerConnection, TransportHandler.HandshakeCompleted(remoteNodeId))
     probe.send(peerConnection, PeerConnection.InitializeConnection(peer.ref))
     transport.expectMsgType[TransportHandler.Listener]
     transport.expectMsgType[wire.Init]
     transport.send(peerConnection, LightningMessageCodecs.initCodec.decode(hex"0000 00050100000000".bits).require.value)
     transport.expectMsgType[TransportHandler.ReadAck]
     probe.expectTerminated(transport.ref)
+    origin.expectMsg(PeerConnection.ConnectionResult.InitializationFailed("incompatible features"))
   }
 
   test("disconnect if incompatible global features") { f =>
     import f._
     val probe = TestProbe()
+    val origin = TestProbe()
     probe.watch(transport.ref)
-    probe.send(peerConnection, PeerConnection.PendingAuth(connection.ref, Some(remoteNodeId), address, origin_opt = None, transport_opt = Some(transport.ref)))
+    probe.send(peerConnection, PeerConnection.PendingAuth(connection.ref, Some(remoteNodeId), address, origin_opt = Some(origin.ref), transport_opt = Some(transport.ref)))
     transport.send(peerConnection, TransportHandler.HandshakeCompleted(remoteNodeId))
     probe.send(peerConnection, PeerConnection.InitializeConnection(peer.ref))
     transport.expectMsgType[TransportHandler.Listener]
     transport.expectMsgType[wire.Init]
     transport.send(peerConnection, LightningMessageCodecs.initCodec.decode(hex"00050100000000 0000".bits).require.value)
     transport.expectMsgType[TransportHandler.ReadAck]
     probe.expectTerminated(transport.ref)
+    origin.expectMsg(PeerConnection.ConnectionResult.InitializationFailed("incompatible features"))
   }
 
   test("masks off MPP and PaymentSecret features") { f =>
@@ -178,15 +186,17 @@ class PeerConnectionSpec extends TestKitBaseClass with FixtureAnyFunSuiteLike wi
   test("disconnect if incompatible networks") { f =>
     import f._
     val probe = TestProbe()
+    val origin = TestProbe()
     probe.watch(transport.ref)
-    probe.send(peerConnection, PeerConnection.PendingAuth(connection.ref, Some(remoteNodeId), address, origin_opt = None, transport_opt = Some(transport.ref)))
+    probe.send(peerConnection, PeerConnection.PendingAuth(connection.ref, Some(remoteNodeId), address, origin_opt = Some(origin.ref), transport_opt = Some(transport.ref)))
     transport.send(peerConnection, TransportHandler.HandshakeCompleted(remoteNodeId))
     probe.send(peerConnection, PeerConnection.InitializeConnection(peer.ref))
     transport.expectMsgType[TransportHandler.Listener]
     transport.expectMsgType[wire.Init]
     transport.send(peerConnection, wire.Init(Bob.nodeParams.features, TlvStream(InitTlv.Networks(Block.LivenetGenesisBlock.hash :: Block.SegnetGenesisBlock.hash :: Nil))))
     transport.expectMsgType[TransportHandler.ReadAck]
     probe.expectTerminated(transport.ref)
+    origin.expectMsg(PeerConnection.ConnectionResult.InitializationFailed("incompatible networks"))
   }
 
   test("sync if no whitelist is defined") { f =>
```

### eclair-core/src/test/scala/fr/acinq/eclair/io/PeerSpec.scala
```diff
@@ -92,7 +92,7 @@ class PeerSpec extends TestKitBaseClass with FixtureAnyFunSuiteLike with StateTe
     val probe = TestProbe()
     probe.send(peer, Peer.Init(Set.empty))
     probe.send(peer, Peer.Connect(remoteNodeId, address_opt = None))
-    probe.expectMsg(s"no address found")
+    probe.expectMsg(PeerConnection.ConnectionResult.NoAddressFound)
   }
 
   test("successfully connect to peer at user request") { f =>
@@ -156,7 +156,7 @@ class PeerSpec extends TestKitBaseClass with FixtureAnyFunSuiteLike with StateTe
     connect(remoteNodeId, peer, peerConnection, channels = Set(ChannelCodecsSpec.normal))
 
     probe.send(peer, Peer.Connect(remoteNodeId, None))
-    probe.expectMsg("already connected")
+    probe.expectMsg(PeerConnection.ConnectionResult.AlreadyConnected)
   }
 
   test("handle disconnect in state CONNECTED") { f =>
```
