# [?] race condition fix

## Summary
Severity: Unknown
Chain: Ergo
Component: ergoplatform/ergo
Published: 2021-01-23
Source: https://github.com/ergoplatform/ergo/commit/01aa5f4ea67bbfe7b0d630da3b5881ecd5e7da39
Type: security-commit

## Details
race condition fix

## Patch
### src/main/scala/org/ergoplatform/mining/ErgoMiner.scala
```diff
@@ -74,6 +74,9 @@ class ErgoMiner(ergoSettings: ErgoSettings,
   // flag which is set once when mining started (first block candidate is formed)
   private var isMining = false
 
+  // Flag which is set when a future with block candidate generation is running
+  private var candidateGenerating: Boolean = false
+
   // cached block candidate
   private var candidateOpt: Option[CandidateCache] = None
 
@@ -207,7 +210,6 @@ class ErgoMiner(ergoSettings: ErgoSettings,
   override def receive: Receive =
     receiveSemanticallySuccessfulModifier orElse
       startMining orElse
-      onReaders orElse
       keysManagement orElse
       mining orElse
       queryWallet orElse
@@ -268,35 +270,34 @@ class ErgoMiner(ergoSettings: ErgoSettings,
     }
   }
 
-  // We produce block candidate on getting readers for node's view from NodeViewHolder
-  private def onReaders: Receive = {
-    // Miner's node can produce block candidate only if it is working in the UTXO regime
-    case Readers(h, s: UtxoStateReader, m, _) =>
-     generateCandidate(h, m, s, None)
-  }
-
   private def mining: Receive = {
-    case PrepareCandidate(_) if !ergoSettings.nodeSettings.mining =>
+    case PrepareCandidate(_, _) if !ergoSettings.nodeSettings.mining =>
       sender() ! Future.failed(new Exception("Candidate creation is not supported when mining is disabled"))
 
-    // Send cached candidate if it is available and (non-empty) list of transactions to include hasn't been changed
-    case PrepareCandidate(txsToInclude) =>
-      val candBlockFuture = if (cachedFor(txsToInclude)) {
-        candidateOpt
-          .map(_.externalVersion)
-          .fold[Future[WorkMessage]](
-          Future.failed(new Exception("Failed to create candidate")))(Future.successful)
+    case PrepareCandidate(txsToInclude, reply) =>
+      val candF: Future[CandidateCache] = if(candidateGenerating){
+        Future.failed(new Exception("Candidate generation is in progress"))
       } else {
-        log.info("Generating new candidate requested by external miner")
-        val readersR = (readersHolderRef ? GetReaders).mapTo[Readers]
-        readersR.flatMap {
-          case Readers(h, s: UtxoStateReader, m, _) =>
-            Future.fromTry(generateCandidate(h, m, s, Some(txsToInclude)).map(_.externalVersion))
-          case _ =>
-            Future.failed(new Exception("Invalid readers state, mining is possible in UTXO mode only"))
+        candidateGenerating = true
+        val f = if (cachedFor(txsToInclude)) {
+          candidateOpt.fold[Future[CandidateCache]](
+            Future.failed(new Exception("Failed to create candidate")))(Future.successful)
+        } else {
+          log.info("Generating new candidate requested by external miner")
+          val readersR = (readersHolderRef ? GetReaders).mapTo[Readers]
+          readersR.flatMap {
+            case Readers(h, s: UtxoStateReader, m, _) =>
+              Future.fromTry(generateCandidate(h, m, s, Some(txsToInclude)))
+            case _ =>
+              Future.failed(new Exception("Invalid readers state, mining is possible in UTXO mode only"))
+          }
         }
+        f.onComplete(_ => candidateGenerating = false)
+        f
+      }
+      if (reply) {
+        sender() ! candF.map(_.externalVersion)
       }
-      sender() ! candBlockFuture
 
     // solution found externally (by e.g. GPU miner)
     case preSolution: AutolykosSolution =>
@@ -453,7 +454,7 @@ class ErgoMiner(ergoSettings: ErgoSettings,
 
   def requestCandidate(): Unit = {
     log.info("Requesting candidate")
-    readersHolderRef ! GetReaders
+    self ! PrepareCandidate(candidateOpt.map(_.txsToInclude).getOrElse(Seq.empty), reply = false)
   }
 
   // Start internal miner's threads. Called once per block candidate.
@@ -694,7 +695,7 @@ object ErgoMiner extends ScorexLogging {
 
   case object QueryWallet
 
-  case class PrepareCandidate(toInclude: Seq[ErgoTransaction])
+  case class PrepareCandidate(toInclude: Seq[ErgoTransaction], reply: Boolean = true)
 
   case object ReadMinerPk
 
```

### src/test/scala/org/ergoplatform/utils/Stubs.scala
```diff
@@ -97,7 +97,9 @@ trait Stubs extends ErgoGenerators with ErgoTestHelpers with ChainGenerator with
 
   class MinerStub extends Actor {
     def receive: Receive = {
-      case ErgoMiner.PrepareCandidate(_) => sender() ! Future.successful(externalCandidateBlock)
+      case ErgoMiner.PrepareCandidate(_, reply) => if (reply) {
+        sender() ! Future.successful(externalCandidateBlock)
+      }
       case _: AutolykosSolution => sender() ! Future.successful(())
       case ErgoMiner.ReadMinerPk => sender() ! Some(pk)
     }
```
