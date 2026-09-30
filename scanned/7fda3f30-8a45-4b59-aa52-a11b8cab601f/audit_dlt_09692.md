# [?] 1588 actor message queue overflow fix

## Summary
Severity: Unknown
Chain: Ergo
Component: ergoplatform/ergo
Published: 2022-01-20
Source: https://github.com/ergoplatform/ergo/commit/80a0e3db260029a94198d32a5009ecf0ea1d4db4
Type: security-commit

## Details
1588 actor message queue overflow fix

## Patch
### benchmarks/src/test/scala/org/ergoplatform/nodeView/state/UtxoStateBenchmark.scala
```diff
@@ -22,10 +22,10 @@ object UtxoStateBenchmark extends HistoryTestHelpers with NVBenchmark {
     val transactionsQty = blocks.flatMap(_.transactions).size
 
     def bench(mods: Seq[ErgoPersistentModifier]): Long = {
-      val state = ErgoState.generateGenesisUtxoState(createTempDir, StateConstants(None, realNetworkSetting), parameters)._1
+      val state = ErgoState.generateGenesisUtxoState(createTempDir, StateConstants(realNetworkSetting), parameters)._1
       Utils.time {
         mods.foldLeft(state) { case (st, mod) =>
-          st.applyModifier(mod).get
+          st.applyModifier(mod)(_ => ()).get
         }
       }.toLong
     }
```

### src/main/scala/org/ergoplatform/nodeView/ErgoNodeViewHolder.scala
```diff
@@ -229,7 +229,7 @@ abstract class ErgoNodeViewHolder[State <: ErgoState[State]](settings: ErgoSetti
         f
       case (success@Success(updateInfo), modToApply) =>
         if (updateInfo.failedMod.isEmpty) {
-          updateInfo.state.applyModifier(modToApply) match {
+          updateInfo.state.applyModifier(modToApply)(lm => pmodModify(lm.pmod, local = true)) match {
             case Success(stateAfterApply) =>
               history.reportModifierIsValid(modToApply).map { newHis =>
                 context.system.eventStream.publish(SemanticallySuccessfulModifier(modToApply))
@@ -376,7 +376,7 @@ abstract class ErgoNodeViewHolder[State <: ErgoState[State]](settings: ErgoSetti
     val history = ErgoHistory.readOrGenerate(settings, timeProvider)
     log.info("History database read")
     val memPool = ErgoMemPool.empty(settings)
-    val constants = StateConstants(Some(self), settings)
+    val constants = StateConstants(settings)
     restoreConsistentState(ErgoState.readOrGenerate(settings, constants, parameters).asInstanceOf[State], history) match {
       case Success(state) =>
         log.info("State database read, state synchronized")
@@ -468,7 +468,7 @@ abstract class ErgoNodeViewHolder[State <: ErgoState[State]](settings: ErgoSetti
     val dir = stateDir(settings)
     deleteRecursive(dir)
 
-    val constants = StateConstants(Some(self), settings)
+    val constants = StateConstants(settings)
     ErgoState.readOrGenerate(settings, constants, parameters)
       .asInstanceOf[State]
       .ensuring(
@@ -505,7 +505,7 @@ abstract class ErgoNodeViewHolder[State <: ErgoState[State]](settings: ErgoSetti
         }
         toApply.foldLeft[Try[State]](Success(initState)) { case (acc, m) =>
           log.info(s"Applying modifier during node start-up to restore consistent state: ${m.id}")
-          acc.flatMap(_.applyModifier(m))
+          acc.flatMap(_.applyModifier(m)(lm => pmodModify(lm.pmod, local = true)))
         }
     }
   }
@@ -514,7 +514,7 @@ abstract class ErgoNodeViewHolder[State <: ErgoState[State]](settings: ErgoSetti
     * Recovers digest state from history.
     */
   private def recoverDigestState(bestFullBlock: ErgoFullBlock, history: ErgoHistory): Try[DigestState] = {
-    val constants = StateConstants(Some(self), settings)
+    val constants = StateConstants(settings)
     val votingLength = settings.chainSettings.voting.votingLength
     val bestHeight = bestFullBlock.header.height
     val newEpochHeadersQty = bestHeight % votingLength // how many blocks current epoch lasts
@@ -536,12 +536,16 @@ abstract class ErgoNodeViewHolder[State <: ErgoState[State]](settings: ErgoSetti
     recoveredStateTry match {
       case Success(state) =>
         log.info("Recovering state using current epoch")
-        chainToApply.foldLeft[Try[DigestState]](Success(state))((acc, m) => acc.flatMap(_.applyModifier(m)))
+        chainToApply.foldLeft[Try[DigestState]](Success(state)) { case (acc, m) =>
+          acc.flatMap(_.applyModifier(m)(lm => pmodModify(lm.pmod, local = true)))
+        }
       case Failure(exception) => // recover using whole headers chain
         log.warn(s"Failed to recover state from current epoch, using whole chain: ${exception.getMessage}")
         val wholeChain = history.headerChainBack(Int.MaxValue, bestFullBlock.header, _.isGenesis).headers
         val genesisState = DigestState.create(None, None, stateDir(settings), constants, parameters)
-        wholeChain.foldLeft[Try[DigestState]](Success(genesisState))((acc, m) => acc.flatMap(_.applyModifier(m)))
+        wholeChain.foldLeft[Try[DigestState]](Success(genesisState)) { case (acc, m) =>
+          acc.flatMap(_.applyModifier(m)(lm => pmodModify(lm.pmod, local = true)))
+        }
     }
   }
 
```

### src/main/scala/org/ergoplatform/nodeView/state/DigestState.scala
```diff
@@ -1,12 +1,12 @@
 package org.ergoplatform.nodeView.state
 
 import java.io.File
-
 import org.ergoplatform.ErgoBox
 import org.ergoplatform.modifiers.history.ADProofs
 import org.ergoplatform.modifiers.history.header.Header
 import org.ergoplatform.modifiers.mempool.ErgoTransaction
 import org.ergoplatform.modifiers.{ErgoFullBlock, ErgoPersistentModifier}
+import org.ergoplatform.nodeView.ErgoNodeViewHolder.ReceivableMessages.LocallyGeneratedModifier
 import org.ergoplatform.nodeView.state.ErgoState.ModifierProcessing
 import org.ergoplatform.settings._
 import org.ergoplatform.utils.LoggingUtil
@@ -35,7 +35,7 @@ class DigestState protected(override val version: VersionTag,
   store.lastVersionID
     .foreach(id => require(version == bytesToVersion(id), "version should always be equal to store.lastVersionID"))
 
-  override val constants: StateConstants = StateConstants(None, ergoSettings)
+  override val constants: StateConstants = StateConstants(ergoSettings)
 
   private lazy val nodeSettings = ergoSettings.nodeSettings
 
@@ -78,7 +78,7 @@ class DigestState protected(override val version: VersionTag,
       Failure(new Exception(s"Modifier not validated: $a"))
   }
 
-  override def applyModifier(mod: ErgoPersistentModifier): Try[DigestState] =
+  override def applyModifier(mod: ErgoPersistentModifier)(generate: LocallyGeneratedModifier => Unit): Try[DigestState] =
     (processFullBlock orElse processHeader orElse processOther) (mod)
 
   @SuppressWarnings(Array("OptionGet"))
```

### src/main/scala/org/ergoplatform/nodeView/state/ErgoState.scala
```diff
@@ -9,6 +9,7 @@ import org.ergoplatform.modifiers.ErgoPersistentModifier
 import org.ergoplatform.modifiers.history.header.Header
 import org.ergoplatform.modifiers.mempool.ErgoTransaction
 import org.ergoplatform.modifiers.state.{Insertion, Lookup, Removal, StateChanges}
+import org.ergoplatform.nodeView.ErgoNodeViewHolder.ReceivableMessages.LocallyGeneratedModifier
 import org.ergoplatform.nodeView.history.ErgoHistory
 import org.ergoplatform.settings.ValidationRules._
 import org.ergoplatform.settings.{ChainSettings, Constants, ErgoSettings, Parameters}
@@ -41,7 +42,13 @@ trait ErgoState[IState <: ErgoState[IState]] extends ErgoStateReader {
 
   self: IState =>
 
-  def applyModifier(mod: ErgoPersistentModifier): Try[IState]
+  /**
+    *
+    * @param mod modifire to apply to the state
+    * @param generate function that handles newly created modifier as a result of application the current one
+    * @return new State
+    */
+  def applyModifier(mod: ErgoPersistentModifier)(generate: LocallyGeneratedModifier => Unit): Try[IState]
 
   def rollbackTo(version: VersionTag): Try[IState]
 
@@ -240,7 +247,7 @@ object ErgoState extends ScorexLogging {
 
   def generateGenesisDigestState(stateDir: File, settings: ErgoSettings, parameters: Parameters): DigestState = {
     DigestState.create(Some(genesisStateVersion), Some(settings.chainSettings.genesisStateDigest),
-      stateDir, StateConstants(None, settings), parameters)
+      stateDir, StateConstants(settings), parameters)
   }
 
   val preGenesisStateDigest: ADDigest = ADDigest @@ Array.fill(32)(0: Byte)
```

### src/main/scala/org/ergoplatform/nodeView/state/StateConstants.scala
```diff
@@ -1,16 +1,14 @@
 package org.ergoplatform.nodeView.state
 
-import akka.actor.ActorRef
 import org.ergoplatform.settings.{ErgoSettings, VotingSettings}
 import scorex.crypto.authds.ADDigest
 
 /**
   * Constants that do not change with state version changes
   *
-  * @param nodeViewHolderRef - actor ref of node view holder
   * @param settings          - node settings
   */
-case class StateConstants(nodeViewHolderRef: Option[ActorRef], settings: ErgoSettings) {
+case class StateConstants(settings: ErgoSettings) {
 
   lazy val keepVersions: Int = settings.nodeSettings.keepVersions
   lazy val votingSettings: VotingSettings = settings.chainSettings.voting
```

### src/main/scala/org/ergoplatform/nodeView/state/UtxoState.scala
```diff
@@ -46,11 +46,6 @@ class UtxoState(override val persistentProver: PersistentBatchAVLProver[Digest32
     persistentProver.digest
   }
 
-  private def onAdProofGenerated(proof: ADProofs): Unit = {
-    if (constants.nodeViewHolderRef.isEmpty) log.warn("Got proof while nodeViewHolderRef is empty")
-    constants.nodeViewHolderRef.foreach(h => h ! LocallyGeneratedModifier(proof))
-  }
-
   import UtxoState.metadata
 
   override def rollbackTo(version: VersionTag): Try[UtxoState] = persistentProver.synchronized {
@@ -96,7 +91,7 @@ class UtxoState(override val persistentProver: PersistentBatchAVLProver[Digest32
     }
   }
 
-  override def applyModifier(mod: ErgoPersistentModifier): Try[UtxoState] = mod match {
+  override def applyModifier(mod: ErgoPersistentModifier)(generate: LocallyGeneratedModifier => Unit): Try[UtxoState] = mod match {
     case fb: ErgoFullBlock =>
       persistentProver.synchronized {
         val height = fb.header.height
@@ -111,7 +106,9 @@ class UtxoState(override val persistentProver: PersistentBatchAVLProver[Digest32
             val meta = metadata(idToVersion(fb.id), fb.header.stateRoot, emissionBox, newStateContext)
             val proofBytes = persistentProver.generateProofAndUpdateStorage(meta)
             val proofHash = ADProofs.proofDigest(proofBytes)
-            if (fb.adProofs.isEmpty) onAdProofGenerated(ADProofs(fb.header.id, proofBytes))
+            if (fb.adProofs.isEmpty) {
+              generate(LocallyGeneratedModifier(ADProofs(fb.header.id, proofBytes)))
+            }
 
             if (!store.get(scorex.core.idToBytes(fb.id)).exists(w => java.util.Arrays.equals(w, fb.header.stateRoot))) {
               throw new Error("Storage kept roothash is not equal to the declared one")
```

### src/test/scala/org/ergoplatform/local/MempoolAuditorSpec.scala
```diff
@@ -43,9 +43,12 @@ class MempoolAuditorSpec extends AnyFlatSpec with NodeViewTestOps with ErgoTestH
     val testProbe = new TestProbe(actorSystem)
     actorSystem.eventStream.subscribe(testProbe.ref, newTx)
 
-    val (us, bh) = createUtxoState(parameters, Some(nodeViewHolderRef))
+    val (us, bh) = createUtxoState(parameters)
     val genesis = validFullBlock(parentOpt = None, us, bh)
-    val wusAfterGenesis = WrappedUtxoState(us, bh, stateConstants, parameters).applyModifier(genesis).get
+    val wusAfterGenesis =
+      WrappedUtxoState(us, bh, stateConstants, parameters).applyModifier(genesis) { mod =>
+        nodeViewHolderRef ! mod
+      } .get
 
     applyBlock(genesis) shouldBe 'success
     getRootHash shouldBe Algos.encode(wusAfterGenesis.rootHash)
@@ -88,11 +91,11 @@ class MempoolAuditorSpec extends AnyFlatSpec with NodeViewTestOps with ErgoTestH
 
   it should "rebroadcast transactions correctly" in {
 
-    val (us0, bh0) = createUtxoState(parameters, None)
+    val (us0, bh0) = createUtxoState(parameters)
     val (txs0, bh1) = validTransactionsFromBoxHolder(bh0)
     val b1 = validFullBlock(None, us0, txs0)
 
-    val us = us0.applyModifier(b1).get
+    val us = us0.applyModifier(b1)(_ => ()).get
 
     val bxs = bh1.boxes.values.toList.filter(_.proposition != genesisEmissionBox.proposition)
     val txs = validTransactionsFromBoxes(200000, bxs, new RandomWrapper)._1
```

### src/test/scala/org/ergoplatform/mining/CandidateGeneratorPropSpec.scala
```diff
@@ -67,8 +67,8 @@ class CandidateGeneratorPropSpec extends ErgoPropertyTest {
       defaultMinerPk
     )
 
-    us.applyModifier(validFullBlock(None, us, incorrectTxs)) shouldBe 'failure
-    us.applyModifier(validFullBlock(None, us, txs)) shouldBe 'success
+    us.applyModifier(validFullBlock(None, us, incorrectTxs))(_ => ()) shouldBe 'failure
+    us.applyModifier(validFullBlock(None, us, txs))(_ => ()) shouldBe 'success
   }
 
   property("collect reward from transaction fees only") {
@@ -93,8 +93,8 @@ class CandidateGeneratorPropSpec extends ErgoPropertyTest {
       defaultMinerPk
     )
 
-    us.applyModifier(validFullBlock(None, us, blockTx +: incorrect)) shouldBe 'failure
-    us.applyModifier(validFullBlock(None, us, blockTx +: txs)) shouldBe 'success
+    us.applyModifier(validFullBlock(None, us, blockTx +: incorrect))(_ => ()) shouldBe 'failure
+    us.applyModifier(validFullBlock(None, us, blockTx +: txs))(_ => ()) shouldBe 'success
   }
 
   property("filter out double spend txs") {
@@ -215,7 +215,7 @@ class CandidateGeneratorPropSpec extends ErgoPropertyTest {
       .toSeq
     val block = validFullBlock(None, us, blockTx +: txs)
 
-    us = us.applyModifier(block).get
+    us = us.applyModifier(block)(_ => ()).get
 
     val blockTx2 =
       validTransactionFromBoxes(txBoxes(1), outputsProposition = feeProposition)
@@ -227,9 +227,9 @@ class CandidateGeneratorPropSpec extends ErgoPropertyTest {
     val invalidBlock2 =
       validFullBlock(Some(block), us, IndexedSeq(earlySpendingTx, blockTx2))
 
-    us.applyModifier(invalidBlock2) shouldBe 'failure
+    us.applyModifier(invalidBlock2)(_ => ()) shouldBe 'failure
 
-    us = us.applyModifier(block2).get
+    us = us.applyModifier(block2)(_ => ()).get
 
     val earlySpendingTx2 =
       validTransactionFromBoxes(txs.head.outputs, stateCtxOpt = Some(us.stateContext))
@@ -238,7 +238,7 @@ class CandidateGeneratorPropSpec extends ErgoPropertyTest {
       validTransactionFromBoxes(txBoxes(2), outputsProposition = feeProposition)
     val block3 = validFullBlock(Some(block2), us, IndexedSeq(earlySpendingTx2, blockTx3))
 
-    us.applyModifier(block3) shouldBe 'success
+    us.applyModifier(block3)(_ => ()) shouldBe 'success
   }
 
   property("collect reward from both emission box and fees") {
```

### src/test/scala/org/ergoplatform/nodeView/mempool/ErgoMemPoolSpec.scala
```diff
@@ -19,7 +19,7 @@ class ErgoMemPoolSpec extends AnyFlatSpec
   it should "accept valid transaction" in {
     val (us, bh) = createUtxoState(parameters)
     val genesis = validFullBlock(None, us, bh)
-    val wus = WrappedUtxoState(us, bh, stateConstants, parameters).applyModifier(genesis).get
+    val wus = WrappedUtxoState(us, bh, stateConstants, parameters).applyModifier(genesis)(_ => ()).get
     val txs = validTransactionsFromUtxoState(wus)
     val pool0 = ErgoMemPool.empty(settings)
     val poolAfter = txs.foldLeft(pool0) { case (pool, tx) =>
@@ -41,7 +41,7 @@ class ErgoMemPoolSpec extends AnyFlatSpec
   it should "decline already contained transaction" in {
     val (us, bh) = createUtxoState(parameters)
     val genesis = validFullBlock(None, us, bh)
-    val wus = WrappedUtxoState(us, bh, stateConstants, parameters).applyModifier(genesis).get
+    val wus = WrappedUtxoState(us, bh, stateConstants, parameters).applyModifier(genesis)(_ => ()).get
     val txs = validTransactionsFromUtxoState(wus)
     var pool = ErgoMemPool.empty(settings)
     txs.foreach { tx =>
@@ -57,7 +57,7 @@ class ErgoMemPoolSpec extends AnyFlatSpec
       whenever(n1 != n2) {
         val (us, bh) = createUtxoState(extendedParameters)
         val genesis = validFullBlock(None, us, bh)
-        val wus = WrappedUtxoState(us, bh, stateConstants, extendedParameters).applyModifier(genesis).get
+        val wus = WrappedUtxoState(us, bh, stateConstants, extendedParameters).applyModifier(genesis)(_ => ()).get
 
         val feeProp = settings.chainSettings.monetary.feeProposition
         val inputBox = wus.takeBoxes(1).head
@@ -113,7 +113,7 @@ class ErgoMemPoolSpec extends AnyFlatSpec
   it should "decline transactions not meeting min fee" in {
     val (us, bh) = createUtxoState(parameters)
     val genesis = validFullBlock(None, us, bh)
-    val wus = WrappedUtxoState(us, bh, stateConstants, parameters).applyModifier(genesis).get
+    val wus = WrappedUtxoState(us, bh, stateConstants, parameters).applyModifier(genesis)(_ => ()).get
     val txs = validTransactionsFromUtxoState(wus)
 
     val maxSettings = settings.copy(nodeSettings = settings.nodeSettings.copy(minimalFeeAmount = Long.MaxValue))
@@ -174,7 +174,7 @@ class ErgoMemPoolSpec extends AnyFlatSpec
   it should "Accept output of pooled transactions" in {
     val (us, bh) = createUtxoState(parameters)
     val genesis = validFullBlock(None, us, bh)
-    val wus = WrappedUtxoState(us, bh, stateConstants, parameters).applyModifier(genesis).get
+    val wus = WrappedUtxoState(us, bh, stateConstants, parameters).applyModifier(genesis)(_ => ()).get
     val txs = validTransactionsFromUtxoState(wus)
     var pool = ErgoMemPool.empty(settings)
     txs.foreach { tx =>
@@ -192,7 +192,7 @@ class ErgoMemPoolSpec extends AnyFlatSpec
   it should "consider families for replacement policy" in {
     val (us, bh) = createUtxoState(parameters)
     val genesis = validFullBlock(None, us, bh)
-    val wus = WrappedUtxoState(us, bh, stateConstants, parameters).applyModifier(genesis).get
+    val wus = WrappedUtxoState(us, bh, stateConstants, parameters).applyModifier(genesis)(_ => ()).get
     var txs = validTransactionsFromUtxoState(wus)
     val family_depth = 10
     val limitedPoolSettings = settings.copy(nodeSettings = settings.nodeSettings.copy(mempoolCapacity = (family_depth + 1) * txs.size))
@@ -222,7 +222,7 @@ class ErgoMemPoolSpec extends AnyFlatSpec
   it should "correctly remove transaction from pool and rebuild families" in {
     val (us, bh) = createUtxoState(parameters)
     val genesis = validFullBlock(None, us, bh)
-    val wus = WrappedUtxoState(us, bh, stateConstants, parameters).applyModifier(genesis).get
+    val wus = WrappedUtxoState(us, bh, stateConstants, parameters).applyModifier(genesis)(_ => ()).get
     var txs = validTransactionsFromUtxoState(wus)
     var allTxs = txs
     val family_depth = 10
@@ -255,7 +255,7 @@ class ErgoMemPoolSpec extends AnyFlatSpec
 
     val (us, bh) = createUtxoState(parameters)
     val genesis = validFullBlock(None, us, bh)
-    val wus = WrappedUtxoState(us, bh, stateConstants, parameters).applyModifier(genesis).get
+    val wus = WrappedUtxoState(us, bh, stateConstants, parameters).applyModifier(genesis)(_ => ()).get
     var txs = validTransactionsFromUtxoState(wus)
     val family_depth = 10
     val limitedPoolSettings = settings.copy(nodeSettings = settings.nodeSettings.copy(mempoolCapacity = (family_depth + 1) * txs.size))
@@ -296,7 +296,7 @@ class ErgoMemPoolSpec extends AnyFlatSpec
   it should "add removed transaction to mempool statistics" in {
     val (us, bh) = createUtxoState(parameters)
     val genesis = validFullBlock(None, us, bh)
-    val wus = WrappedUtxoState(us, bh, stateConstants, parameters).applyModifier(genesis).get
+    val wus = WrappedUtxoState(us, bh, stateConstants, parameters).applyModifier(genesis)(_ => ()).get
     var txs = validTransactionsFromUtxoState(wus)
     var allTxs = txs
     val family_depth = 10
```

### src/test/scala/org/ergoplatform/nodeView/mempool/ScriptsSpec.scala
```diff
@@ -76,6 +76,6 @@ class ScriptsSpec extends ErgoPropertyTest {
       assert(us.boxById(boxId).isDefined, s"Box ${Algos.encode(boxId)} missed")
     }
     val block = validFullBlock(None, us, tx, Some(1234L))
-    us.applyModifier(block)
+    us.applyModifier(block)(_ => ())
   }
 }
```

### src/test/scala/org/ergoplatform/nodeView/state/DigestStateSpecification.scala
```diff
@@ -24,7 +24,7 @@ class DigestStateSpecification extends ErgoPropertyTest {
       val fb = validFullBlock(parentOpt = None, us, bh)
       val dir2 = createTempDir
       val ds = DigestState.create(Some(us.version), Some(us.rootHash), dir2, stateConstants, parameters)
-      ds.applyModifier(fb) shouldBe 'success
+      ds.applyModifier(fb)(_ => ()) shouldBe 'success
       ds.close()
 
       val state = DigestState.create(None, None, dir2, stateConstants, parameters)
@@ -42,8 +42,8 @@ class DigestStateSpecification extends ErgoPropertyTest {
       val blBh = validFullBlockWithBoxHolder(parentOpt, us, bh, new RandomWrapper(Some(seed)))
       val block = blBh._1
       bh = blBh._2
-      ds = ds.applyModifier(block).get
-      us = us.applyModifier(block).get
+      ds = ds.applyModifier(block)(_ => ()).get
+      us = us.applyModifier(block)(_ => ()).get
       parentOpt = Some(block)
     }
   }
@@ -64,14 +64,14 @@ class DigestStateSpecification extends ErgoPropertyTest {
       block.blockTransactions.transactions.exists(_.dataInputs.nonEmpty) shouldBe true
 
       val ds = createDigestState(us.version, us.rootHash, parameters)
-      ds.applyModifier(block) shouldBe 'success
+      ds.applyModifier(block)(_ => ()) shouldBe 'success
     }
   }
 
   property("applyModifier() - invalid block") {
     forAll(invalidErgoFullBlockGen) { b =>
       val state = createDigestState(emptyVersion, emptyAdDigest, parameters)
-      state.applyModifier(b).isFailure shouldBe true
+      state.applyModifier(b)(_ => ()).isFailure shouldBe true
     }
   }
 
@@ -86,7 +86,7 @@ class DigestStateSpecification extends ErgoPropertyTest {
 
       ds.rollbackVersions.size shouldEqual 1
 
-      val ds2 = ds.applyModifier(block).get
+      val ds2 = ds.applyModifier(block)(_ => ()).get
 
       ds2.rollbackVersions.size shouldEqual 2
 
@@ -99,7 +99,7 @@ class DigestStateSpecification extends ErgoPropertyTest {
 
       ds3.stateContext.lastHeaders.size shouldEqual 0
 
-      ds3.applyModifier(block).get.rootHash shouldBe ds2.rootHash
+      ds3.applyModifier(block)(_ => ()).get.rootHash shouldBe ds2.rootHash
     }
   }
 
```

### src/test/scala/org/ergoplatform/nodeView/state/ErgoStateSpecification.scala
```diff
@@ -32,11 +32,11 @@ class ErgoStateSpecification extends ErgoPropertyTest {
       val bt = BlockTransactions(dsHeader.id, version, dsTxs)
       val doubleSpendBlock = ErgoFullBlock(dsHeader, bt, validBlock.extension, validBlock.adProofs)
 
-      us.applyModifier(doubleSpendBlock) shouldBe 'failure
-      us.applyModifier(validBlock) shouldBe 'success
+      us.applyModifier(doubleSpendBlock)(_ => ()) shouldBe 'failure
+      us.applyModifier(validBlock)(_ => ()) shouldBe 'success
 
-      ds.applyModifier(doubleSpendBlock) shouldBe 'failure
-      ds.applyModifier(validBlock) shouldBe 'success
+      ds.applyModifier(doubleSpendBlock)(_ => ()) shouldBe 'failure
+      ds.applyModifier(validBlock)(_ => ()) shouldBe 'success
     }
   }
 
@@ -59,8 +59,8 @@ class ErgoStateSpecification extends ErgoPropertyTest {
       val blBh = validFullBlockWithBoxHolder(lastBlocks.headOption, us, bh, new RandomWrapper(Some(seed)))
       val block = blBh._1
       bh = blBh._2
-      ds = ds.applyModifier(block).get
-      us = us.applyModifier(block).get
+      ds = ds.applyModifier(block)(_ => ()).get
+      us = us.applyModifier(block)(_ => ()).get
       lastBlocks = block +: lastBlocks
       requireEqualStateContexts(us.stateContext, ds.stateContext, lastBlocks.map(_.header))
     }
@@ -83,7 +83,7 @@ class ErgoStateSpecification extends ErgoPropertyTest {
       val block = blBh._1
       parentOpt = Some(block)
       bh = blBh._2
-      us = us.applyModifier(block).get
+      us = us.applyModifier(block)(_ => ()).get
 
       val changes1 = ErgoState.boxChanges(block.transactions)
       val changes2 = ErgoState.boxChanges(block.transactions)
```
