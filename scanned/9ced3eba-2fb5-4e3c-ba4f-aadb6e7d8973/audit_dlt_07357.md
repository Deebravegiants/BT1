# [?] CORDA-2694: Prevent Node Explorer from crashing should it receive unknown transaction objects. (#4842)

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2019-03-05
Source: https://github.com/corda/corda/commit/fae74eecdefc7e46f9f39d10e5dbfeecc8056598
Type: security-commit

## Details
CORDA-2694: Prevent Node Explorer from crashing should it receive unknown transaction objects. (#4842)

* CORDA-2694: Prevent Node Explorer from crashing should it receive unknown transaction objects.
Also ensure that LazyMappedList can only handle TransactionDeserialisationExceptions.

* CORDA-2694: Add unit tests for eager LazyMappedList behaviour.

* CORDA-2694: Hide LazyMappedList from the client:jfx module.

* CORDA-2694: Create an unknown transaction state that has the correct notary.

## Patch
### client/jfx/src/main/kotlin/net/corda/client/jfx/model/NodeMonitorModel.kt
```diff
@@ -119,19 +119,19 @@ class NodeMonitorModel : AutoCloseable {
                 }.toSet()
                 val consumedStates = statesSnapshot.states.toSet() - unconsumedStates
                 val initialVaultUpdate = Vault.Update(consumedStates, unconsumedStates, references = emptySet())
-                vaultUpdates.startWith(initialVaultUpdate).subscribe({ vaultUpdatesSubject.onNext(it) }, {})
+                vaultUpdates.startWith(initialVaultUpdate).subscribe(vaultUpdatesSubject::onNext, {})
 
                 // Transactions
                 val (transactions, newTransactions) = proxy.internalVerifiedTransactionsFeed()
-                newTransactions.startWith(transactions).subscribe({ transactionsSubject.onNext(it) }, {})
+                newTransactions.startWith(transactions).subscribe(transactionsSubject::onNext, {})
 
                 // SM -> TX mapping
                 val (smTxMappings, futureSmTxMappings) = proxy.stateMachineRecordedTransactionMappingFeed()
-                futureSmTxMappings.startWith(smTxMappings).subscribe({ stateMachineTransactionMappingSubject.onNext(it) }, {})
+                futureSmTxMappings.startWith(smTxMappings).subscribe(stateMachineTransactionMappingSubject::onNext, {})
 
                 // Parties on network
                 val (parties, futurePartyUpdate) = proxy.networkMapFeed()
-                futurePartyUpdate.startWith(parties.map { MapChange.Added(it) }).subscribe({ networkMapSubject.onNext(it) }, {})
+                futurePartyUpdate.startWith(parties.map(MapChange::Added)).subscribe(networkMapSubject::onNext, {})
             }
         }
 
```

### client/jfx/src/main/kotlin/net/corda/client/jfx/model/TransactionDataModel.kt
```diff
@@ -5,11 +5,24 @@ import net.corda.client.jfx.utils.distinctBy
 import net.corda.client.jfx.utils.lift
 import net.corda.client.jfx.utils.map
 import net.corda.client.jfx.utils.recordInSequence
-import net.corda.core.contracts.ContractState
-import net.corda.core.contracts.StateAndRef
-import net.corda.core.contracts.StateRef
+import net.corda.core.contracts.*
+import net.corda.core.crypto.entropyToKeyPair
+import net.corda.core.identity.AbstractParty
+import net.corda.core.identity.CordaX500Name
+import net.corda.core.identity.Party
+import net.corda.core.internal.eagerDeserialise
+import net.corda.core.transactions.LedgerTransaction
 import net.corda.core.transactions.SignedTransaction
 import net.corda.core.transactions.WireTransaction
+import java.math.BigInteger.ZERO
+
+private class Unknown : Contract {
+    override fun verify(tx: LedgerTransaction) = throw UnsupportedOperationException()
+
+    object State : ContractState {
+        override val participants: List<AbstractParty> = emptyList()
+    }
+}
 
 /**
  * [PartiallyResolvedTransaction] holds a [SignedTransaction] that has zero or more inputs resolved. The intent is
@@ -41,10 +54,24 @@ data class PartiallyResolvedTransaction(
     }
 
     companion object {
+        private val DUMMY_NOTARY = Party(CordaX500Name("Dummy Notary", "Nowhere", "ZZ"), entropyToKeyPair(ZERO).public)
+
         fun fromSignedTransaction(
                 transaction: SignedTransaction,
                 inputTransactions: Map<StateRef, SignedTransaction?>
         ): PartiallyResolvedTransaction {
+            /**
+             * Forcibly deserialize our transaction outputs up-front.
+             * Replace any [TransactionState] objects that fail to
+             * deserialize with a dummy transaction state that uses
+             * the transaction's notary.
+             */
+            val unknownTransactionState = TransactionState(
+                data = Unknown.State,
+                contract = Unknown::class.java.name,
+                notary = transaction.notary ?: DUMMY_NOTARY
+            )
+            transaction.coreTransaction.outputs.eagerDeserialise { _, _ -> unknownTransactionState }
             return PartiallyResolvedTransaction(
                     transaction = transaction,
                     inputs = transaction.inputs.map { stateRef ->
```

### core/src/main/kotlin/net/corda/core/internal/ConstraintsUtils.kt
```diff
@@ -1,7 +1,6 @@
 package net.corda.core.internal
 
 import net.corda.core.contracts.*
-import net.corda.core.crypto.isFulfilledBy
 import net.corda.core.crypto.keys
 import net.corda.core.internal.cordapp.CordappImpl
 import net.corda.core.utilities.loggerFor
```

### core/src/main/kotlin/net/corda/core/internal/InternalUtils.kt
```diff
@@ -524,6 +524,7 @@ fun <E> MutableSet<E>.toSynchronised(): MutableSet<E> = Collections.synchronized
 /**
  * List implementation that applies the expensive [transform] function only when the element is accessed and caches calculated values.
  * Size is very cheap as it doesn't call [transform].
+ * Used internally by [net.corda.core.transactions.TraversableTransaction].
  */
 class LazyMappedList<T, U>(val originalList: List<T>, val transform: (T, Int) -> U) : AbstractList<U>() {
     private val partialResolvedList = MutableList<U?>(originalList.size) { null }
@@ -532,6 +533,15 @@ class LazyMappedList<T, U>(val originalList: List<T>, val transform: (T, Int) ->
         return partialResolvedList[index]
                 ?: transform(originalList[index], index).also { computed -> partialResolvedList[index] = computed }
     }
+    internal fun eager(onError: (TransactionDeserialisationException, Int) -> U?) {
+        for (i in 0 until size) {
+            try {
+                get(i)
+            } catch (ex: TransactionDeserialisationException) {
+                partialResolvedList[i] = onError(ex, i)
+            }
+        }
+    }
 }
 
 /**
@@ -540,6 +550,17 @@ class LazyMappedList<T, U>(val originalList: List<T>, val transform: (T, Int) ->
  */
 fun <T, U> List<T>.lazyMapped(transform: (T, Int) -> U): List<U> = LazyMappedList(this, transform)
 
+/**
+ * Iterate over a [LazyMappedList], forcing it to transform all of its elements immediately.
+ * This transformation is assumed to be "deserialisation". Does nothing for any other kind of [List].
+ * WARNING: Any changes made to the [LazyMappedList] contents are PERMANENT!
+ */
+fun <T> List<T>.eagerDeserialise(onError: (TransactionDeserialisationException, Int) -> T? = { ex, _ -> throw ex }) {
+    if (this is LazyMappedList<*, T>) {
+        eager(onError)
+    }
+}
+
 private const val MAX_SIZE = 100
 private val warnings = Collections.newSetFromMap(createSimpleCache<String, Boolean>(MAX_SIZE)).toSynchronised()
 
```

### core/src/main/kotlin/net/corda/core/transactions/WireTransaction.kt
```diff
@@ -9,7 +9,6 @@ import net.corda.core.contracts.ComponentGroupEnum.OUTPUTS_GROUP
 import net.corda.core.crypto.*
 import net.corda.core.identity.Party
 import net.corda.core.internal.*
-import net.corda.core.internal.cordapp.CordappImpl.Companion.DEFAULT_CORDAPP_VERSION
 import net.corda.core.node.NetworkParameters
 import net.corda.core.node.ServiceHub
 import net.corda.core.node.ServicesForResolution
```

### core/src/main/kotlin/net/corda/core/utilities/KotlinUtils.kt
```diff
@@ -4,15 +4,12 @@ package net.corda.core.utilities
 
 import net.corda.core.DeleteForDJVM
 import net.corda.core.KeepForDJVM
-import net.corda.core.internal.LazyMappedList
 import net.corda.core.internal.concurrent.get
-import net.corda.core.internal.createSimpleCache
 import net.corda.core.internal.uncheckedCast
 import net.corda.core.serialization.CordaSerializable
 import org.slf4j.Logger
 import org.slf4j.LoggerFactory
 import java.time.Duration
-import java.util.*
 import java.util.concurrent.ExecutionException
 import java.util.concurrent.Future
 import kotlin.reflect.KProperty
```

### core/src/test/kotlin/net/corda/core/utilities/LazyMappedListTest.kt
```diff
@@ -1,11 +1,20 @@
 package net.corda.core.utilities
 
+import net.corda.core.contracts.ComponentGroupEnum.*
 import net.corda.core.internal.lazyMapped
+import net.corda.core.internal.TransactionDeserialisationException
+import net.corda.core.internal.eagerDeserialise
+import net.corda.core.serialization.MissingAttachmentsException
+import org.junit.Rule
 import org.junit.Test
+import org.junit.rules.ExpectedException
 import kotlin.test.assertEquals
 
 class LazyMappedListTest {
 
+    @get:Rule
+    val exception: ExpectedException = ExpectedException.none()
+
     @Test
     fun `LazyMappedList works`() {
         val originalList = (1 until 10).toList()
@@ -33,4 +42,29 @@ class LazyMappedListTest {
         assertEquals(1, callCounter)
     }
 
+    @Test
+    fun testMissingAttachments() {
+        exception.expect(MissingAttachmentsException::class.java)
+        exception.expectMessage("Uncatchable!")
+
+        val lazyList = (0 until 5).toList().lazyMapped<Int, Int> { _, _ ->
+            throw MissingAttachmentsException(emptyList(), "Uncatchable!")
+        }
+
+        lazyList.eagerDeserialise { _, _ -> -999 }
+    }
+
+    @Test
+    fun testDeserialisationExceptions() {
+        val lazyList = (0 until 5).toList().lazyMapped<Int, Int> { _, index ->
+            throw TransactionDeserialisationException(
+                OUTPUTS_GROUP, index, IllegalStateException("Catch this!"))
+        }
+
+        lazyList.eagerDeserialise { _, _ -> -999 }
+        assertEquals(5, lazyList.size)
+        lazyList.forEachIndexed { idx, item ->
+            assertEquals(-999, item, "Item[$idx] mismatch")
+        }
+    }
 }
```
