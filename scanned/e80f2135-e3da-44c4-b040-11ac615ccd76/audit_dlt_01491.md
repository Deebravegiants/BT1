# [?] Fix race condition in integration test (#1564)

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ACINQ/eclair
Published: 2020-10-15
Source: https://github.com/ACINQ/eclair/commit/bffb7a3fe1e5455c8075ce816e48fdb342f5bc3e
Type: security-commit

## Details
Fix race condition in integration test (#1564)

In the revoked commit tx case, both nodes are competing to claim the
HTLC outputs from the commit tx.

The test incorrectly assumed that node F would always win that race.

## Patch
### eclair-core/src/test/scala/fr/acinq/eclair/integration/ChannelIntegrationSpec.scala
```diff
@@ -738,10 +738,11 @@ class AnchorOutputChannelIntegrationSpec extends ChannelIntegrationSpec {
     sender.expectMsg(revokedCommitTx.txid)
     // get the revoked commitment confirmed: now HTLC txs can be published
     generateBlocks(bitcoincli, 2)
-    bitcoinClient.publishTransaction(htlcSuccess.head).pipeTo(sender.ref)
-    sender.expectMsg(htlcSuccess.head.txid)
-    bitcoinClient.publishTransaction(htlcTimeout.head).pipeTo(sender.ref)
-    sender.expectMsg(htlcTimeout.head.txid)
+    // NB: The test cannot be deterministic because there is a race between C and F here; C may publish more quickly and
+    // claim the HTLC outputs directly from the commit tx. As a result we may have different combinations of transactions
+    // if the test is run several times. It's okay, we just need to make sure that the test never fails.
+    bitcoinClient.publishTransaction(htlcSuccess.head)
+    bitcoinClient.publishTransaction(htlcTimeout.head)
     // at this point C should have 6 recv transactions: its previous main output, F's main output and all htlc outputs (taken as punishment)
     awaitCond({
       val receivedByC = listReceivedByAddress(finalAddressC, sender)
```
