# [?] ENT-9147 Remove un-notarised transactions upon Double Spend. (#7324)

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2023-04-19
Source: https://github.com/corda/corda/commit/7bd3f5dd33eba746caf918b1d5c37183aca8d732
Type: security-commit

## Details
ENT-9147 Remove un-notarised transactions upon Double Spend. (#7324)

## Patch
### .ci/api-current.txt
```diff
@@ -2542,9 +2542,7 @@ public final class net.corda.core.flows.FinalityFlow extends net.corda.core.flow
   public <init>(net.corda.core.transactions.SignedTransaction, java.util.Collection<? extends net.corda.core.flows.FlowSession>, java.util.Collection<net.corda.core.identity.Party>, net.corda.core.utilities.ProgressTracker)
   public <init>(net.corda.core.transactions.SignedTransaction, java.util.Collection<? extends net.corda.core.flows.FlowSession>, net.corda.core.node.StatesToRecord)
   public <init>(net.corda.core.transactions.SignedTransaction, java.util.Collection<? extends net.corda.core.flows.FlowSession>, net.corda.core.node.StatesToRecord, net.corda.core.utilities.ProgressTracker)
-  public <init>(net.corda.core.transactions.SignedTransaction, java.util.Collection, net.corda.core.node.StatesToRecord, net.corda.core.utilities.ProgressTracker, int, kotlin.jvm.internal.DefaultConstructorMarker)
   public <init>(net.corda.core.transactions.SignedTransaction, java.util.Collection<? extends net.corda.core.flows.FlowSession>, net.corda.core.utilities.ProgressTracker)
-  public <init>(net.corda.core.transactions.SignedTransaction, java.util.Collection, net.corda.core.utilities.ProgressTracker, int, kotlin.jvm.internal.DefaultConstructorMarker)
   public <init>(net.corda.core.transactions.SignedTransaction, java.util.Set<net.corda.core.identity.Party>)
   public <init>(net.corda.core.transactions.SignedTransaction, java.util.Set<net.corda.core.identity.Party>, net.corda.core.utilities.ProgressTracker)
   public <init>(net.corda.core.transactions.SignedTransaction, net.corda.core.flows.FlowSession, net.corda.core.flows.FlowSession...)
```

### core-tests/src/test/kotlin/net/corda/coretests/flows/FinalityFlowTests.kt
```diff
@@ -45,6 +45,7 @@ import net.corda.finance.contracts.asset.Cash
 import net.corda.finance.flows.CashIssueFlow
 import net.corda.finance.flows.CashPaymentFlow
 import net.corda.finance.issuedBy
+import net.corda.node.services.persistence.DBTransactionStorage
 import net.corda.testing.contracts.DummyContract
 import net.corda.testing.core.ALICE_NAME
 import net.corda.testing.core.BOB_NAME
@@ -182,13 +183,47 @@ class FinalityFlowTests : WithFinality {
         }
         catch (e: NotaryException) {
             val stxId = (e.error as NotaryError.Conflict).txId
-            val (_, txnDsStatusAlice) = aliceNode.services.validatedTransactions.getTransactionInternal(stxId) ?: fail()
-            assertEquals(TransactionStatus.MISSING_NOTARY_SIG, txnDsStatusAlice)
+            assertNull(aliceNode.services.validatedTransactions.getTransactionInternal(stxId))
+            // Note: double spend error not propagated to peers by default
             val (_, txnDsStatusBob) = bobNode.services.validatedTransactions.getTransactionInternal(stxId) ?: fail()
             assertEquals(TransactionStatus.MISSING_NOTARY_SIG, txnDsStatusBob)
         }
     }
 
+    @Test(timeout=300_000)
+    fun `two phase finality flow double spend transaction with double spend handling`() {
+        val bobNode = createBob(platformVersion = PlatformVersionSwitches.TWO_PHASE_FINALITY)
+
+        val ref = aliceNode.startFlowAndRunNetwork(IssueFlow(notary)).resultFuture.getOrThrow()
+        val stx = aliceNode.startFlowAndRunNetwork(SpendFlow(ref, bobNode.info.singleIdentity())).resultFuture.getOrThrow()
+
+        val (_, txnStatusAlice) = aliceNode.services.validatedTransactions.getTransactionInternal(stx.id) ?: fail()
+        assertEquals(TransactionStatus.VERIFIED, txnStatusAlice)
+        val (_, txnStatusBob) = bobNode.services.validatedTransactions.getTransactionInternal(stx.id) ?: fail()
+        assertEquals(TransactionStatus.VERIFIED, txnStatusBob)
+
+        try {
+            aliceNode.startFlowAndRunNetwork(SpendFlow(ref, bobNode.info.singleIdentity(), handleDoubleSpend = true)).resultFuture.getOrThrow()
+        }
+        catch (e: NotaryException) {
+            val stxId = (e.error as NotaryError.Conflict).txId
+            assertNull(aliceNode.services.validatedTransactions.getTransactionInternal(stxId))
+            assertTxnRemovedFromDatabase(aliceNode, stxId)
+            assertNull(bobNode.services.validatedTransactions.getTransactionInternal(stxId))
+            assertTxnRemovedFromDatabase(bobNode, stxId)
+        }
+    }
+
+    private fun assertTxnRemovedFromDatabase(node: TestStartedNode, stxId: SecureHash) {
+        val fromDb = node.database.transaction {
+            session.createQuery(
+                    "from ${DBTransactionStorage.DBTransaction::class.java.name} where tx_id = :transactionId",
+                    DBTransactionStorage.DBTransaction::class.java
+            ).setParameter("transactionId", stxId.toString()).resultList.map { it }
+        }
+        assertEquals(0, fromDb.size)
+    }
+
     @Test(timeout=300_000)
     fun `two phase finality flow double spend transaction from pre-2PF initiator`() {
         val bobNode = createBob(platformVersion = PlatformVersionSwitches.TWO_PHASE_FINALITY - 1)
@@ -207,7 +242,9 @@ class FinalityFlowTests : WithFinality {
         catch (e: NotaryException) {
             val stxId = (e.error as NotaryError.Conflict).txId
             assertNull(bobNode.services.validatedTransactions.getTransactionInternal(stxId))
+            assertTxnRemovedFromDatabase(bobNode, stxId)
             assertNull(aliceNode.services.validatedTransactions.getTransactionInternal(stxId))
+            assertTxnRemovedFromDatabase(aliceNode, stxId)
         }
     }
 
@@ -228,9 +265,10 @@ class FinalityFlowTests : WithFinality {
         }
         catch (e: NotaryException) {
             val stxId = (e.error as NotaryError.Conflict).txId
-            val (_, txnDsStatusAlice) = aliceNode.services.validatedTransactions.getTransactionInternal(stxId) ?: fail()
-            assertEquals(TransactionStatus.MISSING_NOTARY_SIG, txnDsStatusAlice)
+            assertNull(aliceNode.services.validatedTransactions.getTransactionInternal(stxId))
+            assertTxnRemovedFromDatabase(aliceNode, stxId)
             assertNull(bobNode.services.validatedTransactions.getTransactionInternal(stxId))
+            assertTxnRemovedFromDatabase(bobNode, stxId)
         }
     }
 
@@ -281,15 +319,16 @@ class FinalityFlowTests : WithFinality {
 
     @StartableByRPC
     @InitiatingFlow
-    class SpendFlow(private val stateAndRef: StateAndRef<DummyContract.SingleOwnerState>, private val newOwner: Party) : FlowLogic<SignedTransaction>() {
+    class SpendFlow(private val stateAndRef: StateAndRef<DummyContract.SingleOwnerState>, private val newOwner: Party,
+                    private val handleDoubleSpend: Boolean? = null) : FlowLogic<SignedTransaction>() {
 
         @Suspendable
         override fun call(): SignedTransaction {
             val txBuilder = DummyContract.move(stateAndRef, newOwner)
             val signedTransaction = serviceHub.signInitialTransaction(txBuilder, ourIdentity.owningKey)
             val sessionWithCounterParty = initiateFlow(newOwner)
             sessionWithCounterParty.sendAndReceive<String>("initial-message")
-            return subFlow(FinalityFlow(signedTransaction, setOf(sessionWithCounterParty)))
+            return subFlow(FinalityFlow(signedTransaction, setOf(sessionWithCounterParty), handleDoubleSpend = handleDoubleSpend))
         }
     }
 
```

### core/src/main/kotlin/net/corda/core/flows/FinalityFlow.kt
```diff
@@ -19,8 +19,10 @@ import net.corda.core.node.StatesToRecord.ONLY_RELEVANT
 import net.corda.core.transactions.LedgerTransaction
 import net.corda.core.transactions.SignedTransaction
 import net.corda.core.utilities.ProgressTracker
+import net.corda.core.utilities.Try
 import net.corda.core.utilities.debug
 import net.corda.core.utilities.unwrap
+import java.time.Duration
 
 /**
  * Verifies the given transaction, then sends it to the named notary. If the notary agrees that the transaction
@@ -46,13 +48,15 @@ import net.corda.core.utilities.unwrap
 // To maintain backwards compatibility with the old API, FinalityFlow can act both as an initiating flow and as an inlined flow.
 // This is only possible because a flow is only truly initiating when the first call to initiateFlow is made (where the
 // presence of @InitiatingFlow is checked). So the new API is inlined simply because that code path doesn't call initiateFlow.
+@Suppress("TooManyFunctions")
 @InitiatingFlow
 class FinalityFlow private constructor(val transaction: SignedTransaction,
                                        private val oldParticipants: Collection<Party>,
                                        override val progressTracker: ProgressTracker,
                                        private val sessions: Collection<FlowSession>,
                                        private val newApi: Boolean,
-                                       private val statesToRecord: StatesToRecord = ONLY_RELEVANT) : FlowLogic<SignedTransaction>() {
+                                       private val statesToRecord: StatesToRecord = ONLY_RELEVANT,
+                                       private val handleDoubleSpend: Boolean? = null) : FlowLogic<SignedTransaction>() {
 
     @CordaInternal
     data class ExtraConstructorArgs(val oldParticipants: Collection<Party>, val sessions: Collection<FlowSession>, val newApi: Boolean, val statesToRecord: StatesToRecord)
@@ -87,13 +91,15 @@ class FinalityFlow private constructor(val transaction: SignedTransaction,
      * @param transaction What to commit.
      * @param sessions A collection of [FlowSession]s for each non-local participant of the transaction. Sessions to non-participants can
      * also be provided.
+     * @param handleDoubleSpend Whether to catch and propagate Double Spend exception to peers.
      */
     @JvmOverloads
     constructor(
             transaction: SignedTransaction,
             sessions: Collection<FlowSession>,
-            progressTracker: ProgressTracker = tracker()
-    ) : this(transaction, emptyList(), progressTracker, sessions, true)
+            progressTracker: ProgressTracker = tracker(),
+            handleDoubleSpend: Boolean? = null
+    ) : this(transaction, emptyList(), progressTracker, sessions, true, handleDoubleSpend = handleDoubleSpend)
 
     /**
      * Notarise the given transaction and broadcast it to all the participants.
@@ -102,14 +108,16 @@ class FinalityFlow private constructor(val transaction: SignedTransaction,
      * @param sessions A collection of [FlowSession]s for each non-local participant of the transaction. Sessions to non-participants can
      * also be provided.
      * @param statesToRecord Which states to commit to the vault.
+     * @param handleDoubleSpend Whether to catch and propagate Double Spend exception to peers.
      */
     @JvmOverloads
     constructor(
             transaction: SignedTransaction,
             sessions: Collection<FlowSession>,
             statesToRecord: StatesToRecord,
-            progressTracker: ProgressTracker = tracker()
-    ) : this(transaction, emptyList(), progressTracker, sessions, true, statesToRecord)
+            progressTracker: ProgressTracker = tracker(),
+            handleDoubleSpend: Boolean? = null
+    ) : this(transaction, emptyList(), progressTracker, sessions, true, statesToRecord, handleDoubleSpend = handleDoubleSpend)
 
     /**
      * Notarise the given transaction and broadcast it to all the participants.
@@ -146,11 +154,13 @@ class FinalityFlow private constructor(val transaction: SignedTransaction,
         @Suppress("ClassNaming")
         object BROADCASTING_POST_NOTARISATION : ProgressTracker.Step("Broadcasting notary signature")
         @Suppress("ClassNaming")
+        object BROADCASTING_DOUBLE_SPEND_ERROR : ProgressTracker.Step("Broadcasting notary double spend error")
+        @Suppress("ClassNaming")
         object FINALISING_TRANSACTION : ProgressTracker.Step("Finalising transaction locally")
         object BROADCASTING : ProgressTracker.Step("Broadcasting notarised transaction to other participants")
 
         @JvmStatic
-        fun tracker() = ProgressTracker(RECORD_UNNOTARISED, BROADCASTING_PRE_NOTARISATION, NOTARISING, BROADCASTING_POST_NOTARISATION, FINALISING_TRANSACTION, BROADCASTING)
+        fun tracker() = ProgressTracker(RECORD_UNNOTARISED, BROADCASTING_PRE_NOTARISATION, NOTARISING, BROADCASTING_POST_NOTARISATION, BROADCASTING_DOUBLE_SPEND_ERROR, FINALISING_TRANSACTION, BROADCASTING)
     }
 
     @Suspendable
@@ -202,28 +212,39 @@ class FinalityFlow private constructor(val transaction: SignedTransaction,
             recordLocallyAndBroadcast(newPlatformSessions, transaction)
         }
 
-        val stxn = notariseOrRecord()
-        val notarySignatures = stxn.sigs - transaction.sigs.toSet()
-        if (notarySignatures.isNotEmpty()) {
-            if (useTwoPhaseFinality && newPlatformSessions.isNotEmpty()) {
-                broadcastSignaturesAndFinalise(newPlatformSessions, notarySignatures)
-            }
-            else {
-                progressTracker.currentStep = FINALISING_TRANSACTION
-                serviceHub.telemetryServiceInternal.span("${this::class.java.name}#finalizeTransactionWithExtraSignatures", flowLogic = this) {
-                    (serviceHub as ServiceHubCoreInternal).finalizeTransactionWithExtraSignatures(transaction, notarySignatures, statesToRecord)
-                    logger.info("Finalised transaction locally.")
+        try {
+            val stxn = notariseOrRecord()
+            val notarySignatures = stxn.sigs - transaction.sigs.toSet()
+            if (notarySignatures.isNotEmpty()) {
+                if (useTwoPhaseFinality && newPlatformSessions.isNotEmpty()) {
+                    broadcastSignaturesAndFinalise(newPlatformSessions, notarySignatures)
+                } else {
+                    progressTracker.currentStep = FINALISING_TRANSACTION
+                    serviceHub.telemetryServiceInternal.span("${this::class.java.name}#finalizeTransactionWithExtraSignatures", flowLogic = this) {
+                        (serviceHub as ServiceHubCoreInternal).finalizeTransactionWithExtraSignatures(transaction, notarySignatures, statesToRecord)
+                        logger.info("Finalised transaction locally.")
+                    }
                 }
             }
-        }
 
-        if (!useTwoPhaseFinality || !needsNotarySignature(transaction)) {
-            broadcastToOtherParticipants(externalTxParticipants, newPlatformSessions + oldPlatformSessions, stxn)
-        } else if (useTwoPhaseFinality && oldPlatformSessions.isNotEmpty()) {
-            broadcastToOtherParticipants(externalTxParticipants, oldPlatformSessions, stxn)
+            if (!useTwoPhaseFinality || !needsNotarySignature(transaction)) {
+                broadcastToOtherParticipants(externalTxParticipants, newPlatformSessions + oldPlatformSessions, stxn)
+            } else if (useTwoPhaseFinality && oldPlatformSessions.isNotEmpty()) {
+                broadcastToOtherParticipants(externalTxParticipants, oldPlatformSessions, stxn)
+            }
+            return stxn
+        }
+        catch (e: NotaryException) {
+            if (e.error is NotaryError.Conflict && useTwoPhaseFinality) {
+                (serviceHub as ServiceHubCoreInternal).removeUnnotarisedTransaction(e.error.txId)
+                val overrideHandleDoubleSpend = handleDoubleSpend ?:
+                    (serviceHub.cordappProvider.getAppContext().cordapp.targetPlatformVersion >= PlatformVersionSwitches.TWO_PHASE_FINALITY)
+                if (overrideHandleDoubleSpend && newPlatformSessions.isNotEmpty()) {
+                    broadcastDoubleSpendError(newPlatformSessions, e)
+                } else sleep(Duration.ZERO) // force checkpoint to persist db update.
+            }
+            throw e
         }
-
-        return stxn
     }
 
     @Suspendable
@@ -257,7 +278,7 @@ class FinalityFlow private constructor(val transaction: SignedTransaction,
             sessions.forEach { session ->
                 try {
                     logger.debug { "Sending notary signature to party $session." }
-                    session.send(notarySignatures)
+                    session.send(Try.Success(notarySignatures))
                     // remote will finalise txn with notary signature
                 } catch (e: UnexpectedFlowEndException) {
                     throw UnexpectedFlowEndException(
@@ -276,6 +297,27 @@ class FinalityFlow private constructor(val transaction: SignedTransaction,
         }
     }
 
+    @Suspendable
+    private fun broadcastDoubleSpendError(sessions: Collection<FlowSession>, error: NotaryException) {
+        progressTracker.currentStep = BROADCASTING_DOUBLE_SPEND_ERROR
+        serviceHub.telemetryServiceInternal.span("${this::class.java.name}#broadcastDoubleSpendError", flowLogic = this) {
+            logger.info("Broadcasting notary double spend error.")
+            sessions.forEach { session ->
+                try {
+                    logger.debug { "Sending notary double spend error to party $session." }
+                    session.send(Try.Failure<List<TransactionSignature>>(error))
+                } catch (e: UnexpectedFlowEndException) {
+                    throw UnexpectedFlowEndException(
+                            "${session.counterparty} has finished prematurely and we're trying to send them a notary double spend error. " +
+                                    "Did they forget to call ReceiveFinalityFlow? (${e.message})",
+                            e.cause,
+                            e.originalErrorId
+                    )
+                }
+            }
+        }
+    }
+
     @Suspendable
     private fun broadcastToOtherParticipants(externalTxParticipants: Set<Party>, sessions: Collection<FlowSession>, tx: SignedTransaction) {
         if (externalTxParticipants.isEmpty() && sessions.isEmpty() && oldParticipants.isEmpty()) return
@@ -433,12 +475,21 @@ class ReceiveFinalityFlow @JvmOverloads constructor(private val otherSideSession
             }
             otherSideSession.send(FetchDataFlow.Request.End) // Finish fetching data (deferredAck)
             logger.info("Peer recorded transaction without notary signature. Waiting to receive notary signature.")
-            val notarySignatures = otherSideSession.receive<List<TransactionSignature>>()
-                    .unwrap { it }
-            serviceHub.telemetryServiceInternal.span("${this::class.java.name}#finalizeTransactionWithExtraSignatures", flowLogic = this) {
-                logger.debug { "Peer received notarised signature." }
-                (serviceHub as ServiceHubCoreInternal).finalizeTransactionWithExtraSignatures(stx, notarySignatures, statesToRecord)
-                logger.info("Peer finalised transaction with notary signature.")
+
+            try {
+                val notarySignatures = otherSideSession.receive<Try<List<TransactionSignature>>>().unwrap { it.getOrThrow() }
+                serviceHub.telemetryServiceInternal.span("${this::class.java.name}#finalizeTransactionWithExtraSignatures", flowLogic = this) {
+                    logger.debug { "Peer received notarised signature." }
+                    (serviceHub as ServiceHubCoreInternal).finalizeTransactionWithExtraSignatures(stx, notarySignatures, statesToRecord)
+                    logger.info("Peer finalised transaction with notary signature.")
+                }
+            } catch(throwable: NotaryException) {
+                if(throwable.error is NotaryError.Conflict) {
+                    logger.info("Peer received double spend error.")
+                    (serviceHub as ServiceHubCoreInternal).removeUnnotarisedTransaction(stx.id)
+                    sleep(Duration.ZERO) // force checkpoint to persist db update.
+                }
+                throw throwable
             }
         } else {
             serviceHub.telemetryServiceInternal.span("${this::class.java.name}#recordTransactions", flowLogic = this) {
```

### core/src/main/kotlin/net/corda/core/internal/ServiceHubCoreInternal.kt
```diff
@@ -2,6 +2,7 @@ package net.corda.core.internal
 
 import co.paralleluniverse.fibers.Suspendable
 import net.corda.core.DeleteForDJVM
+import net.corda.core.crypto.SecureHash
 import net.corda.core.crypto.TransactionSignature
 import net.corda.core.flows.FlowTransactionMetadata
 import net.corda.core.internal.notary.NotaryService
@@ -37,6 +38,14 @@ interface ServiceHubCoreInternal : ServiceHub {
      */
     fun recordUnnotarisedTransaction(txn: SignedTransaction, metadata: FlowTransactionMetadata?= null)
 
+    /**
+     * Removes transaction from data store.
+     * This is expected to be run within a database transaction.
+     *
+     * @param id of transaction to remove.
+     */
+    fun removeUnnotarisedTransaction(id: SecureHash)
+
     /**
      * Stores [SignedTransaction] with extra signatures in the local transaction storage
      *
```

### node/src/integration-test/kotlin/net/corda/node/services/statemachine/FlowHospitalTest.kt
```diff
@@ -42,6 +42,7 @@ import net.corda.testing.core.CHARLIE_NAME
 import net.corda.testing.core.singleIdentity
 import net.corda.testing.driver.DriverParameters
 import net.corda.testing.driver.driver
+import net.corda.testing.flows.waitForAllFlowsToComplete
 import net.corda.testing.node.User
 import net.corda.testing.node.internal.CustomCordapp
 import net.corda.testing.node.internal.DUMMY_CONTRACTS_CORDAPP
@@ -247,6 +248,7 @@ class FlowHospitalTest {
                 it.startFlow(::SpendStateAndCatchDoubleSpendFlow, nodeBHandle.nodeInfo.singleIdentity(), ref).returnValue.getOrThrow(20.seconds)
                 it.startFlow(::SpendStateAndCatchDoubleSpendFlow, nodeBHandle.nodeInfo.singleIdentity(), ref).returnValue.getOrThrow(20.seconds)
             }
+            waitForAllFlowsToComplete(nodeAHandle)
         }
         // 1 is the notary failing to notarise and propagating the error
         // 2 is the receiving flow failing due to the unexpected session end error
@@ -348,6 +350,7 @@ class FlowHospitalTest {
                 val ref3 = it.startFlow(::SpendStateAndCatchDoubleSpendFlow, nodeCHandle.nodeInfo.singleIdentity(), ref2).returnValue.getOrThrow(20.seconds)
                 it.startFlow(::CreateTransactionButDontFinalizeFlow, nodeBHandle.nodeInfo.singleIdentity(), ref3).returnValue.getOrThrow(20.seconds)
             }
+            waitForAllFlowsToComplete(nodeAHandle)
         }
         assertEquals(0, dischargedCounter)
         assertEquals(1, observationCounter)
@@ -374,6 +377,7 @@ class FlowHospitalTest {
                 it.startFlow(::SpendStateAndCatchDoubleSpendFlow, nodeBHandle.nodeInfo.singleIdentity(), ref).returnValue.getOrThrow(20.seconds)
                 it.startFlow(::SpendStateAndCatchDoubleSpendFlow, nodeBHandle.nodeInfo.singleIdentity(), ref, true).returnValue.getOrThrow(20.seconds)
             }
+            waitForAllFlowsToComplete(nodeAHandle)
         }
         // 1 is the notary failing to notarise and propagating the error
         assertEquals(1, dischargedCounter)
@@ -552,6 +556,7 @@ class FlowHospitalTest {
             var exceptionSeenInUserFlow = false
         }
 
+        @Suppress("TooGenericExceptionCaught")
         @Suspendable
         override fun call() {
             val consumeError = session.receive<Boolean>().unwrap { it }
@@ -562,10 +567,15 @@ class FlowHospitalTest {
             })
             try {
                 subFlow(ReceiveFinalityFlow(session, stx.id))
-            } catch (e: UnexpectedFlowEndException) {
-                exceptionSeenInUserFlow = true
-                if (!consumeError) {
-                    throw e
+            } catch (ex: Exception) {
+                when (ex) {
+                    is NotaryException,
+                    is UnexpectedFlowEndException -> {
+                        exceptionSeenInUserFlow = true
+                        if (!consumeError) {
+                            throw ex
+                        }
+                    }
                 }
             }
         }
```

### node/src/main/kotlin/net/corda/node/services/api/ServiceHubInternal.kt
```diff
@@ -251,6 +251,12 @@ interface ServiceHubInternal : ServiceHubCoreInternal {
         }
     }
 
+    override fun removeUnnotarisedTransaction(id: SecureHash) {
+        database.transaction {
+            validatedTransactions.removeUnnotarisedTransaction(id)
+        }
+    }
+
     override fun createTransactionsResolver(flow: ResolveTransactionsFlow): TransactionsResolver = DbTransactionsResolver(flow)
 
     /**
@@ -346,6 +352,12 @@ interface WritableTransactionStorage : TransactionStorage {
      */
     fun addUnnotarisedTransaction(transaction: SignedTransaction, metadata: FlowTransactionMetadata? = null): Boolean
 
+    /**
+     * Removes an un-notarised transaction (with a status of *MISSING_TRANSACTION_SIG*) from the data store.
+     * Returns null if no transaction with the ID exists.
+     */
+    fun removeUnnotarisedTransaction(id: SecureHash): Boolean
+
     /**
      * Update a previously un-notarised transaction including associated notary signatures.
      * @param transaction The notarised transaction to be finalized.
```

### node/src/main/kotlin/net/corda/node/services/persistence/DBTransactionStorage.kt
```diff
@@ -268,6 +268,27 @@ class DBTransactionStorage(private val database: CordaPersistence, cacheFactory:
                 }
             }
 
+    override fun removeUnnotarisedTransaction(id: SecureHash): Boolean {
+        return database.transaction {
+            val session = currentDBSession()
+            val criteriaBuilder = session.criteriaBuilder
+            val delete = criteriaBuilder.createCriteriaDelete(DBTransaction::class.java)
+            val root = delete.from(DBTransaction::class.java)
+            delete.where(criteriaBuilder.and(
+                    criteriaBuilder.equal(root.get<String>(DBTransaction::txId.name), id.toString()),
+                    criteriaBuilder.equal(root.get<TransactionStatus>(DBTransaction::status.name), TransactionStatus.MISSING_NOTARY_SIG)
+            ))
+            if (session.createQuery(delete).executeUpdate() != 0) {
+                txStorage.locked {
+                    txStorage.content.clear(id)
+                    txStorage.content[id]
+                    logger.debug { "Un-notarised transaction $id has been removed." }
+                }
+                true
+            } else false
+        }
+    }
+
     override fun finalizeTransactionWithExtraSignatures(transaction: SignedTransaction, signatures: Collection<TransactionSignature>) =
             addTransaction(transaction + signatures) {
                 finalizeTransactionWithExtraSignatures(transaction.id, signatures)
```

### node/src/main/kotlin/net/corda/node/utilities/AppendOnlyPersistentMap.kt
```diff
@@ -2,6 +2,7 @@ package net.corda.node.utilities
 
 import com.github.benmanes.caffeine.cache.LoadingCache
 import com.github.benmanes.caffeine.cache.Weigher
+import net.corda.core.crypto.SecureHash
 import net.corda.core.internal.NamedCacheFactory
 import net.corda.core.utilities.contextLogger
 import net.corda.nodeapi.internal.persistence.DatabaseTransaction
@@ -248,6 +249,8 @@ abstract class AppendOnlyPersistentMapBase<K, V, E, out EK>(
         cache.invalidateAll()
     }
 
+    fun clear(id: SecureHash) = cache.invalidate(id)
+
     // Helpers to know if transaction(s) are currently writing the given key.
     private fun weAreWriting(key: K): Boolean = pendingKeys[key]?.transactions?.contains(contextTransaction) ?: false
 
```

### node/src/test/kotlin/net/corda/node/messaging/TwoPartyTradeFlowTests.kt
```diff
@@ -809,6 +809,12 @@ class TwoPartyTradeFlowTests(private val anonymous: Boolean) {
             return true
         }
 
+        override fun removeUnnotarisedTransaction(id: SecureHash): Boolean {
+            return database.transaction {
+                delegate.removeUnnotarisedTransaction(id)
+            }
+        }
+
         override fun finalizeTransactionWithExtraSignatures(transaction: SignedTransaction, signatures: Collection<TransactionSignature>) : Boolean {
             database.transaction {
                 delegate.finalizeTransactionWithExtraSignatures(transaction, signatures)
```

### node/src/test/kotlin/net/corda/node/services/persistence/DBTransactionStorageTests.kt
```diff
@@ -43,13 +43,15 @@ import org.junit.Before
 import org.junit.Rule
 import org.junit.Test
 import rx.plugins.RxJavaHooks
+import java.lang.AssertionError
 import java.security.KeyPair
 import java.time.Clock
 import java.time.Instant
 import java.util.concurrent.Semaphore
 import java.util.concurrent.TimeUnit
 import kotlin.concurrent.thread
 import kotlin.test.assertEquals
+import kotlin.test.assertFailsWith
 import kotlin.test.assertFalse
 import kotlin.test.assertNull
 
@@ -159,6 +161,21 @@ class DBTransactionStorageTests {
         }
     }
 
+    @Test(timeout = 300_000)
+    fun `remove un-notarised transaction`() {
+        val now = Instant.ofEpochSecond(333444555L)
+        val transactionClock = TransactionClock(now)
+        newTransactionStorage(clock = transactionClock)
+        val transaction = newTransaction(notarySig = false)
+        transactionStorage.addUnnotarisedTransaction(transaction)
+        assertNull(transactionStorage.getTransaction(transaction.id))
+        assertEquals(MISSING_NOTARY_SIG, readTransactionFromDB(transaction.id).status)
+
+        assertEquals(true, transactionStorage.removeUnnotarisedTransaction(transaction.id))
+        assertFailsWith<AssertionError> { readTransactionFromDB(transaction.id).status }
+        assertNull(transactionStorage.getTransactionInternal(transaction.id))
+    }
+
     @Test(timeout = 300_000)
     fun `finalize unverified transaction and verify no additional signatures are added`() {
         val now = Instant.ofEpochSecond(333444555L)
```

### testing/node-driver/src/main/kotlin/net/corda/testing/flows/FlowTestsUtils.kt
```diff
@@ -1,13 +1,15 @@
 package net.corda.testing.flows
 
 import co.paralleluniverse.fibers.Suspendable
+import co.paralleluniverse.strands.Strand
 import net.corda.core.concurrent.CordaFuture
 import net.corda.core.flows.FlowLogic
 import net.corda.core.flows.FlowSession
 import net.corda.core.toFuture
 import net.corda.core.utilities.UntrustworthyData
 import net.corda.core.utilities.unwrap
 import net.corda.node.internal.InitiatedFlowFactory
+import net.corda.testing.driver.NodeHandle
 import net.corda.testing.node.internal.TestStartedNode
 import rx.Observable
 import kotlin.reflect.KClass
@@ -95,4 +97,13 @@ fun <T : FlowLogic<*>> TestStartedNode.registerCoreFlowFactory(initiatingFlowCla
                                                                initiatedFlowClass: Class<T>,
                                                                flowFactory: (FlowSession) -> T, track: Boolean): Observable<T> {
     return this.internals.registerInitiatedFlowFactory(initiatingFlowClass, initiatedFlowClass, InitiatedFlowFactory.Core(flowFactory), track)
+}
+
+fun waitForAllFlowsToComplete(nodeHandle: NodeHandle, maxIterations: Int = 60, iterationDelay: Long = 500) {
+    repeat((0..maxIterations).count()) {
+        if (nodeHandle.rpc.stateMachinesSnapshot().isEmpty()) {
+            return
+        }
+        Strand.sleep(iterationDelay)
+    }
 }
\ No newline at end of file
```

### testing/node-driver/src/main/kotlin/net/corda/testing/node/internal/MockTransactionStorage.kt
```diff
@@ -59,6 +59,10 @@ open class MockTransactionStorage : WritableTransactionStorage, SingletonSeriali
         return txns.putIfAbsent(transaction.id, TxHolder(transaction, status = TransactionStatus.MISSING_NOTARY_SIG)) == null
     }
 
+    override fun removeUnnotarisedTransaction(id: SecureHash): Boolean {
+        return txns.remove(id) != null
+    }
+
     override fun finalizeTransactionWithExtraSignatures(transaction: SignedTransaction, signatures: Collection<TransactionSignature>): Boolean {
         val current = txns.replace(transaction.id, TxHolder(transaction, status = TransactionStatus.VERIFIED))
         return if (current != null) {
```
