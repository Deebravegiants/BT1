# [?] Merge pull request #1563 from ergoplatform/1558-non-deterministic-test-failure-fixes

## Summary
Severity: Unknown
Chain: Ergo
Component: ergoplatform/ergo
Published: 2022-01-13
Source: https://github.com/ergoplatform/ergo/commit/7769ffdd18bf498d77b40c81b48f551543347ed7
Type: security-commit

## Details
Merge pull request #1563 from ergoplatform/1558-non-deterministic-test-failure-fixes

avoid using global LaunchParameters throughout the codebase

## Patch
### benchmarks/src/test/scala/org/ergoplatform/nodeView/state/TransactionExecutionBenchmark.scala
```diff
@@ -17,13 +17,11 @@ object TransactionExecutionBenchmark extends HistoryTestHelpers with NVBenchmark
 
   val WarmupRuns = 3
 
-  def stateContextWithMaxCost(manualCost: Int): UpcomingStateContext = {
-    val table2: Map[Byte, Int] = Parameters.DefaultParameters + (MaxBlockCostIncrease -> manualCost)
-    val params2 = new Parameters(height = 0,
-      parametersTable = table2,
-      proposedUpdate = ErgoValidationSettingsUpdate.empty)
-    emptyStateContext.copy(currentParameters = params2)(settings)
-  }
+  override val parameters =
+    new Parameters(height = 0,
+      parametersTable = Parameters.DefaultParameters + (MaxBlockCostIncrease -> Int.MaxValue),
+      proposedUpdate = ErgoValidationSettingsUpdate.empty
+    )
 
   def main(args: Array[String]): Unit = {
 
@@ -41,10 +39,9 @@ object TransactionExecutionBenchmark extends HistoryTestHelpers with NVBenchmark
     }.result()
 
     val boxes = bh.boxes
-    val stateContext = stateContextWithMaxCost(Int.MaxValue)
     def bench: Long =
       Utils.time {
-        assert(ErgoState.execTransactions(txs, stateContext)(id => Try(boxes(ByteArrayWrapper(id)))) == Valid(178665000))
+        assert(ErgoState.execTransactions(txs, emptyStateContext)(id => Try(boxes(ByteArrayWrapper(id)))) == Valid(178665000))
       }.toLong
 
     (0 to WarmupRuns).foreach(_ => bench)
```

### benchmarks/src/test/scala/org/ergoplatform/nodeView/state/UtxoStateBenchmark.scala
```diff
@@ -22,7 +22,7 @@ object UtxoStateBenchmark extends HistoryTestHelpers with NVBenchmark {
     val transactionsQty = blocks.flatMap(_.transactions).size
 
     def bench(mods: Seq[ErgoPersistentModifier]): Long = {
-      val state = ErgoState.generateGenesisUtxoState(createTempDir, StateConstants(None, realNetworkSetting))._1
+      val state = ErgoState.generateGenesisUtxoState(createTempDir, StateConstants(None, realNetworkSetting), parameters)._1
       Utils.time {
         mods.foldLeft(state) { case (st, mod) =>
           st.applyModifier(mod).get
```

### build.sbt
```diff
@@ -84,7 +84,7 @@ libraryDependencies ++= Seq(
   "org.scala-lang.modules" %% "scala-async" % "0.9.7" % "test",
   "com.storm-enroute" %% "scalameter" % "0.8.+" % "test",
   "org.scalactic" %% "scalactic" % "3.0.3" % "test",
-  "org.scalatest" %% "scalatest" % "3.1.1" % "test,it",
+  "org.scalatest" %% "scalatest" % "3.2.10" % "test,it",
   "org.scalacheck" %% "scalacheck" % "1.14.+" % "test",
   "org.scalatestplus" %% "scalatestplus-scalacheck" % "3.1.0.0-RC2" % Test,
 
```

### src/it/scala/org/ergoplatform/it/WalletSpec.scala
```diff
@@ -12,7 +12,7 @@ import org.ergoplatform.it.util.RichEither
 import org.ergoplatform.modifiers.mempool.UnsignedErgoTransaction
 import org.ergoplatform.nodeView.wallet.requests.{PaymentRequest, PaymentRequestEncoder, RequestsHolder, RequestsHolderEncoder}
 import org.ergoplatform.nodeView.wallet.{AugWalletTransaction, ErgoWalletServiceImpl}
-import org.ergoplatform.settings.{Args, ErgoSettings, LaunchParameters}
+import org.ergoplatform.settings.{Args, ErgoSettings}
 import org.ergoplatform.utils.{ErgoTestHelpers, WalletTestOps}
 import org.ergoplatform.wallet.interface4j.SecretString
 import org.ergoplatform.wallet.boxes.ErgoBoxSerializer
@@ -71,7 +71,7 @@ class WalletSpec extends AsyncWordSpec with IntegrationSuite with WalletTestOps
   "it should generate unsigned transaction" in {
     import sigmastate.eval._
     val mnemonic = SecretString.create(walletAutoInitConfig.getString("ergo.wallet.testMnemonic"))
-    val prover = new ErgoWalletServiceImpl().buildProverFromMnemonic(mnemonic, None, LaunchParameters)
+    val prover = new ErgoWalletServiceImpl().buildProverFromMnemonic(mnemonic, None, parameters)
     val pk = prover.hdPubKeys.head.key
     val ergoTree = ErgoTree.fromProposition(TrueLeaf)
     val transactionId = ModifierId @@ Base16.encode(Array.fill(32)(5: Byte))
```

### src/main/scala/org/ergoplatform/ErgoApp.scala
```diff
@@ -12,7 +12,7 @@ import org.ergoplatform.mining.ErgoMiner.StartMining
 import org.ergoplatform.network.{ErgoNodeViewSynchronizer, ErgoSyncTracker, ModeFeature}
 import org.ergoplatform.nodeView.history.ErgoSyncInfoMessageSpec
 import org.ergoplatform.nodeView.{ErgoNodeViewRef, ErgoReadersHolderRef}
-import org.ergoplatform.settings.{Args, ErgoSettings, NetworkType}
+import org.ergoplatform.settings.{Args, ErgoSettings, LaunchParameters, NetworkType}
 import scorex.core.api.http._
 import scorex.core.app.ScorexContext
 import scorex.core.network.NetworkController.ReceivableMessages.ShutdownNetwork
@@ -86,7 +86,9 @@ class ErgoApp(args: Args) extends ScorexLogging {
   private val networkControllerRef: ActorRef = NetworkControllerRef(
     "networkController", scorexSettings.network, peerManagerRef, scorexContext)
 
-  private val nodeViewHolderRef: ActorRef = ErgoNodeViewRef(ergoSettings, timeProvider)
+  private val parameters = LaunchParameters
+
+  private val nodeViewHolderRef: ActorRef = ErgoNodeViewRef(ergoSettings, timeProvider, parameters)
 
   private val readersHolderRef: ActorRef = ErgoReadersHolderRef(nodeViewHolderRef)
 
@@ -99,7 +101,7 @@ class ErgoApp(args: Args) extends ScorexLogging {
     }
 
   private val statsCollectorRef: ActorRef =
-    ErgoStatsCollectorRef(readersHolderRef, networkControllerRef, ergoSettings, timeProvider)
+    ErgoStatsCollectorRef(readersHolderRef, networkControllerRef, ergoSettings, timeProvider, parameters)
 
   private val syncTracker = ErgoSyncTracker(actorSystem, scorexSettings.network, timeProvider)
 
```

### src/main/scala/org/ergoplatform/local/ErgoStatsCollector.scala
```diff
@@ -11,7 +11,7 @@ import org.ergoplatform.modifiers.history.header.Header
 import org.ergoplatform.nodeView.ErgoReadersHolder.{GetReaders, Readers}
 import org.ergoplatform.nodeView.history.ErgoHistory
 import org.ergoplatform.nodeView.state.{ErgoStateReader, StateType}
-import org.ergoplatform.settings.{Algos, ErgoSettings, LaunchParameters, Parameters}
+import org.ergoplatform.settings.{Algos, ErgoSettings, Parameters}
 import scorex.core.network.ConnectedPeer
 import scorex.core.network.NetworkController.ReceivableMessages.{GetConnectedPeers, GetPeersStatus}
 import org.ergoplatform.network.ErgoNodeViewSynchronizer.ReceivableMessages._
@@ -29,7 +29,8 @@ import scala.concurrent.duration._
 class ErgoStatsCollector(readersHolder: ActorRef,
                          networkController: ActorRef,
                          settings: ErgoSettings,
-                         timeProvider: NetworkTimeProvider)
+                         timeProvider: NetworkTimeProvider,
+                         parameters: Parameters)
   extends Actor with ScorexLogging {
 
   override def preStart(): Unit = {
@@ -63,7 +64,7 @@ class ErgoStatsCollector(readersHolder: ActorRef,
     launchTime = networkTime(),
     lastIncomingMessageTime = networkTime(),
     None,
-    LaunchParameters)
+    parameters)
 
   override def receive: Receive =
     onConnectedPeers orElse
@@ -195,11 +196,15 @@ object ErgoStatsCollectorRef {
   def props(readersHolder: ActorRef,
             networkController: ActorRef,
             settings: ErgoSettings,
-            timeProvider: NetworkTimeProvider): Props =
-    Props(new ErgoStatsCollector(readersHolder, networkController, settings, timeProvider))
+            timeProvider: NetworkTimeProvider,
+            parameters: Parameters): Props =
+    Props(new ErgoStatsCollector(readersHolder, networkController, settings, timeProvider, parameters))
 
-  def apply(readersHolder: ActorRef, networkController: ActorRef, settings: ErgoSettings, timeProvider: NetworkTimeProvider)
-           (implicit system: ActorSystem): ActorRef =
-    system.actorOf(props(readersHolder, networkController, settings, timeProvider))
+  def apply(readersHolder: ActorRef,
+            networkController: ActorRef,
+            settings: ErgoSettings,
+            timeProvider: NetworkTimeProvider,
+            parameters: Parameters)(implicit system: ActorSystem): ActorRef =
+    system.actorOf(props(readersHolder, networkController, settings, timeProvider, parameters))
 
 }
```

### src/main/scala/org/ergoplatform/nodeView/ErgoNodeViewHolder.scala
```diff
@@ -16,7 +16,7 @@ import org.ergoplatform.nodeView.mempool.ErgoMemPool
 import org.ergoplatform.nodeView.mempool.ErgoMemPool.ProcessingOutcome
 import org.ergoplatform.nodeView.state._
 import org.ergoplatform.nodeView.wallet.ErgoWallet
-import org.ergoplatform.settings.{Algos, Constants, ErgoSettings}
+import org.ergoplatform.settings.{Algos, Constants, ErgoSettings, Parameters}
 import scorex.core._
 import org.ergoplatform.network.ErgoNodeViewSynchronizer.ReceivableMessages._
 import org.ergoplatform.nodeView.ErgoNodeViewHolder.{CurrentView, DownloadRequest}
@@ -42,7 +42,8 @@ import scala.util.{Failure, Success, Try}
   *
   */
 abstract class ErgoNodeViewHolder[State <: ErgoState[State]](settings: ErgoSettings,
-                                                             timeProvider: NetworkTimeProvider)
+                                                             timeProvider: NetworkTimeProvider,
+                                                             parameters: Parameters)
   extends Actor with ScorexLogging with ScorexEncoding with FileUtils {
 
   private implicit lazy val actorSystem: ActorSystem = context.system
@@ -349,7 +350,8 @@ abstract class ErgoNodeViewHolder[State <: ErgoState[State]](settings: ErgoSetti
 
     val wallet = ErgoWallet.readOrGenerate(
       history.getReader.asInstanceOf[ErgoHistoryReader],
-      settings)
+      settings,
+      parameters)
 
     val memPool = ErgoMemPool.empty(settings)
 
@@ -368,12 +370,13 @@ abstract class ErgoNodeViewHolder[State <: ErgoState[State]](settings: ErgoSetti
     log.info("History database read")
     val memPool = ErgoMemPool.empty(settings)
     val constants = StateConstants(Some(self), settings)
-    restoreConsistentState(ErgoState.readOrGenerate(settings, constants).asInstanceOf[State], history) match {
+    restoreConsistentState(ErgoState.readOrGenerate(settings, constants, parameters).asInstanceOf[State], history) match {
       case Success(state) =>
         log.info("State database read, state synchronized")
         val wallet = ErgoWallet.readOrGenerate(
           history.getReader.asInstanceOf[ErgoHistoryReader],
-          settings)
+          settings,
+          parameters)
         log.info("Wallet database read")
         Some((history, state, wallet, memPool))
       case Failure(ex) =>
@@ -456,7 +459,7 @@ abstract class ErgoNodeViewHolder[State <: ErgoState[State]](settings: ErgoSetti
     deleteRecursive(dir)
 
     val constants = StateConstants(Some(self), settings)
-    ErgoState.readOrGenerate(settings, constants)
+    ErgoState.readOrGenerate(settings, constants, parameters)
       .asInstanceOf[State]
       .ensuring(
         state => java.util.Arrays.equals(state.rootHash, settings.chainSettings.genesisStateDigest),
@@ -517,7 +520,7 @@ abstract class ErgoNodeViewHolder[State <: ErgoState[State]](settings: ErgoSetti
       .flatMap { ctx =>
         val recoverVersion = idToVersion(lastHeaders.last.id)
         val recoverRoot = bestFullBlock.header.stateRoot
-        DigestState.recover(recoverVersion, recoverRoot, ctx, stateDir(settings), constants)
+        DigestState.recover(recoverVersion, recoverRoot, ctx, stateDir(settings), constants, parameters)
       }
 
     recoveredStateTry match {
@@ -527,7 +530,7 @@ abstract class ErgoNodeViewHolder[State <: ErgoState[State]](settings: ErgoSetti
       case Failure(exception) => // recover using whole headers chain
         log.warn(s"Failed to recover state from current epoch, using whole chain: ${exception.getMessage}")
         val wholeChain = history.headerChainBack(Int.MaxValue, bestFullBlock.header, _.isGenesis).headers
-        val genesisState = DigestState.create(None, None, stateDir(settings), constants)
+        val genesisState = DigestState.create(None, None, stateDir(settings), constants, parameters)
         wholeChain.foldLeft[Try[DigestState]](Success(genesisState))((acc, m) => acc.flatMap(_.applyModifier(m)))
     }
   }
@@ -618,34 +621,40 @@ object ErgoNodeViewHolder {
 }
 
 private[nodeView] class DigestNodeViewHolder(settings: ErgoSettings,
-                                             timeProvider: NetworkTimeProvider)
-  extends ErgoNodeViewHolder[DigestState](settings, timeProvider)
+                                             timeProvider: NetworkTimeProvider,
+                                             parameters: Parameters)
+  extends ErgoNodeViewHolder[DigestState](settings, timeProvider, parameters)
 
 private[nodeView] class UtxoNodeViewHolder(settings: ErgoSettings,
-                                           timeProvider: NetworkTimeProvider)
-  extends ErgoNodeViewHolder[UtxoState](settings, timeProvider)
+                                           timeProvider: NetworkTimeProvider,
+                                           parameters: Parameters)
+  extends ErgoNodeViewHolder[UtxoState](settings, timeProvider, parameters)
 
 
 
 object ErgoNodeViewRef {
 
   private def digestProps(settings: ErgoSettings,
-                  timeProvider: NetworkTimeProvider): Props =
-    Props.create(classOf[DigestNodeViewHolder], settings, timeProvider)
+                          timeProvider: NetworkTimeProvider,
+                          parameters: Parameters): Props =
+    Props.create(classOf[DigestNodeViewHolder], settings, timeProvider, parameters)
 
   private def utxoProps(settings: ErgoSettings,
-                timeProvider: NetworkTimeProvider): Props =
-    Props.create(classOf[UtxoNodeViewHolder], settings, timeProvider)
+                        timeProvider: NetworkTimeProvider,
+                        parameters: Parameters): Props =
+    Props.create(classOf[UtxoNodeViewHolder], settings, timeProvider, parameters)
 
   def props(settings: ErgoSettings,
-            timeProvider: NetworkTimeProvider): Props =
+            timeProvider: NetworkTimeProvider,
+            parameters: Parameters): Props =
     settings.nodeSettings.stateType match {
-      case StateType.Digest => digestProps(settings, timeProvider)
-      case StateType.Utxo => utxoProps(settings, timeProvider)
+      case StateType.Digest => digestProps(settings, timeProvider, parameters)
+      case StateType.Utxo => utxoProps(settings, timeProvider, parameters)
     }
 
   def apply(settings: ErgoSettings,
-            timeProvider: NetworkTimeProvider)(implicit system: ActorSystem): ActorRef =
-    system.actorOf(props(settings, timeProvider))
+            timeProvider: NetworkTimeProvider,
+            parameters: Parameters)(implicit system: ActorSystem): ActorRef =
+    system.actorOf(props(settings, timeProvider, parameters))
   
 }
```

### src/main/scala/org/ergoplatform/nodeView/state/DigestState.scala
```diff
@@ -26,6 +26,7 @@ import scala.util.{Failure, Success, Try}
 class DigestState protected(override val version: VersionTag,
                             override val rootHash: ADDigest,
                             override val store: LDBVersionedStore,
+                            override val parameters: Parameters,
                             ergoSettings: ErgoSettings)
   extends ErgoState[DigestState]
     with ScorexLogging
@@ -88,7 +89,7 @@ class DigestState protected(override val version: VersionTag,
       store.clean(nodeSettings.keepVersions)
       val rootHash = ADDigest @@ store.get(versionBytes).get
       log.info(s"Rollback to version ${Algos.encoder.encode(version)} with roothash ${Algos.encoder.encode(rootHash)}")
-      new DigestState(version, rootHash, store, ergoSettings)
+      new DigestState(version, rootHash, store, parameters, ergoSettings)
     }
   }
 
@@ -140,7 +141,7 @@ class DigestState protected(override val version: VersionTag,
     val toUpdate = DigestState.metadata(newVersion, newRootHash, newStateContext)
 
     store.update(scorex.core.versionToBytes(newVersion), Seq.empty, toUpdate).map { _ =>
-      new DigestState(newVersion, newRootHash, store, ergoSettings)
+      new DigestState(newVersion, newRootHash, store, parameters, ergoSettings)
     }
   }
 
@@ -155,45 +156,47 @@ object DigestState extends ScorexLogging with ScorexEncoding {
               rootHash: ADDigest,
               stateContext: ErgoStateContext,
               dir: File,
-              constants: StateConstants): Try[DigestState] = {
+              constants: StateConstants,
+              parameters: Parameters): Try[DigestState] = {
     val store = new LDBVersionedStore(dir, keepVersions = constants.keepVersions)
     val toUpdate = DigestState.metadata(version, rootHash, stateContext)
 
     store.update(scorex.core.versionToBytes(version), Seq.empty, toUpdate).map { _ =>
-      new DigestState(version, rootHash, store, constants.settings)
+      new DigestState(version, rootHash, store, parameters, constants.settings)
     }
   }
 
   def create(versionOpt: Option[VersionTag],
              rootHashOpt: Option[ADDigest],
              dir: File,
-             constants: StateConstants): DigestState = {
+             constants: StateConstants,
+             parameters: Parameters): DigestState = {
     val store = new LDBVersionedStore(dir, keepVersions = constants.keepVersions)
     Try {
-      val context = ErgoStateReader.storageStateContext(store, constants)
+      val context = ErgoStateReader.storageStateContext(store, constants, parameters)
       (versionOpt, rootHashOpt) match {
         case (Some(version), Some(rootHash)) =>
           val state = if (store.lastVersionID.map(w => bytesToVersion(w)).contains(version)) {
-            new DigestState(version, rootHash, store, constants.settings)
+            new DigestState(version, rootHash, store, parameters, constants.settings)
           } else {
             val inVersion = store.lastVersionID.map(w => bytesToVersion(w)).getOrElse(version)
-            new DigestState(inVersion, rootHash, store, constants.settings)
+            new DigestState(inVersion, rootHash, store, parameters, constants.settings)
               .update(version, rootHash, context).get //sync store
           }
           state.ensuring(bytesToVersion(store.lastVersionID.get) == version)
         case (None, None) if store.lastVersionID.isEmpty =>
-          ErgoState.generateGenesisDigestState(dir, constants.settings)
+          ErgoState.generateGenesisDigestState(dir, constants.settings, parameters)
         case _ =>
           val version = store.lastVersionID.get
           val rootHash = store.get(version).get
-          new DigestState(bytesToVersion(version), ADDigest @@ rootHash, store, constants.settings)
+          new DigestState(bytesToVersion(version), ADDigest @@ rootHash, store, parameters, constants.settings)
       }
     } match {
       case Success(state) => state
       case Failure(e) =>
         store.close()
         log.warn(s"Failed to create state with ${versionOpt.map(encoder.encode)} and ${rootHashOpt.map(encoder.encode)}", e)
-        ErgoState.generateGenesisDigestState(dir, constants.settings)
+        ErgoState.generateGenesisDigestState(dir, constants.settings, parameters)
     }
   }
 
```

### src/main/scala/org/ergoplatform/nodeView/state/ErgoState.scala
```diff
@@ -11,7 +11,7 @@ import org.ergoplatform.modifiers.mempool.ErgoTransaction
 import org.ergoplatform.modifiers.state.{Insertion, Lookup, Removal, StateChanges}
 import org.ergoplatform.nodeView.history.ErgoHistory
 import org.ergoplatform.settings.ValidationRules._
-import org.ergoplatform.settings.{ChainSettings, Constants, ErgoSettings}
+import org.ergoplatform.settings.{ChainSettings, Constants, ErgoSettings, Parameters}
 import org.ergoplatform.wallet.interpreter.ErgoInterpreter
 import scorex.core.validation.ValidationResult.Valid
 import scorex.core.validation.{ModifierValidator, ValidationResult}
@@ -225,36 +225,38 @@ object ErgoState extends ScorexLogging {
   }
 
   def generateGenesisUtxoState(stateDir: File,
-                               constants: StateConstants): (UtxoState, BoxHolder) = {
+                               constants: StateConstants,
+                               parameters: Parameters): (UtxoState, BoxHolder) = {
 
     log.info("Generating genesis UTXO state")
     val boxes = genesisBoxes(constants.settings.chainSettings)
     val bh = BoxHolder(boxes)
 
-    UtxoState.fromBoxHolder(bh, boxes.headOption, stateDir, constants).ensuring(us => {
+    UtxoState.fromBoxHolder(bh, boxes.headOption, stateDir, constants, parameters).ensuring(us => {
       log.info(s"Genesis UTXO state generated with hex digest ${Base16.encode(us.rootHash)}")
       java.util.Arrays.equals(us.rootHash, constants.settings.chainSettings.genesisStateDigest) && us.version == genesisStateVersion
     }) -> bh
   }
 
-  def generateGenesisDigestState(stateDir: File, settings: ErgoSettings): DigestState = {
+  def generateGenesisDigestState(stateDir: File, settings: ErgoSettings, parameters: Parameters): DigestState = {
     DigestState.create(Some(genesisStateVersion), Some(settings.chainSettings.genesisStateDigest),
-      stateDir, StateConstants(None, settings))
+      stateDir, StateConstants(None, settings), parameters)
   }
 
   val preGenesisStateDigest: ADDigest = ADDigest @@ Array.fill(32)(0: Byte)
 
   lazy val genesisStateVersion: VersionTag = idToVersion(Header.GenesisParentId)
 
   def readOrGenerate(settings: ErgoSettings,
-                     constants: StateConstants): ErgoState[_] = {
+                     constants: StateConstants,
+                     parameters: Parameters): ErgoState[_] = {
     val dir = stateDir(settings)
     dir.mkdirs()
 
     settings.nodeSettings.stateType match {
-      case StateType.Digest => DigestState.create(None, None, dir, constants)
-      case StateType.Utxo if dir.listFiles().nonEmpty => UtxoState.create(dir, constants)
-      case _ => ErgoState.generateGenesisUtxoState(dir, constants)._1
+      case StateType.Digest => DigestState.create(None, None, dir, constants, parameters)
+      case StateType.Utxo if dir.listFiles().nonEmpty => UtxoState.create(dir, constants, parameters)
+      case _ => ErgoState.generateGenesisUtxoState(dir, constants, parameters)._1
     }
   }
 
```

### src/main/scala/org/ergoplatform/nodeView/state/ErgoStateContext.scala
```diff
@@ -296,19 +296,19 @@ class ErgoStateContext(val lastHeaders: Seq[Header],
 
 object ErgoStateContext {
 
-  def empty(constants: StateConstants): ErgoStateContext = {
-    empty(constants.settings.chainSettings.genesisStateDigest, constants.settings)
+  def empty(constants: StateConstants, parameters: Parameters): ErgoStateContext = {
+    empty(constants.settings.chainSettings.genesisStateDigest, constants.settings, parameters)
   }
 
-  def empty(settings: ErgoSettings): ErgoStateContext = {
-    empty(settings.chainSettings.genesisStateDigest, settings)
+  def empty(settings: ErgoSettings, parameters: Parameters): ErgoStateContext = {
+    empty(settings.chainSettings.genesisStateDigest, settings, parameters)
   }
 
   /**
     * Initialize empty state context
     */
-  def empty(genesisStateDigest: ADDigest, settings: ErgoSettings): ErgoStateContext = {
-    new ErgoStateContext(Seq.empty, None, genesisStateDigest, LaunchParameters, ErgoValidationSettings.initial,
+  def empty(genesisStateDigest: ADDigest, settings: ErgoSettings, parameters: Parameters): ErgoStateContext = {
+    new ErgoStateContext(Seq.empty, None, genesisStateDigest, parameters, ErgoValidationSettings.initial,
       VotingData.empty)(settings)
   }
 
```

### src/main/scala/org/ergoplatform/nodeView/state/ErgoStateReader.scala
```diff
@@ -1,7 +1,7 @@
 package org.ergoplatform.nodeView.state
 
 import org.ergoplatform.ErgoBox
-import org.ergoplatform.settings.{Algos, VotingSettings}
+import org.ergoplatform.settings.{Algos, Parameters, VotingSettings}
 import scorex.core.{NodeViewComponent, VersionTag}
 import scorex.crypto.authds.ADDigest
 import scorex.crypto.hash.Digest32
@@ -11,14 +11,15 @@ import scorex.util.ScorexLogging
 trait ErgoStateReader extends NodeViewComponent with ScorexLogging {
 
   def rootHash: ADDigest
+  def parameters: Parameters
   val store: LDBVersionedStore
   val constants: StateConstants
 
   private lazy val chainSettings = constants.settings.chainSettings
 
   protected lazy val votingSettings: VotingSettings = chainSettings.voting
 
-  def stateContext: ErgoStateContext = ErgoStateReader.storageStateContext(store, constants)
+  def stateContext: ErgoStateContext = ErgoStateReader.storageStateContext(store, constants, parameters)
 
   def genesisBoxes: Seq[ErgoBox] = ErgoState.genesisBoxes(chainSettings)
 
@@ -36,10 +37,10 @@ object ErgoStateReader {
 
   val ContextKey: Digest32 = Algos.hash("current state context")
 
-  def storageStateContext(store: LDBVersionedStore, constants: StateConstants): ErgoStateContext = {
+  def storageStateContext(store: LDBVersionedStore, constants: StateConstants, parameters: Parameters): ErgoStateContext = {
     store.get(ErgoStateReader.ContextKey)
       .flatMap(b => ErgoStateContextSerializer(constants.settings).parseBytesTry(b).toOption)
-      .getOrElse(ErgoStateContext.empty(constants))
+      .getOrElse(ErgoStateContext.empty(constants, parameters))
   }
 
 }
```

### src/main/scala/org/ergoplatform/nodeView/state/UtxoState.scala
```diff
@@ -10,7 +10,7 @@ import org.ergoplatform.modifiers.mempool.ErgoTransaction
 import org.ergoplatform.modifiers.{ErgoFullBlock, ErgoPersistentModifier}
 import org.ergoplatform.settings.Algos.HF
 import org.ergoplatform.settings.ValidationRules.{fbDigestIncorrect, fbOperationFailed}
-import org.ergoplatform.settings.Algos
+import org.ergoplatform.settings.{Algos, Parameters}
 import org.ergoplatform.utils.LoggingUtil
 import org.ergoplatform.nodeView.ErgoNodeViewHolder.ReceivableMessages.LocallyGeneratedModifier
 import scorex.core._
@@ -35,7 +35,8 @@ import scala.util.{Failure, Success, Try}
 class UtxoState(override val persistentProver: PersistentBatchAVLProver[Digest32, HF],
                 override val version: VersionTag,
                 override val store: LDBVersionedStore,
-                override val constants: StateConstants)
+                override val constants: StateConstants,
+                override val parameters: Parameters)
   extends ErgoState[UtxoState]
     with TransactionValidation
     with UtxoStateReader
@@ -59,7 +60,7 @@ class UtxoState(override val persistentProver: PersistentBatchAVLProver[Digest32
       case Some(hash) =>
         val rootHash: ADDigest = ADDigest @@ hash
         val rollbackResult = p.rollback(rootHash).map { _ =>
-          new UtxoState(p, version, store, constants)
+          new UtxoState(p, version, store, constants, parameters)
         }
         store.clean(constants.keepVersions)
         rollbackResult
@@ -121,7 +122,7 @@ class UtxoState(override val persistentProver: PersistentBatchAVLProver[Digest32
             }
             log.info(s"Valid modifier with header ${fb.header.encodedId} and emission box " +
               s"${emissionBox.map(e => Algos.encode(e.id))} applied to UtxoState at height ${fb.header.height}")
-            new UtxoState(persistentProver, idToVersion(fb.id), store, constants)
+            new UtxoState(persistentProver, idToVersion(fb.id), store, constants, parameters)
           }
         }
         stateTry.recoverWith[UtxoState] { case e =>
@@ -139,7 +140,7 @@ class UtxoState(override val persistentProver: PersistentBatchAVLProver[Digest32
       //todo: update state context with headers (when snapshot downloading is done), so
       //todo: application of the first full block after the snapshot should have correct state context
       //todo: (in particular, "lastHeaders" field of it)
-      Success(new UtxoState(persistentProver, idToVersion(h.id), this.store, constants))
+      Success(new UtxoState(persistentProver, idToVersion(h.id), this.store, constants, parameters))
 
     case a: Any =>
       log.error(s"Unhandled unknown modifier: $a")
@@ -174,7 +175,7 @@ object UtxoState {
     Seq(idStateDigestIdxElem, stateDigestIdIdxElem, bestVersion, eb, cb)
   }
 
-  def create(dir: File, constants: StateConstants): UtxoState = {
+  def create(dir: File, constants: StateConstants, parameters: Parameters): UtxoState = {
     val store = new LDBVersionedStore(dir, keepVersions = constants.keepVersions)
     val version = store.get(bestVersionKey).map(w => bytesToVersion(w))
       .getOrElse(ErgoState.genesisStateVersion)
@@ -184,7 +185,7 @@ object UtxoState {
       val storage: VersionedLDBAVLStorage[Digest32] = new VersionedLDBAVLStorage(store, np)(Algos.hash)
       PersistentBatchAVLProver.create(bp, storage).get
     }
-    new UtxoState(persistentProver, version, store, constants)
+    new UtxoState(persistentProver, version, store, constants, parameters)
   }
 
   /**
@@ -194,15 +195,16 @@ object UtxoState {
   def fromBoxHolder(bh: BoxHolder,
                     currentEmissionBoxOpt: Option[ErgoBox],
                     dir: File,
-                    constants: StateConstants): UtxoState = {
+                    constants: StateConstants,
+                    parameters: Parameters): UtxoState = {
     val p = new BatchAVLProver[Digest32, HF](keyLength = 32, valueLengthOpt = None)
     bh.sortedBoxes.foreach { b =>
       p.performOneOperation(Insert(b.id, ADValue @@ b.bytes)).ensuring(_.isSuccess)
     }
 
     val store = new LDBVersionedStore(dir, keepVersions = constants.keepVersions)
 
-    val defaultStateContext = ErgoStateContext.empty(constants)
+    val defaultStateContext = ErgoStateContext.empty(constants, parameters)
     val np = NodeParameters(keySize = 32, valueSize = None, labelSize = 32)
     val storage: VersionedLDBAVLStorage[Digest32] = new VersionedLDBAVLStorage(store, np)(Algos.hash)
     val persistentProver = PersistentBatchAVLProver.create(
@@ -212,7 +214,7 @@ object UtxoState {
       paranoidChecks = true
     ).get
 
-    new UtxoState(persistentProver, ErgoState.genesisStateVersion, store, constants)
+    new UtxoState(persistentProver, ErgoState.genesisStateVersion, store, constants, parameters)
   }
 
 }
```
