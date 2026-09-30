# [?] Improve wallet double-spend detection (#2258)

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ACINQ/eclair
Published: 2022-05-16
Source: https://github.com/ACINQ/eclair/commit/10eb9e932f9c0de06cc8926230d8ad4e2d1d9e2c
Type: security-commit

## Details
Improve wallet double-spend detection (#2258)

Our mechanism to detect double-spending wasn't correctly taking into
account unconfirmed inputs. This was only used in single-funder scenarios
so it could only be an issue in rare edge cases, where it would not lead
to any loss of funds as we keep commit tx data in our DB even for closed
channels.

## Patch
### eclair-core/src/main/scala/fr/acinq/eclair/blockchain/bitcoind/rpc/BitcoinCoreClient.scala
```diff
@@ -17,8 +17,8 @@
 package fr.acinq.eclair.blockchain.bitcoind.rpc
 
 import fr.acinq.bitcoin.scalacompat.Crypto.PublicKey
-import fr.acinq.bitcoin.{Bech32, Block}
 import fr.acinq.bitcoin.scalacompat._
+import fr.acinq.bitcoin.{Bech32, Block}
 import fr.acinq.eclair.ShortChannelId.coordinates
 import fr.acinq.eclair.blockchain.OnChainWallet
 import fr.acinq.eclair.blockchain.OnChainWallet.{MakeFundingTxResponse, OnChainBalance}
@@ -95,11 +95,41 @@ class BitcoinCoreClient(val rpcClient: BitcoinJsonRPCClient) extends OnChainWall
       index = txs.indexOf(JString(txid.toHex))
     } yield (BlockHeight(height.toInt), index)
 
+  /**
+   * Return true if this output can potentially be spent.
+   *
+   * Note that if this function returns false, that doesn't mean the output cannot be spent. The output could be unknown
+   * (not in the blockchain nor in the mempool) but could reappear later and be spendable at that point. If you want to
+   * ensure that an output is not spendable anymore, you should use [[isTransactionOutputSpent]].
+   */
   def isTransactionOutputSpendable(txid: ByteVector32, outputIndex: Int, includeMempool: Boolean)(implicit ec: ExecutionContext): Future[Boolean] =
     for {
       json <- rpcClient.invoke("gettxout", txid, outputIndex, includeMempool)
     } yield json != JNull
 
+  /**
+   * Return true if this output has already been spent by a confirmed transaction.
+   * Note that a reorg may invalidate the result of this function and make a spent output spendable again.
+   */
+  def isTransactionOutputSpent(txid: ByteVector32, outputIndex: Int)(implicit ec: ExecutionContext): Future[Boolean] = {
+    getTxConfirmations(txid).flatMap {
+      case Some(confirmations) if confirmations > 0 =>
+        // There is an important limitation when using isTransactionOutputSpendable: if it returns false, it can mean a
+        // few different things:
+        //  - the input has been spent
+        //  - the input is coming from an unconfirmed transaction (in the mempool) but can be unspent
+        //  - the input is unknown (it may come from an unconfirmed transaction that we don't have in our mempool)
+        //
+        // The only way to make sure that our output has been spent is to verify that it is coming from a confirmed
+        // transaction and that it has been spent by another confirmed transaction. We want to ignore the mempool to
+        // only consider spending transactions that have been confirmed.
+        isTransactionOutputSpendable(txid, outputIndex, includeMempool = false).map(r => !r)
+      case _ =>
+        // If the output itself isn't in the blockchain, it cannot be spent by a confirmed transaction.
+        Future.successful(false)
+    }
+  }
+
   def doubleSpent(tx: Transaction)(implicit ec: ExecutionContext): Future[Boolean] =
     for {
       exists <- getTransaction(tx.txid)
@@ -111,16 +141,20 @@ class BitcoinCoreClient(val rpcClient: BitcoinJsonRPCClient) extends OnChainWall
             false // won't be reached
           case _ => false
         }
-      doublespent <- if (exists) {
-        // if the tx is in the blockchain, it can't have been double-spent
+      doubleSpent <- if (exists) {
+        // if the tx is in the blockchain or in the mempool, it can't have been double-spent
         Future.successful(false)
       } else {
-        // if the tx wasn't in the blockchain and one of its inputs has been spent, it is double-spent
-        // NB: we don't look in the mempool, so it means that we will only consider that the tx has been double-spent if
-        // the overriding transaction has been confirmed
-        Future.sequence(tx.txIn.map(txIn => isTransactionOutputSpendable(txIn.outPoint.txid, txIn.outPoint.index.toInt, includeMempool = false))).map(_.exists(_ == false))
+        // The only way to make sure that our transaction has been double-spent is to find an input that is coming from
+        // a confirmed transaction and that it has been spent by another confirmed transaction.
+        //
+        // Note that if our transaction only had unconfirmed inputs and the transactions creating those inputs have
+        // themselves been double-spent, we will never be able to consider our transaction double-spent. With the
+        // information we have, these unknown inputs could eventually reappear and the transaction could be broadcast
+        // again.
+        Future.sequence(tx.txIn.map(txIn => isTransactionOutputSpent(txIn.outPoint.txid, txIn.outPoint.index.toInt))).map(_.exists(_ == true))
       }
-    } yield doublespent
+    } yield doubleSpent
 
   /**
    * Iterate over blocks to find the transaction that has spent a given output.
```

### eclair-core/src/test/scala/fr/acinq/eclair/blockchain/bitcoind/BitcoinCoreClientSpec.scala
```diff
@@ -19,10 +19,11 @@ package fr.acinq.eclair.blockchain.bitcoind
 import akka.actor.Status.Failure
 import akka.pattern.pipe
 import akka.testkit.TestProbe
+import fr.acinq.bitcoin
 import fr.acinq.bitcoin.scalacompat.Crypto.PublicKey
 import fr.acinq.bitcoin.scalacompat.{Block, BtcDouble, ByteVector32, MilliBtcDouble, OutPoint, Satoshi, SatoshiLong, Script, ScriptWitness, Transaction, TxIn, TxOut}
-import fr.acinq.bitcoin
 import fr.acinq.eclair.blockchain.OnChainWallet.{MakeFundingTxResponse, OnChainBalance}
+import fr.acinq.eclair.blockchain.WatcherSpec.{createSpendManyP2WPKH, createSpendP2WPKH}
 import fr.acinq.eclair.blockchain.bitcoind.BitcoindService.BitcoinReq
 import fr.acinq.eclair.blockchain.bitcoind.rpc.BitcoinCoreClient._
 import fr.acinq.eclair.blockchain.bitcoind.rpc.BitcoinJsonRPCAuthMethod.UserPassword
@@ -655,25 +656,18 @@ class BitcoinCoreClientSpec extends TestKitBaseClass with BitcoindService with A
     val bitcoinClient = new BitcoinCoreClient(bitcoinrpcclient)
 
     // first let's create a tx
-    val address = "n2YKngjUp139nkjKvZGnfLRN6HzzYxJsje"
-    bitcoinrpcclient.invoke("createrawtransaction", Array.empty, Map(address -> 6)).pipeTo(sender.ref)
-    val JString(noinputTx1) = sender.expectMsgType[JString]
-    bitcoinrpcclient.invoke("fundrawtransaction", noinputTx1).pipeTo(sender.ref)
-    val json = sender.expectMsgType[JValue]
-    val JString(unsignedtx1) = json \ "hex"
-    bitcoinrpcclient.invoke("signrawtransactionwithwallet", unsignedtx1).pipeTo(sender.ref)
-    val JString(signedTx1) = sender.expectMsgType[JValue] \ "hex"
-    val tx1 = Transaction.read(signedTx1)
+    val noInputTx1 = Transaction(2, Nil, Seq(TxOut(500_000 sat, Script.pay2wpkh(randomKey().publicKey))), 0)
+    bitcoinClient.fundTransaction(noInputTx1, FundTransactionOptions(FeeratePerKw(2500 sat))).pipeTo(sender.ref)
+    val unsignedTx1 = sender.expectMsgType[FundTransactionResponse].tx
+    bitcoinClient.signTransaction(unsignedTx1).pipeTo(sender.ref)
+    val tx1 = sender.expectMsgType[SignTransactionResponse].tx
 
     // let's then generate another tx that double spends the first one
-    val inputs = tx1.txIn.map(txIn => Map("txid" -> txIn.outPoint.txid.toString, "vout" -> txIn.outPoint.index)).toArray
-    bitcoinrpcclient.invoke("createrawtransaction", inputs, Map(address -> tx1.txOut.map(_.amount).sum.toLong * 1.0 / 1e8)).pipeTo(sender.ref)
-    val JString(unsignedtx2) = sender.expectMsgType[JValue]
-    bitcoinrpcclient.invoke("signrawtransactionwithwallet", unsignedtx2).pipeTo(sender.ref)
-    val JString(signedTx2) = sender.expectMsgType[JValue] \ "hex"
-    val tx2 = Transaction.read(signedTx2)
-
-    // tx1/tx2 haven't been published, so tx1 isn't double spent
+    val unsignedTx2 = tx1.copy(txOut = Seq(TxOut(tx1.txOut.map(_.amount).sum, Script.pay2wpkh(randomKey().publicKey))))
+    bitcoinClient.signTransaction(unsignedTx2).pipeTo(sender.ref)
+    val tx2 = sender.expectMsgType[SignTransactionResponse].tx
+
+    // tx1/tx2 haven't been published, so tx1 isn't double-spent
     bitcoinClient.doubleSpent(tx1).pipeTo(sender.ref)
     sender.expectMsg(false)
     // let's publish tx2
@@ -682,11 +676,79 @@ class BitcoinCoreClientSpec extends TestKitBaseClass with BitcoindService with A
     // tx2 hasn't been confirmed so tx1 is still not considered double-spent
     bitcoinClient.doubleSpent(tx1).pipeTo(sender.ref)
     sender.expectMsg(false)
+    // tx2 isn't considered double-spent either
+    bitcoinClient.doubleSpent(tx2).pipeTo(sender.ref)
+    sender.expectMsg(false)
     // let's confirm tx2
     generateBlocks(1)
-    // this time tx1 has been double spent
+    // this time tx1 has been double-spent
     bitcoinClient.doubleSpent(tx1).pipeTo(sender.ref)
     sender.expectMsg(true)
+    // and tx2 isn't considered double-spent since it's confirmed
+    bitcoinClient.doubleSpent(tx2).pipeTo(sender.ref)
+    sender.expectMsg(false)
+  }
+
+  test("detect if tx has been double-spent (with unconfirmed inputs)") {
+    val sender = TestProbe()
+    val bitcoinClient = new BitcoinCoreClient(bitcoinrpcclient)
+    val priv = randomKey()
+
+    // Let's create one confirmed and one unconfirmed utxo.
+    val (confirmedParentTx, unconfirmedParentTx) = {
+      val txs = Seq(400_000 sat, 500_000 sat).map(amount => {
+        val noInputTx = Transaction(2, Nil, Seq(TxOut(amount, Script.pay2wpkh(priv.publicKey))), 0)
+        bitcoinClient.fundTransaction(noInputTx, FundTransactionOptions(FeeratePerKw(2500 sat), lockUtxos = true)).pipeTo(sender.ref)
+        val unsignedTx = sender.expectMsgType[FundTransactionResponse].tx
+        bitcoinClient.signTransaction(unsignedTx).pipeTo(sender.ref)
+        sender.expectMsgType[SignTransactionResponse].tx
+      })
+      bitcoinClient.publishTransaction(txs.head).pipeTo(sender.ref)
+      sender.expectMsg(txs.head.txid)
+      generateBlocks(1)
+      bitcoinClient.publishTransaction(txs.last).pipeTo(sender.ref)
+      sender.expectMsg(txs.last.txid)
+      (txs.head, txs.last)
+    }
+
+    // Let's spend those unconfirmed utxos.
+    val childTx = createSpendManyP2WPKH(Seq(confirmedParentTx, unconfirmedParentTx), priv, priv.publicKey, 500 sat, 0, 0)
+    // The tx hasn't been published, so it isn't double-spent.
+    bitcoinClient.doubleSpent(childTx).pipeTo(sender.ref)
+    sender.expectMsg(false)
+    // We publish the tx and verify it isn't double-spent.
+    bitcoinClient.publishTransaction(childTx).pipeTo(sender.ref)
+    sender.expectMsg(childTx.txid)
+    bitcoinClient.doubleSpent(childTx).pipeTo(sender.ref)
+    sender.expectMsg(false)
+
+    // We double-spend the unconfirmed parent, which evicts our child transaction.
+    {
+      val previousAmountOut = unconfirmedParentTx.txOut.map(_.amount).sum
+      val unsignedTx = unconfirmedParentTx.copy(txOut = Seq(TxOut(previousAmountOut - 50_000.sat, Script.pay2wpkh(randomKey().publicKey))))
+      bitcoinClient.signTransaction(unsignedTx).pipeTo(sender.ref)
+      val signedTx = sender.expectMsgType[SignTransactionResponse].tx
+      bitcoinClient.publishTransaction(signedTx).pipeTo(sender.ref)
+      sender.expectMsg(signedTx.txid)
+    }
+
+    // We can't know whether the child transaction is double-spent or not, as its unconfirmed input is now unknown: it's
+    // not in the blockchain nor in the mempool. This unknown input may reappear in the future and the tx could then be
+    // published again.
+    bitcoinClient.doubleSpent(childTx).pipeTo(sender.ref)
+    sender.expectMsg(false)
+
+    // We double-spend the confirmed input.
+    val spendingTx = createSpendP2WPKH(confirmedParentTx, priv, priv.publicKey, 600 sat, 0, 0)
+    bitcoinClient.publishTransaction(spendingTx).pipeTo(sender.ref)
+    sender.expectMsg(spendingTx.txid)
+    // While the spending transaction is unconfirmed, we don't consider our transaction double-spent.
+    bitcoinClient.doubleSpent(childTx).pipeTo(sender.ref)
+    sender.expectMsg(false)
+    // Once the spending transaction confirms, we know that our transaction is double-spent.
+    generateBlocks(1)
+    bitcoinClient.doubleSpent(childTx).pipeTo(sender.ref)
+    sender.expectMsg(true)
   }
 
   test("find spending transaction of a given output") {
```
