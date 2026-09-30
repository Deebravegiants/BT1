# [?] fix race condition in ChannelSpec test

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ACINQ/eclair
Published: 2016-02-17
Source: https://github.com/ACINQ/eclair/commit/de4caeb1fdcd624daa61650ab8fd2ef4907f7ee4
Type: security-commit

## Details
fix race condition in ChannelSpec test

## Patch
### eclair-demo/src/test/scala/fr/acinq/eclair/channel/ChannelSpec.scala
```diff
@@ -35,6 +35,12 @@ class ChannelSpec extends TestKit(ActorSystem("TestSystem")) with WordSpecLike w
   "channel" should {
     "open, propose, accept, fulfill htlcs and close" in {
       val blockchain = TestProbe("blockchain")
+      blockchain.ignoreMsg {
+        case m: WatchConfirmed => true
+        case m: WatchSpent => true
+        case m: WatchLost => true
+        case m: WatchConfirmedBasedOnOutputs => true
+      }
       val alice = system.actorOf(Props(new Channel(blockchain.ref, Alice.channelParams)), "Alice")
       val bob = system.actorOf(Props(new Channel(blockchain.ref, Bob.channelParams)), "Bob")
 
@@ -63,10 +69,6 @@ class ChannelSpec extends TestKit(ActorSystem("TestSystem")) with WordSpecLike w
         lockTime = 0
       )
       blockchain.reply((anchorTx, 0))
-      blockchain.expectMsgClass(classOf[WatchConfirmed])
-      blockchain.expectMsgClass(classOf[WatchSpent])
-      blockchain.expectMsgClass(classOf[WatchConfirmed])
-      blockchain.expectMsgClass(classOf[WatchSpent])
       blockchain.expectMsgClass(classOf[Publish])
 
       val Transition(_, OPEN_WAIT_FOR_OPEN_WITHANCHOR, OPEN_WAIT_FOR_COMMIT_SIG) = waitForAliceTransition
@@ -76,10 +78,8 @@ class ChannelSpec extends TestKit(ActorSystem("TestSystem")) with WordSpecLike w
       val Transition(_, OPEN_WAIT_FOR_ANCHOR, OPEN_WAITING_THEIRANCHOR) = waitForBobTransition
 
       blockchain.send(alice, BITCOIN_ANCHOR_DEPTHOK)
-      blockchain.expectMsgClass(classOf[WatchLost])
 
       blockchain.send(bob, BITCOIN_ANCHOR_DEPTHOK)
-      blockchain.expectMsgClass(classOf[WatchLost])
 
       val Transition(_, OPEN_WAITING_OURANCHOR, OPEN_WAIT_FOR_COMPLETE_OURANCHOR) = waitForAliceTransition
       val Transition(_, OPEN_WAITING_THEIRANCHOR, OPEN_WAIT_FOR_COMPLETE_THEIRANCHOR) = waitForBobTransition
@@ -111,10 +111,7 @@ class ChannelSpec extends TestKit(ActorSystem("TestSystem")) with WordSpecLike w
       val Transition(_, NORMAL_HIGHPRIO, WAIT_FOR_CLOSE_COMPLETE) = waitForAliceTransition
       val Transition(_, NORMAL_LOWPRIO, WAIT_FOR_CLOSE_ACK) = waitForBobTransition
 
-      blockchain.expectMsgClass(classOf[WatchConfirmedBasedOnOutputs])
-      blockchain.expectMsgClass(classOf[WatchConfirmed])
       val Publish(closingTx1) = blockchain.expectMsgClass(classOf[Publish])
-      blockchain.expectMsgClass(classOf[WatchConfirmed])
       val Publish(closingTx2) = blockchain.expectMsgClass(classOf[Publish])
 
       val Transition(_, WAIT_FOR_CLOSE_COMPLETE, CLOSING) = waitForAliceTransition
```
