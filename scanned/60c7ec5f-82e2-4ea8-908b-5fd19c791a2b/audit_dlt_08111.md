# [?] Fix race condition in 'stream updates to front' test (#1978)

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ACINQ/eclair
Published: 2021-09-30
Source: https://github.com/ACINQ/eclair/commit/97393b13b43d60887eef3b747ceb86f2e9938d2b
Type: security-commit

## Details
Fix race condition in 'stream updates to front' test (#1978)

As usual, the race condition is due to a delay before subscribing to the event stream.

## Patch
### eclair-core/src/test/scala/fr/acinq/eclair/router/RouterSpec.scala
```diff
@@ -681,11 +681,20 @@ class RouterSpec extends BaseRouterSpec {
     }
     assert(nodes.size === 8 && channels.size === 5 && updates.size === 10) // public channels only
 
+    // just making sure that we have been subscribed to network events, otherwise there is a possible race condition
+    awaitCond({
+      system.eventStream.publish(SyncProgress(42))
+      sender.msgAvailable
+    }, max = 30 seconds)
+
     // new announcements
     val update_ab_2 = makeChannelUpdate(Block.RegtestGenesisBlock.hash, priv_a, b, channelId_ab, CltvExpiryDelta(7), htlcMinimumMsat = 0 msat, feeBaseMsat = 10 msat, feeProportionalMillionths = 10, htlcMaximumMsat = htlcMaximum, timestamp = update_ab.timestamp + 1)
     val peerConnection = TestProbe()
     router ! PeerRoutingMessage(peerConnection.ref, remoteNodeId, update_ab_2)
-    sender.expectMsg(ChannelUpdatesReceived(List(update_ab_2)))
+    sender.fishForMessage() {
+      case cu: ChannelUpdatesReceived => cu == ChannelUpdatesReceived(List(update_ab_2))
+      case _ => false
+    }
   }
 
 }
```
