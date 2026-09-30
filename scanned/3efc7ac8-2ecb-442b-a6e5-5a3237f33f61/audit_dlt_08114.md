# [?] fixed race condition when registering tcp client listener

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ACINQ/eclair
Published: 2017-04-28
Source: https://github.com/ACINQ/eclair/commit/aafa3f63a60c1740d762f0a774c52957bc3c1b3f
Type: security-commit

## Details
fixed race condition when registering tcp client listener

## Patch
### eclair-node/src/main/scala/fr/acinq/eclair/crypto/TransportHandler.scala
```diff
@@ -30,6 +30,8 @@ class TransportHandler[T: ClassTag](keyPair: KeyPair, rs: Option[BinaryData], co
 
   import TransportHandler._
 
+  connection ! akka.io.Tcp.Register(self)
+
   // it means we initiate the dialog
   val isWriter = rs.isDefined
 
```

### eclair-node/src/main/scala/fr/acinq/eclair/io/Client.scala
```diff
@@ -36,7 +36,6 @@ class Client(nodeParams: NodeParams, switchboard: ActorRef, address: InetSocketA
           Some(remoteNodeId),
           connection = connection,
           serializer = LightningMessageSerializer)))
-      connection ! akka.io.Tcp.Register(transport)
       context watch transport
       context become authenticating(transport)
   }
```

### eclair-node/src/main/scala/fr/acinq/eclair/io/Server.scala
```diff
@@ -35,13 +35,12 @@ class Server(nodeParams: NodeParams, switchboard: ActorRef, address: InetSocketA
     case Connected(remote, _) =>
       log.info(s"connected to $remote")
       val connection = sender
-      val transport = context.actorOf(Props(
+      context.actorOf(Props(
         new TransportHandler[LightningMessage](
           KeyPair(nodeParams.privateKey.publicKey.toBin, nodeParams.privateKey.toBin),
           None,
           connection = connection,
           serializer = LightningMessageSerializer)))
-      connection ! akka.io.Tcp.Register(transport)
 
     case h: HandshakeCompleted =>
       log.info(s"handshake completed with ${h.remoteNodeId}")
```
