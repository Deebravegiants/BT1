# [?] Fix potential race condition in node-relay (#1716)

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ACINQ/eclair
Published: 2021-03-08
Source: https://github.com/ACINQ/eclair/commit/ea8f94022e734aaca189ae1288fc00197907a19f
Type: security-commit

## Details
Fix potential race condition in node-relay (#1716)

We previously relied on `context.child` to check whether we already had a
relay handler for a given payment_hash.

Unfortunately this could return an actor that is currently stopping itself.
When that happens our relay command can end up in the dead letters and the
payment will not be relayed, nor be failed upstream.

We fix that by maintaining the list of current relay handlers in the
NodeRelayer and removing them from the list before stopping them.
This is similar to what's done in the MultiPartPaymentFSM.

## Patch
### eclair-core/src/main/scala/fr/acinq/eclair/payment/relay/NodeRelay.scala
```diff
@@ -16,8 +16,6 @@
 
 package fr.acinq.eclair.payment.relay
 
-import java.util.UUID
-
 import akka.actor.ActorRef
 import akka.actor.typed.Behavior
 import akka.actor.typed.eventstream.EventStream
@@ -41,6 +39,7 @@ import fr.acinq.eclair.router.{BalanceTooLow, RouteCalculation, RouteNotFound}
 import fr.acinq.eclair.wire._
 import fr.acinq.eclair.{CltvExpiry, Features, Logs, MilliSatoshi, NodeParams, nodeFee, randomBytes32}
 
+import java.util.UUID
 import scala.collection.immutable.Queue
 
 /**
@@ -52,6 +51,7 @@ object NodeRelay {
   // @formatter:off
   sealed trait Command
   case class Relay(nodeRelayPacket: IncomingPacket.NodeRelayPacket) extends Command
+  case object Stop extends Command
   private case class WrappedMultiPartExtraPaymentReceived(mppExtraReceived: MultiPartPaymentFSM.ExtraPaymentReceived[HtlcPart]) extends Command
   private case class WrappedMultiPartPaymentFailed(mppFailed: MultiPartPaymentFSM.MultiPartPaymentFailed) extends Command
   private case class WrappedMultiPartPaymentSucceeded(mppSucceeded: MultiPartPaymentFSM.MultiPartPaymentSucceeded) extends Command
@@ -60,13 +60,13 @@ object NodeRelay {
   private case class WrappedPaymentFailed(paymentFailed: PaymentFailed) extends Command
   // @formatter:on
 
-  def apply(nodeParams: NodeParams, router: ActorRef, register: ActorRef, relayId: UUID, paymentHash: ByteVector32, fsmFactory: FsmFactory = new FsmFactory): Behavior[Command] =
+  def apply(nodeParams: NodeParams, parent: akka.actor.typed.ActorRef[NodeRelayer.Command], router: ActorRef, register: ActorRef, relayId: UUID, paymentHash: ByteVector32, fsmFactory: FsmFactory = new FsmFactory): Behavior[Command] =
     Behaviors.setup { context =>
       Behaviors.withMdc(Logs.mdc(
         category_opt = Some(Logs.LogCategory.PAYMENT),
         parentPaymentId_opt = Some(relayId), // for a node relay, we use the same identifier for the whole relay itself, and the outgoing payment
         paymentHash_opt = Some(paymentHash))) {
-        new NodeRelay(nodeParams, router, register, relayId, paymentHash, context, fsmFactory)()
+        new NodeRelay(nodeParams, parent, router, register, relayId, paymentHash, context, fsmFactory)()
       }
     }
 
@@ -136,6 +136,7 @@ object NodeRelay {
  * see https://doc.akka.io/docs/akka/current/typed/style-guide.html#passing-around-too-many-parameters
  */
 class NodeRelay private(nodeParams: NodeParams,
+                        parent: akka.actor.typed.ActorRef[NodeRelayer.Command],
                         router: ActorRef,
                         register: ActorRef,
                         relayId: UUID,
@@ -164,7 +165,7 @@ class NodeRelay private(nodeParams: NodeParams,
           // TODO: @pm: maybe those checks should be done later in the flow (by the mpp FSM?)
           context.log.warn("rejecting htlcId={}: missing payment secret", add.id)
           rejectHtlc(add.id, add.channelId, add.amountMsat)
-          Behaviors.stopped
+          stopping()
         case Some(secret) =>
           import akka.actor.typed.scaladsl.adapter._
           context.log.info("relaying payment relayId={}", relayId)
@@ -205,15 +206,15 @@ class NodeRelay private(nodeParams: NodeParams,
         context.log.warn("could not complete incoming multi-part payment (parts={} paidAmount={} failure={})", parts.size, parts.map(_.amount).sum, failure)
         Metrics.recordPaymentRelayFailed(failure.getClass.getSimpleName, Tags.RelayType.Trampoline)
         parts.collect { case p: MultiPartPaymentFSM.HtlcPart => rejectHtlc(p.htlc.id, p.htlc.channelId, p.amount, Some(failure)) }
-        Behaviors.stopped
+        stopping()
       case WrappedMultiPartPaymentSucceeded(MultiPartPaymentFSM.MultiPartPaymentSucceeded(_, parts)) =>
         context.log.info("completed incoming multi-part payment with parts={} paidAmount={}", parts.size, parts.map(_.amount).sum)
         val upstream = Upstream.Trampoline(htlcs)
         validateRelay(nodeParams, upstream, nextPayload) match {
           case Some(failure) =>
             context.log.warn(s"rejecting trampoline payment reason=$failure")
             rejectPayment(upstream, Some(failure))
-            Behaviors.stopped
+            stopping()
           case None =>
             doSend(upstream, nextPayload, nextPacket)
         }
@@ -249,16 +250,27 @@ class NodeRelay private(nodeParams: NodeParams,
         case WrappedPaymentSent(paymentSent) =>
           context.log.debug("trampoline payment fully resolved downstream")
           success(upstream, fulfilledUpstream, paymentSent)
-          Behaviors.stopped
-        case WrappedPaymentFailed(PaymentFailed(id, _, failures, _)) =>
+          stopping()
+        case WrappedPaymentFailed(PaymentFailed(_, _, failures, _)) =>
           context.log.debug(s"trampoline payment failed downstream")
           if (!fulfilledUpstream) {
             rejectPayment(upstream, translateError(nodeParams, failures, upstream, nextPayload))
           }
-          Behaviors.stopped
+          stopping()
       }
     }
 
+  /**
+   * Once the downstream payment is settled (fulfilled or failed), we reject new upstream payments while we wait for our parent to stop us.
+   */
+  private def stopping(): Behavior[Command] = {
+    parent ! NodeRelayer.RelayComplete(context.self, paymentHash)
+    Behaviors.receiveMessagePartial {
+      rejectExtraHtlcPartialFunction orElse {
+        case Stop => Behaviors.stopped
+      }
+    }
+  }
 
   private def relay(upstream: Upstream.Trampoline, payloadOut: Onion.NodeRelayPayload, packetOut: OnionRoutingPacket): ActorRef = {
     val paymentCfg = SendPaymentConfig(relayId, relayId, None, paymentHash, payloadOut.amountToForward, payloadOut.outgoingNodeId, upstream, None, storeInDb = false, publishEvent = false, Nil)
@@ -297,11 +309,10 @@ class NodeRelay private(nodeParams: NodeParams,
     case Relay(nodeRelayPacket) =>
       rejectExtraHtlc(nodeRelayPacket.add)
       Behaviors.same
-    // NB: this messages would be sent from the payment FSM which we stopped before going to this state, but all
-    // this is asynchronous
+    // NB: this message would be sent from the payment FSM which we stopped before going to this state, but all this is asynchronous.
     // We always fail extraneous HTLCs. They are a spec violation from the sender, but harmless in the relay case.
     // By failing them fast (before the payment has reached the final recipient) there's a good chance the sender won't lose any money.
-    // We don't expect to relay pay-to-open payments
+    // We don't expect to relay pay-to-open payments.
     case WrappedMultiPartExtraPaymentReceived(extraPaymentReceived) =>
       rejectExtraHtlc(extraPaymentReceived.payment.htlc)
       Behaviors.same
```

### eclair-core/src/main/scala/fr/acinq/eclair/payment/relay/NodeRelayer.scala
```diff
@@ -16,14 +16,14 @@
 
 package fr.acinq.eclair.payment.relay
 
-import java.util.UUID
-
-import akka.actor.ActorRef
-import akka.actor.typed.Behavior
 import akka.actor.typed.scaladsl.Behaviors
+import akka.actor.typed.{ActorRef, Behavior}
+import fr.acinq.bitcoin.ByteVector32
 import fr.acinq.eclair.payment._
 import fr.acinq.eclair.{Logs, NodeParams}
 
+import java.util.UUID
+
 /**
  * Created by t-bast on 10/10/2019.
  */
@@ -38,33 +38,47 @@ object NodeRelayer {
   // @formatter:off
   sealed trait Command
   case class Relay(nodeRelayPacket: IncomingPacket.NodeRelayPacket) extends Command
+  case class RelayComplete(childHandler: ActorRef[NodeRelay.Command], paymentHash: ByteVector32) extends Command
+  private[relay] case class GetPendingPayments(replyTo: akka.actor.ActorRef) extends Command
   // @formatter:on
 
   def mdc: Command => Map[String, String] = {
-    case c: Relay => Logs.mdc(
-      paymentHash_opt = Some(c.nodeRelayPacket.add.paymentHash))
+    case c: Relay => Logs.mdc(paymentHash_opt = Some(c.nodeRelayPacket.add.paymentHash))
+    case c: RelayComplete => Logs.mdc(paymentHash_opt = Some(c.paymentHash))
+    case _: GetPendingPayments => Logs.mdc()
   }
 
-  def apply(nodeParams: NodeParams, router: ActorRef, register: ActorRef): Behavior[Command] =
+  /**
+   * @param children a map of current in-process payments, indexed by payment hash and purposefully *not* by payment id,
+   *                 because that is how we aggregate payment parts (when the incoming payment uses MPP).
+   */
+  def apply(nodeParams: NodeParams, router: akka.actor.ActorRef, register: akka.actor.ActorRef, children: Map[ByteVector32, ActorRef[NodeRelay.Command]] = Map.empty): Behavior[Command] =
     Behaviors.setup { context =>
       Behaviors.withMdc(Logs.mdc(category_opt = Some(Logs.LogCategory.PAYMENT)), mdc) {
-          Behaviors.receiveMessage {
-            case Relay(nodeRelayPacket) =>
-              import nodeRelayPacket.add.paymentHash
-              val handler = context.child(paymentHash.toString) match {
-                case Some(handler) =>
-                  // NB: we could also maintain a list of children
-                  handler.unsafeUpcast[NodeRelay.Command] // we know that all children are of type NodeRelay
-                case None =>
-                  val relayId = UUID.randomUUID()
-                  context.log.debug(s"spawning a new handler with relayId=$relayId")
-                  // we index children by paymentHash, not relayId, because there is no concept of individual payment on LN
-                  context.spawn(NodeRelay.apply(nodeParams, router, register, relayId, paymentHash), name = paymentHash.toString)
-              }
-              context.log.debug("forwarding incoming htlc to handler")
-              handler ! NodeRelay.Relay(nodeRelayPacket)
-              Behaviors.same
-          }
+        Behaviors.receiveMessage {
+          case Relay(nodeRelayPacket) =>
+            import nodeRelayPacket.add.paymentHash
+            children.get(paymentHash) match {
+              case Some(handler) =>
+                context.log.debug("forwarding incoming htlc to existing handler")
+                handler ! NodeRelay.Relay(nodeRelayPacket)
+                Behaviors.same
+              case None =>
+                val relayId = UUID.randomUUID()
+                context.log.debug(s"spawning a new handler with relayId=$relayId")
+                val handler = context.spawn(NodeRelay.apply(nodeParams, context.self, router, register, relayId, paymentHash), relayId.toString)
+                context.log.debug("forwarding incoming htlc to new handler")
+                handler ! NodeRelay.Relay(nodeRelayPacket)
+                apply(nodeParams, router, register, children + (paymentHash -> handler))
+            }
+          case RelayComplete(childHandler, paymentHash) =>
+            // we do a back-and-forth between parent and child before stopping the child to prevent a race condition
+            childHandler ! NodeRelay.Stop
+            apply(nodeParams, router, register, children - paymentHash)
+          case GetPendingPayments(replyTo) =>
+            replyTo ! children
+            Behaviors.same
+        }
       }
     }
 }
```

### eclair-core/src/test/scala/fr/acinq/eclair/payment/relay/NodeRelayerSpec.scala
```diff
@@ -23,7 +23,7 @@ import akka.actor.typed.eventstream.EventStream
 import akka.actor.typed.scaladsl.ActorContext
 import akka.actor.typed.scaladsl.adapter._
 import com.typesafe.config.ConfigFactory
-import fr.acinq.bitcoin.{Block, Crypto}
+import fr.acinq.bitcoin.{Block, ByteVector32, Crypto}
 import fr.acinq.eclair.Features.{BasicMultiPartPayment, PaymentSecret, VariableLengthOnion}
 import fr.acinq.eclair.channel.{CMD_FAIL_HTLC, CMD_FULFILL_HTLC, Register}
 import fr.acinq.eclair.crypto.Sphinx
@@ -53,10 +53,11 @@ class NodeRelayerSpec extends ScalaTestWithActorTestKit(ConfigFactory.load("appl
 
   import NodeRelayerSpec._
 
-  case class FixtureParam(nodeParams: NodeParams, nodeRelayer: ActorRef[NodeRelay.Command], router: TestProbe[Any], register: TestProbe[Any], mockPayFSM: TestProbe[Any], eventListener: TestProbe[PaymentEvent])
+  case class FixtureParam(nodeParams: NodeParams, nodeRelayer: ActorRef[NodeRelay.Command], parent: TestProbe[NodeRelayer.Command], router: TestProbe[Any], register: TestProbe[Any], mockPayFSM: TestProbe[Any], eventListener: TestProbe[PaymentEvent])
 
   override def withFixture(test: OneArgTest): Outcome = {
     val nodeParams = TestConstants.Bob.nodeParams.copy(multiPartPaymentExpiry = 5 seconds)
+    val parent = TestProbe[NodeRelayer.Command]("parent-relayer")
     val router = TestProbe[Any]("router")
     val register = TestProbe[Any]("register")
     val eventListener = TestProbe[PaymentEvent]("event-listener")
@@ -78,8 +79,53 @@ class NodeRelayerSpec extends ScalaTestWithActorTestKit(ConfigFactory.load("appl
         }
       }
     }
-    val nodeRelay = testKit.spawn(NodeRelay(nodeParams, router.ref.toClassic, register.ref.toClassic, relayId, paymentHash, fsmFactory))
-    withFixture(test.toNoArgTest(FixtureParam(nodeParams, nodeRelay, router, register, mockPayFSM, eventListener)))
+    val nodeRelay = testKit.spawn(NodeRelay(nodeParams, parent.ref, router.ref.toClassic, register.ref.toClassic, relayId, paymentHash, fsmFactory))
+    withFixture(test.toNoArgTest(FixtureParam(nodeParams, nodeRelay, parent, router, register, mockPayFSM, eventListener)))
+  }
+
+  test("stop child handler when relay is complete") { f =>
+    import f._
+    val probe = TestProbe[Any]
+
+    {
+      val parentRelayer = testKit.spawn(NodeRelayer(nodeParams, router.ref.toClassic, register.ref.toClassic))
+      parentRelayer ! NodeRelayer.GetPendingPayments(probe.ref.toClassic)
+      probe.expectMessage(Map.empty)
+    }
+    {
+      val (paymentHash1, child1) = (randomBytes32, TestProbe[NodeRelay.Command])
+      val (paymentHash2, child2) = (randomBytes32, TestProbe[NodeRelay.Command])
+      val children = Map(paymentHash1 -> child1.ref, paymentHash2 -> child2.ref)
+      val parentRelayer = testKit.spawn(NodeRelayer(nodeParams, router.ref.toClassic, register.ref.toClassic, children))
+      parentRelayer ! NodeRelayer.GetPendingPayments(probe.ref.toClassic)
+      probe.expectMessage(children)
+
+      parentRelayer ! NodeRelayer.RelayComplete(child1.ref, paymentHash1)
+      child1.expectMessage(NodeRelay.Stop)
+      parentRelayer ! NodeRelayer.RelayComplete(child1.ref, paymentHash1)
+      child1.expectMessage(NodeRelay.Stop)
+      parentRelayer ! NodeRelayer.GetPendingPayments(probe.ref.toClassic)
+      probe.expectMessage(children - paymentHash1)
+    }
+    {
+      val parentRelayer = testKit.spawn(NodeRelayer(nodeParams, router.ref.toClassic, register.ref.toClassic))
+      parentRelayer ! NodeRelayer.Relay(incomingMultiPart.head)
+      parentRelayer ! NodeRelayer.GetPendingPayments(probe.ref.toClassic)
+      val pending1 = probe.expectMessageType[Map[ByteVector32, ActorRef[NodeRelay.Command]]]
+      assert(pending1.size === 1)
+      assert(pending1.head._1 === paymentHash)
+
+      parentRelayer ! NodeRelayer.RelayComplete(pending1.head._2, paymentHash)
+      parentRelayer ! NodeRelayer.GetPendingPayments(probe.ref.toClassic)
+      probe.expectMessage(Map.empty)
+
+      parentRelayer ! NodeRelayer.Relay(incomingMultiPart.head)
+      parentRelayer ! NodeRelayer.GetPendingPayments(probe.ref.toClassic)
+      val pending2 = probe.expectMessageType[Map[ByteVector32, ActorRef[NodeRelay.Command]]]
+      assert(pending2.size === 1)
+      assert(pending2.head._1 === paymentHash)
+      assert(pending2.head._2 !== pending1.head._2)
+    }
   }
 
   test("fail to relay when incoming multi-part payment times out") { f =>
@@ -95,6 +141,7 @@ class NodeRelayerSpec extends ScalaTestWithActorTestKit(ConfigFactory.load("appl
       assert(fwd.message === CMD_FAIL_HTLC(p.add.id, failure, commit = true))
     }
 
+    parent.expectMessageType[NodeRelayer.RelayComplete]
     register.expectNoMessage(100 millis)
   }
 
@@ -398,6 +445,7 @@ class NodeRelayerSpec extends ScalaTestWithActorTestKit(ConfigFactory.load("appl
     validateRelayEvent(relayEvent)
     assert(relayEvent.incoming.toSet === incomingMultiPart.map(i => PaymentRelayed.Part(i.add.amountMsat, i.add.channelId)).toSet)
     assert(relayEvent.outgoing.nonEmpty)
+    parent.expectMessageType[NodeRelayer.RelayComplete]
     register.expectNoMessage(100 millis)
   }
 
@@ -425,6 +473,7 @@ class NodeRelayerSpec extends ScalaTestWithActorTestKit(ConfigFactory.load("appl
     validateRelayEvent(relayEvent)
     assert(relayEvent.incoming === Seq(PaymentRelayed.Part(incomingSinglePart.add.amountMsat, incomingSinglePart.add.channelId)))
     assert(relayEvent.outgoing.nonEmpty)
+    parent.expectMessageType[NodeRelayer.RelayComplete]
     register.expectNoMessage(100 millis)
   }
 
@@ -464,6 +513,7 @@ class NodeRelayerSpec extends ScalaTestWithActorTestKit(ConfigFactory.load("appl
     validateRelayEvent(relayEvent)
     assert(relayEvent.incoming === incomingMultiPart.map(i => PaymentRelayed.Part(i.add.amountMsat, i.add.channelId)))
     assert(relayEvent.outgoing.nonEmpty)
+    parent.expectMessageType[NodeRelayer.RelayComplete]
     register.expectNoMessage(100 millis)
   }
 
@@ -500,6 +550,7 @@ class NodeRelayerSpec extends ScalaTestWithActorTestKit(ConfigFactory.load("appl
     validateRelayEvent(relayEvent)
     assert(relayEvent.incoming === incomingMultiPart.map(i => PaymentRelayed.Part(i.add.amountMsat, i.add.channelId)))
     assert(relayEvent.outgoing.length === 1)
+    parent.expectMessageType[NodeRelayer.RelayComplete]
     register.expectNoMessage(100 millis)
   }
 
```
