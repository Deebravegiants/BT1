# [?] NODE-2031: Fix UTX race condition (#2881)

## Summary
Severity: Unknown
Chain: Waves
Component: wavesplatform/Waves
Published: 2020-01-20
Source: https://github.com/wavesplatform/Waves/commit/26b35766ccb37cc886f72a9920f000828ec0a2a9
Type: security-commit

## Details
NODE-2031: Fix UTX race condition (#2881)

## Patch
### node/src/main/scala/com/wavesplatform/utx/UtxPoolImpl.scala
```diff
@@ -28,8 +28,8 @@ import com.wavesplatform.transaction.transfer._
 import com.wavesplatform.utils.{LoggerFacade, Schedulers, ScorexLogging, Time}
 import kamon.Kamon
 import kamon.metric.MeasurementUnit
+import monix.execution.atomic.AtomicBoolean
 import monix.execution.schedulers.SchedulerService
-import monix.execution.{AsyncQueue, CancelableFuture}
 import monix.reactive.Observer
 import org.slf4j.LoggerFactory
 
@@ -57,9 +57,6 @@ class UtxPoolImpl(
   private[this] val transactions          = new ConcurrentHashMap[ByteStr, Transaction]()
   private[this] val pessimisticPortfolios = new PessimisticPortfolios(spendableBalanceChanged, blockchain.transactionHeight(_).nonEmpty)
 
-  // Init consume loop
-  TxQueue.consume()
-
   override def putIfNew(tx: Transaction, verify: Boolean): TracedResult[ValidationError, Boolean] = {
     if (transactions.containsKey(tx.id())) TracedResult.wrapValue(false)
     else putNewTx(tx, verify)
@@ -179,10 +176,11 @@ class UtxPoolImpl(
         pessimisticPortfolios.add(tx.id(), diff); true
       }
 
-    if (!verify || isNew.resultE.isRight) {
-      transactions.put(tx.id(), tx)
-      PoolMetrics.addTransaction(tx)
-    }
+    if (!verify || isNew.resultE.isRight)
+      transactions.computeIfAbsent(tx.id(), { _ =>
+        PoolMetrics.addTransaction(tx)
+        tx
+      })
 
     isNew
   }
@@ -309,6 +307,7 @@ class UtxPoolImpl(
   private[this] val traceLogger = LoggerFacade(LoggerFactory.getLogger(this.getClass.getCanonicalName + ".trace"))
   traceLogger.trace("Validation trace reporting is enabled")
 
+  @scala.annotation.tailrec
   private def extractErrorMessage(error: ValidationError): String = error match {
     case see: TxValidationError.ScriptExecutionError        => s"ScriptExecutionError(${see.error})"
     case _: TxValidationError.TransactionNotAllowedByScript => "TransactionNotAllowedByScript"
@@ -342,25 +341,22 @@ class UtxPoolImpl(
       blockchain.assetDescription(asset).forall(_.reissuable)
   }
 
-  private[this] object TxQueue {
-    private[this] val queue = AsyncQueue.unbounded[Seq[Transaction]]()(cleanupScheduler)
-
-    def offer(transactions: Seq[Transaction]): Unit =
-      queue.offer(transactions)
+  private[this] object TxCleanup {
+    private[this] val scheduled = AtomicBoolean(false)
 
-    def consume(): CancelableFuture[Unit] =
-      queue
-        .drain(1, Int.MaxValue)
-        .flatMap { transactionSeq =>
-          for (ts <- transactionSeq; transaction <- ts) addTransaction(transaction, verify = false)
-          packUnconfirmed(MultiDimensionalMiningConstraint.unlimited, ScalaDuration.Inf)
-          consume()
-        }(cleanupScheduler)
+    def runCleanupAsync(): Unit = if (scheduled.compareAndSet(false, true)) {
+      cleanupScheduler.execute { () =>
+        try packUnconfirmed(MultiDimensionalMiningConstraint.unlimited, ScalaDuration.Inf)
+        finally scheduled.set(false)
+      }
+    }
   }
 
   /** DOES NOT verify transactions */
-  def addAndCleanup(transactions: Seq[Transaction]): Unit =
-    TxQueue.offer(transactions)
+  def addAndCleanup(transactions: Seq[Transaction]): Unit = {
+    for (tx <- transactions) addTransaction(tx, verify = false)
+    TxCleanup.runCleanupAsync()
+  }
 
   override def close(): Unit = {
     cleanupScheduler.shutdown()
```
