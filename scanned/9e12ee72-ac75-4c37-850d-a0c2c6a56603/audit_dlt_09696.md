# [?] test for double spend rejection

## Summary
Severity: Unknown
Chain: Ergo
Component: ergoplatform/ergo
Published: 2020-10-12
Source: https://github.com/ergoplatform/ergo/commit/1bee3b5819cf70b6545c2cdc9546c532f2f9466c
Type: security-commit

## Details
test for double spend rejection

## Patch
### src/main/scala/org/ergoplatform/nodeView/mempool/ErgoMemPool.scala
```diff
@@ -68,9 +68,11 @@ class ErgoMemPool private[mempool](pool: OrderedTxPool)(implicit settings: ErgoS
     }
     doubleSpendingInputOpt match {
       case Some(doubleSpendingInput) =>
+        val ownWtx = weighted(tx)
         val doubleWtx = pool.inputs.get(doubleSpendingInput.boxId).get //.get
-        if (weighted(tx).weight > doubleWtx.weight) {
-          new ErgoMemPool(pool.put(tx)) -> ProcessingOutcome.Accepted
+        if (ownWtx.weight > doubleWtx.weight) {
+          val doubleTx = pool.orderedTransactions.get(doubleWtx).get //.get
+          new ErgoMemPool(pool.put(tx).remove(doubleTx)) -> ProcessingOutcome.Accepted
         } else {
           this -> ProcessingOutcome.DoubleSpendingLoser(doubleWtx.id)
         }
@@ -143,14 +145,15 @@ object ErgoMemPool {
 
   private[mempool] def extractFee(tx: ErgoTransaction)(implicit ms: MonetarySettings): Long =
     tx.outputs
-      .filter(_.ergoTree == ms.feeProposition)
+      .filter(b => java.util.Arrays.equals(b.propositionBytes, ms.feePropositionBytes))
       .map(_.value)
       .sum
 
   private[mempool] def weighted(tx: ErgoTransaction)(implicit ms: MonetarySettings): WeightedTxId = {
     val fee = extractFee(tx)
     // We multiply by 1024 for better precision
-    WeightedTxId(tx.id, fee * 1024 / tx.size)
+    val weight = fee * 1024 / tx.size
+    WeightedTxId(tx.id, weight)
   }
 
 }
```

### src/test/scala/org/ergoplatform/nodeView/mempool/ErgoMemPoolSpec.scala
```diff
@@ -1,13 +1,16 @@
 package org.ergoplatform.nodeView.mempool
 
-import org.ergoplatform.{ErgoBoxCandidate, Input}
-import org.ergoplatform.modifiers.mempool.ErgoTransaction
+import org.ergoplatform.{ErgoBoxCandidate, Input, UnsignedInput}
+import org.ergoplatform.modifiers.mempool.{ErgoTransaction, UnsignedErgoTransaction}
 import org.ergoplatform.nodeView.mempool.ErgoMemPool.ProcessingOutcome
 import org.ergoplatform.nodeView.state.wrapped.WrappedUtxoState
 import org.ergoplatform.utils.ErgoTestHelpers
 import org.ergoplatform.utils.generators.ErgoGenerators
+import org.ergoplatform.wallet.interpreter.ErgoProvingInterpreter
 import org.scalatest.FlatSpec
 import org.scalatest.prop.PropertyChecks
+import sigmastate.Values.ByteArrayConstant
+import sigmastate.interpreter.ContextExtension
 
 import scala.util.Random
 
@@ -47,6 +50,44 @@ class ErgoMemPoolSpec extends FlatSpec
     }
   }
 
+  it should "reject double-spending transaction if it is paying no more than one already sitting in the pool" in {
+    val (us, bh) = createUtxoState()
+    val genesis = validFullBlock(None, us, bh, Random)
+    val wus = WrappedUtxoState(us, bh, stateConstants).applyModifier(genesis).get
+
+    val feeProp = settings.chainSettings.monetary.feeProposition
+    val inputBox = wus.takeBoxes(1).head
+    val feeOut = new ErgoBoxCandidate(inputBox.value, feeProp, creationHeight = 0)
+
+    val prover = ErgoProvingInterpreter(IndexedSeq.empty, parameters)
+
+    def rndContext() = ContextExtension(Map(
+      (1: Byte) -> ByteArrayConstant(Array.fill(10 + Random.nextInt(50))(0: Byte)))
+    )
+
+    val tx1Like = prover.sign(UnsignedErgoTransaction (
+      IndexedSeq(new UnsignedInput(inputBox.id, rndContext())),
+      IndexedSeq(feeOut)
+    ), IndexedSeq(inputBox), IndexedSeq.empty, emptyStateContext).get
+
+    val tx2Like = prover.sign(UnsignedErgoTransaction (
+      IndexedSeq(new UnsignedInput(inputBox.id, rndContext())),
+      IndexedSeq(feeOut)
+    ), IndexedSeq(inputBox), IndexedSeq.empty, emptyStateContext).get
+
+    val tx1 = ErgoTransaction(tx1Like.inputs, tx1Like.outputCandidates)
+    val tx2 = ErgoTransaction(tx2Like.inputs, tx2Like.outputCandidates)
+
+    var pool = ErgoMemPool.empty(settings)
+    pool = pool.process(tx1, us)._1
+
+    if(tx2.size >= tx1.size) {
+      pool.process(tx2, us)._2.isInstanceOf[ProcessingOutcome.DoubleSpendingLoser] shouldBe true
+    } else {
+      pool.process(tx2, us)._2.isInstanceOf[ProcessingOutcome.DoubleSpendingLoser] shouldBe false
+    }
+  }
+
   it should "decline transactions invalidated earlier" in {
     val us = createUtxoState()._1
     var pool = ErgoMemPool.empty(settings)
```
