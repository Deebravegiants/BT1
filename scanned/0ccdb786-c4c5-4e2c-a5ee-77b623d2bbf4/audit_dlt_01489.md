# [?] Fix HTLC fulfill race condition in integration spec (#1666)

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ACINQ/eclair
Published: 2021-01-19
Source: https://github.com/ACINQ/eclair/commit/9c4ab7d923a8e6947689c0129a2bfc6169aff657
Type: security-commit

## Details
Fix HTLC fulfill race condition in integration spec (#1666)

We were extracting F's commit tx from its internal state right after receiving
the `PaymentSent` event. The issue is that this could happen before the fulfill
was completely signed on both sides, so the commit tx we obtained would still
contain the HTLC and would be different from the one F would publish when
closing.

## Patch
### eclair-core/src/test/scala/fr/acinq/eclair/channel/states/h/ClosingStateSpec.scala
```diff
@@ -503,7 +503,7 @@ class ClosingStateSpec extends TestKitBaseClass with FixtureAnyFunSuiteLike with
     // actual test starts here
     channelUpdateListener.expectMsgType[LocalChannelDown]
     assert(closingState.htlcSuccessTxs.isEmpty && closingState.htlcTimeoutTxs.isEmpty && closingState.claimHtlcDelayedTxs.isEmpty)
-    // when the commit tx is signed, alice knows that the htlc she sent right before the unilateral close will never reach the chain
+    // when the commit tx is confirmed, alice knows that the htlc she sent right before the unilateral close will never reach the chain
     alice ! WatchEventConfirmed(BITCOIN_TX_CONFIRMED(aliceCommitTx), 0, 0, aliceCommitTx)
     // so she fails it
     val origin = alice.stateData.asInstanceOf[DATA_CLOSING].commitments.originChannels(htlc.id)
@@ -513,9 +513,31 @@ class ClosingStateSpec extends TestKitBaseClass with FixtureAnyFunSuiteLike with
     relayerA.expectNoMsg(100 millis)
   }
 
+  test("recv BITCOIN_TX_CONFIRMED (local commit with fulfill only signed by local)") { f =>
+    import f._
+    // bob sends an htlc
+    val (r, htlc) = addHtlc(110000000 msat, bob, alice, bob2alice, alice2bob)
+    crossSign(bob, alice, bob2alice, alice2bob)
+    relayerA.expectMsgType[RelayForward]
+    val aliceCommitTx = alice.stateData.asInstanceOf[DATA_NORMAL].commitments.localCommit.publishableTxs.commitTx.tx
+    assert(aliceCommitTx.txOut.size === 3) // 2 main outputs + 1 htlc
+
+    // alice fulfills the HTLC but bob doesn't receive the signature
+    alice ! CMD_FULFILL_HTLC(htlc.id, r, commit = true)
+    alice2bob.expectMsgType[UpdateFulfillHtlc]
+    alice2bob.forward(bob)
+    alice2bob.expectMsgType[CommitSig]
+    // note that bob doesn't receive the new sig!
+    // then we make alice unilaterally close the channel
+    val closingState = localClose(alice, alice2blockchain)
+    assert(closingState.commitTx === aliceCommitTx)
+    assert(closingState.htlcTimeoutTxs.isEmpty)
+    assert(closingState.htlcSuccessTxs.size === 1)
+    assert(closingState.claimHtlcDelayedTxs.size === 1)
+  }
+
   test("recv BITCOIN_TX_CONFIRMED (remote commit with htlcs only signed by local in next remote commit)") { f =>
     import f._
-    val sender = TestProbe()
     val listener = TestProbe()
     system.eventStream.subscribe(listener.ref, classOf[PaymentSettlingOnChain])
     val bobCommitTx = bob.stateData.asInstanceOf[DATA_NORMAL].commitments.localCommit.publishableTxs.commitTx.tx
```

### eclair-core/src/test/scala/fr/acinq/eclair/integration/ChannelIntegrationSpec.scala
```diff
@@ -655,6 +655,13 @@ class AnchorOutputChannelIntegrationSpec extends ChannelIntegrationSpec {
     val ps = sender.expectMsgType[PaymentSent](60 seconds)
     assert(ps.id == paymentId)
 
+    // we make sure the htlc has been removed from F's commitment before we force-close
+    awaitCond({
+      sender.send(nodes("F").register, Register.Forward(sender.ref, channelId, CMD_GETSTATEDATA(ActorRef.noSender)))
+      val stateDataF = sender.expectMsgType[RES_GETSTATEDATA[DATA_NORMAL]].data
+      stateDataF.commitments.localCommit.spec.htlcs.isEmpty
+    }, max = 20 seconds, interval = 1 second)
+
     sender.send(nodes("F").register, Register.Forward(sender.ref, channelId, CMD_GETSTATEDATA(ActorRef.noSender)))
     val stateDataF = sender.expectMsgType[RES_GETSTATEDATA[DATA_NORMAL]].data
     val commitmentIndex = stateDataF.commitments.localCommit.index
```
