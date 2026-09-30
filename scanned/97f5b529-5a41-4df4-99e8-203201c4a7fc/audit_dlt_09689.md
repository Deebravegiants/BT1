# [?] fixed rollback sometimes crashing indexer by trying to retrieve an already deleted address

## Summary
Severity: Unknown
Chain: Ergo
Component: ergoplatform/ergo
Published: 2023-04-30
Source: https://github.com/ergoplatform/ergo/commit/d2bffda6d940577657b11c6ee9221806e0670186
Type: security-commit

## Details
fixed rollback sometimes crashing indexer by trying to retrieve an already deleted address

## Patch
### src/main/scala/org/ergoplatform/http/api/BlockchainApiRoute.scala
```diff
@@ -105,7 +105,7 @@ case class BlockchainApiRoute(readersHolder: ActorRef, ergoSettings: ErgoSetting
   private def getIndexedHeightF: Future[Json] =
     getHistory.map { history =>
       Json.obj(
-        "indexedHeight" -> ExtraIndexer.getIndex(ExtraIndexer.IndexedHeightKey, history).getInt().asJson,
+        "indexedHeight" -> getIndex(ExtraIndexer.IndexedHeightKey, history).getInt.asJson,
         "fullHeight" -> history.fullBlockHeight.asJson
       )
     }
```

### src/main/scala/org/ergoplatform/nodeView/history/extra/ExtraIndexer.scala
```diff
@@ -278,10 +278,11 @@ trait ExtraIndexerBase extends ScorexLogging {
     log.info(s"Rolling back indexes from $indexedHeight to $height")
 
     val lastTxToKeep: ErgoTransaction = history.bestBlockTransactionsAt(height).get.txs.last
+    val txTarget: Long = history.typedExtraIndexById[IndexedErgoTransaction](lastTxToKeep.id).get.globalIndex
+    val boxTarget: Long = history.typedExtraIndexById[IndexedErgoBox](bytesToId(lastTxToKeep.outputs.last.id)).get.globalIndex
+    val toRemove: ArrayBuffer[ModifierId] = ArrayBuffer.empty[ModifierId]
 
     // remove all tx indexes
-    val txTarget: Long = history.typedExtraIndexById[IndexedErgoTransaction](lastTxToKeep.id).get.globalIndex
-    val txs: ArrayBuffer[ModifierId] = ArrayBuffer.empty[ModifierId]
     globalTxIndex -= 1
     while(globalTxIndex > txTarget) {
       val tx: IndexedErgoTransaction = NumericTxIndex.getTxByNumber(history, globalTxIndex).get
@@ -291,38 +292,35 @@ trait ExtraIndexerBase extends ScorexLogging {
         val address = history.typedExtraIndexById[IndexedErgoAddress](hashErgoTree(iEb.box.ergoTree)).get.addBox(iEb, record = false)
         address.findAndModBox(iEb.globalIndex, history)
         historyStorage.insertExtra(Array.empty, Array[ExtraIndex](iEb, address) ++ address.segments)
-        address.segments.clear()
       })
-      txs += tx.id // tx by id
-      txs += bytesToId(NumericTxIndex.indexToBytes(globalTxIndex)) // tx id by number
+      toRemove += tx.id // tx by id
+      toRemove += bytesToId(NumericTxIndex.indexToBytes(globalTxIndex)) // tx id by number
       globalTxIndex -= 1
     }
     globalTxIndex += 1
-    historyStorage.removeExtra(txs.toArray)
 
     // remove all box indexes, tokens and address balances
-    val boxTarget: Long = history.typedExtraIndexById[IndexedErgoBox](bytesToId(lastTxToKeep.outputs.last.id)).get.globalIndex
-    val toRemove: ArrayBuffer[ModifierId] = ArrayBuffer.empty[ModifierId]
     globalBoxIndex -= 1
     while(globalBoxIndex > boxTarget) {
       val iEb: IndexedErgoBox = NumericBoxIndex.getBoxByNumber(history, globalBoxIndex).get
-      val address: IndexedErgoAddress = history.typedExtraIndexById[IndexedErgoAddress](hashErgoTree(iEb.box.ergoTree)).get
-      address.spendBox(iEb)
       cfor(0)(_ < iEb.box.additionalTokens.length, _ + 1) { i =>
         history.typedExtraIndexById[IndexedToken](IndexedToken.fromBox(iEb.box, i).id) match {
           case Some(token) if token.boxId == iEb.id =>
             toRemove += token.id // token created, delete
           case _ => // no token created
         }
       }
-      address.rollback(txTarget, boxTarget, _history)
+      history.typedExtraIndexById[IndexedErgoAddress](hashErgoTree(iEb.box.ergoTree)).map { address =>
+        address.spendBox(iEb)
+        toRemove ++= address.rollback(txTarget, boxTarget, _history)
+      }
       toRemove += iEb.id // box by id
       toRemove += bytesToId(NumericBoxIndex.indexToBytes(globalBoxIndex)) // box id by number
       globalBoxIndex -= 1
     }
+    globalBoxIndex += 1
 
     // Reset indexer flags
-    globalBoxIndex += 1
     indexedHeight = height
     caughtUp = false
     rollback = false
@@ -434,7 +432,7 @@ object ExtraIndexer {
   /**
    * Current newest database schema version. Used to force extra database resync.
    */
-  val NewestVersion: Int = 2
+  val NewestVersion: Int = 3
   val NewestVersionBytes: Array[Byte] = ByteBuffer.allocate(4).putInt(NewestVersion).array
 
   val IndexedHeightKey: Array[Byte] = Algos.hash("indexed height")
```

### src/main/scala/org/ergoplatform/nodeView/history/extra/IndexedErgoAddress.scala
```diff
@@ -215,10 +215,13 @@ case class IndexedErgoAddress(treeHash: ModifierId,
     * @param txTarget  - remove transaction numbers above this number
     * @param boxTarget - remove box numbers above this number and revert the balance
     * @param _history  - history handle to update address in database
+    * @return modifier ids to remove
     */
-  private[extra] def rollback(txTarget: Long, boxTarget: Long, _history: ErgoHistory)(implicit segmentTreshold: Int): Unit = {
+  private[extra] def rollback(txTarget: Long, boxTarget: Long, _history: ErgoHistory)(implicit segmentTreshold: Int): Array[ModifierId] = {
 
-    if(txs.last <= txTarget && abs(boxes.last) <= boxTarget) return
+    if((txCount == 0 && boxCount == 0) || // address already rolled back
+       (txs.last <= txTarget && abs(boxes.last) <= boxTarget)) // no rollback needed
+      return Array.empty[ModifierId]
 
     def history: ErgoHistoryReader = _history.getReader
 
@@ -258,8 +261,8 @@ case class IndexedErgoAddress(treeHash: ModifierId,
 
     // Save changes
     _history.historyStorage.insertExtra(Array.empty, toSave.toArray)
-    _history.historyStorage.removeExtra(toRemove.toArray)
 
+    toRemove.toArray
   }
 
   /**
```
