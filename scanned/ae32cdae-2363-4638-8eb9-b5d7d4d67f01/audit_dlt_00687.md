# [?] Fix race condition in `Postman` causing flaky `OfferPayment` tests (#3270)

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ACINQ/eclair
Published: 2026-03-19
Source: https://github.com/ACINQ/eclair/commit/8c5f39f434bf6de32227d7ac92918ec7dd979608
Type: security-commit

## Details
Fix race condition in `Postman` causing flaky `OfferPayment` tests (#3270)

The integration test "send blinded multi-part payment a->b->c (single
channel a->b)" in `OfferPaymentSpec` fails intermittently. The root
cause is a race condition in `Postman` where the subscription for an
onion message reply is registered after the message is sent, allowing
the reply to arrive and be silently dropped before the subscription
exists.

In integration tests where all 3 nodes run on the same JVM, the onion
message round-trip (Alice -> Bob -> Carol -> creates invoice -> Carol
-> Bob -> Alice) can complete in just a few milliseconds - fast enough
to beat the `Subscribe` message to the `Postman`'s mailbox.

This explains why the test is flaky: it usually works (round-trip slower
than subscribe), but occasionally fails (round-trip faster than
subscribe, reply dropped).

We simply move the subscription registration to *before* the message is
sent to the network.

## Patch
### eclair-core/src/main/scala/fr/acinq/eclair/message/Postman.scala
```diff
@@ -218,6 +218,9 @@ private class SendingMessage(nodeParams: NodeParams,
         replyTo ! Postman.MessageFailed(failure.toString)
         Behaviors.stopped
       case Right(message) =>
+        if (expectsReply) {
+          postman ! Postman.Subscribe(messageId, replyTo)
+        }
         val nextNodeId = EncodedNodeId.WithPublicKey.Plain(intermediateNodes.headOption.getOrElse(plainNodeId))
         val relay = context.spawn(Behaviors.supervise(MessageRelay(nodeParams, switchboard, register, router)).onFailure(typed.SupervisorStrategy.stop), s"relay-message-$messageId")
         relay ! MessageRelay.RelayMessage(messageId, nodeParams.nodeId, Right(nextNodeId), message, MessageRelay.RelayAll, Some(context.messageAdapter[MessageRelay.Status](SendingStatus)))
@@ -228,9 +231,7 @@ private class SendingMessage(nodeParams: NodeParams,
   private def waitForSent(): Behavior[Command] = {
     Behaviors.receiveMessagePartial {
       case SendingStatus(MessageRelay.Sent(messageId)) =>
-        if (expectsReply) {
-          postman ! Postman.Subscribe(messageId, replyTo)
-        } else {
+        if (!expectsReply) {
           replyTo ! Postman.MessageSent
         }
         Behaviors.stopped
```
