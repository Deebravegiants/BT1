# [?] Fix crash

## Summary
Severity: Unknown
Chain: Ergo
Component: ergoplatform/ergo
Published: 2024-04-10
Source: https://github.com/ergoplatform/ergo/commit/ed207e4e361ba2c1bfdc54d279bb29a2b21b3287
Type: security-commit

## Details
Fix crash

## Patch
### src/main/scala/org/ergoplatform/nodeView/history/extra/ExtraIndexer.scala
```diff
@@ -25,16 +25,14 @@ import spire.syntax.all.cfor
 import java.util.concurrent.ConcurrentHashMap
 import scala.collection.mutable
 import scala.collection.concurrent
-import scala.concurrent.{ExecutionContextExecutor, Future}
+import scala.concurrent.Future
 import scala.jdk.CollectionConverters._
 
 /**
   * Base trait for extra indexer actor and its test.
   */
 trait ExtraIndexerBase extends Actor with Stash with ScorexLogging {
 
-  private implicit val ec: ExecutionContextExecutor = context.dispatcher
-
   /**
     * Max buffer size (determined by config)
     */
@@ -86,22 +84,22 @@ trait ExtraIndexerBase extends Actor with Stash with ScorexLogging {
     * @param height - blockheight to get transations from
     * @return transactions at height
     */
-  private def getBlockTransactionsAt(height: Int): BlockTransactions = {
-    val txs = blockCache.remove(height).getOrElse(history.bestBlockTransactionsAt(height).get)
-    if (height % 1000 == 0) blockCache.keySet.filter(_ < height).map(blockCache.remove)
-    if (readingUpTo - height < 300 && chainHeight - height > 1000) {
-      readingUpTo = math.min(height + 1001, chainHeight)
-      val blockNums = height + 1 to readingUpTo by 50
-      blockNums.zip(blockNums.tail).map { range => // ranges of 50 blocks for each thread to read
-        Future {
-          (range._1 until range._2).foreach { blockNum =>
-            blockCache.put(blockNum, history.bestBlockTransactionsAt(blockNum).get)
-          }
+  private def getBlockTransactionsAt(height: Int): Option[BlockTransactions] =
+    blockCache.remove(height).orElse(history.bestBlockTransactionsAt(height)).map { txs =>
+      if (height % 1000 == 0) blockCache.keySet.filter(_ < height).map(blockCache.remove)
+      if (readingUpTo - height < 300 && chainHeight - height > 1000) {
+        readingUpTo = math.min(height + 1001, chainHeight)
+        val blockNums = height + 1 to readingUpTo by 50
+        blockNums.zip(blockNums.tail).map { range => // ranges of 50 blocks for each thread to read
+          Future {
+            (range._1 until range._2).foreach { blockNum =>
+              history.bestBlockTransactionsAt(blockNum).map(blockCache.put(blockNum, _))
+            }
+          }(context.dispatcher)
         }
       }
+      txs
     }
-    txs
-  }
 
   /**
     * Spend an IndexedErgoBox from buffer or database. Also record tokens for later use in balance tracking logic.
@@ -149,7 +147,7 @@ trait ExtraIndexerBase extends Actor with Stash with ScorexLogging {
         }
       case None => // address not found at all
         spendOrReceive match {
-          case Left(iEb) => log.warn(s"Unknown address spent box ${bytesToId(iEb.box.id)}") // spend box should never happen by an unknown address
+          case Left(iEb) => log.error(s"Unknown address spent box ${bytesToId(iEb.box.id)}") // spend box should never happen by an unknown address
           case Right(iEb) => trees.put(id, IndexedErgoAddress(id).initBalance.addTx(state.globalTxIndex).addBox(iEb)) // receive box, new address
         }
     }
@@ -176,7 +174,7 @@ trait ExtraIndexerBase extends Actor with Stash with ScorexLogging {
           case Right(iEb) => tokens.put(id, x.addBox(iEb)) // receive box
         }
       case None => // token not found at all
-        log.warn(s"Unknown token $id") // spend box should never happen by an unknown token
+        log.error(s"Unknown token $id") // spend box should never happen by an unknown token
     }
   }
 
@@ -234,18 +232,25 @@ trait ExtraIndexerBase extends Actor with Stash with ScorexLogging {
     * @param headerOpt - header to index blocktransactions of (used after caught up with chain)
     */
   protected def index(state: IndexerState, headerOpt: Option[Header] = None): IndexerState = {
-    val bt = headerOpt.flatMap { header =>
+    val btOpt = headerOpt.flatMap { header =>
       history.typedModifierById[BlockTransactions](header.transactionsId)
-    }.getOrElse(getBlockTransactionsAt(state.indexedHeight))
+    }.orElse(getBlockTransactionsAt(state.indexedHeight))
     val height = headerOpt.map(_.height).getOrElse(state.indexedHeight)
 
+    if(btOpt.isEmpty) {
+      log.warn(s"Could not read block $height / $chainHeight from database, waiting for new block until retrying")
+      return state.decrementIndexedHeight.copy(caughtUp = true)
+    }
+
+    val txs: Seq[ErgoTransaction] = btOpt.get.txs
+
     var boxCount: Int = 0
     implicit var newState: IndexerState = state
 
     // record transactions and boxes
-    cfor(0)(_ < bt.txs.length, _ + 1) { n =>
+    cfor(0)(_ < txs.length, _ + 1) { n =>
 
-      val tx: ErgoTransaction = bt.txs(n)
+      val tx: ErgoTransaction = txs(n)
       val inputs: Array[Long] = Array.ofDim[Long](tx.inputs.length)
       val outputs: Array[Long] = Array.ofDim[Long](tx.outputs.length)
 
@@ -302,7 +307,7 @@ trait ExtraIndexerBase extends Actor with Stash with ScorexLogging {
 
     }
 
-    log.info(s"Buffered block $height / $chainHeight [txs: ${bt.txs.length}, boxes: $boxCount] (buffer: $modCount / $saveLimit)")
+    log.info(s"Buffered block $height / $chainHeight [txs: ${txs.length}, boxes: $boxCount] (buffer: $modCount / $saveLimit)")
 
     val maxHeight = headerOpt.map(_.height).getOrElse(chainHeight)
     newState.copy(caughtUp = newState.indexedHeight == maxHeight)
@@ -314,7 +319,7 @@ trait ExtraIndexerBase extends Actor with Stash with ScorexLogging {
     * @param state  - current state of indexer
     * @param height - starting height
     */
-  protected def removeAfter(state: IndexerState, height: Int): IndexerState = {
+  private def removeAfter(state: IndexerState, height: Int): IndexerState = {
 
     var newState: IndexerState = state
 
```

### src/main/scala/org/ergoplatform/nodeView/history/extra/IndexerState.scala
```diff
@@ -20,6 +20,7 @@ case class IndexerState(indexedHeight: Int,
   def rollbackInProgress: Boolean = rollbackTo > 0
 
   def incrementIndexedHeight: IndexerState = copy(indexedHeight = indexedHeight + 1)
+  def decrementIndexedHeight: IndexerState = copy(indexedHeight = indexedHeight - 1)
 
   def incrementTxIndex: IndexerState = copy(globalTxIndex = globalTxIndex + 1)
   def incrementBoxIndex: IndexerState = copy(globalBoxIndex = globalBoxIndex + 1)
```
