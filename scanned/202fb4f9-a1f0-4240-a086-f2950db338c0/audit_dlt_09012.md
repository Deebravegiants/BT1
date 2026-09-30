# [?] ENT-4857: Fix race condition in trackTransaction (#6096)

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2020-03-25
Source: https://github.com/corda/corda/commit/2dbf90cafeb0e58f6724edbced183a776e2e7195
Type: security-commit

## Details
ENT-4857: Fix race condition in trackTransaction (#6096)

- Fix issue
- Emit warning if we are inside a DB transaction
- Include a path that does not emit warning
- Add unit tests

## Patch
### node/src/main/kotlin/net/corda/node/services/api/ServiceHubInternal.kt
```diff
@@ -260,6 +260,12 @@ interface WritableTransactionStorage : TransactionStorage {
      * ID exists.
      */
     fun getTransactionInternal(id: SecureHash): Pair<SignedTransaction, Boolean>?
+
+    /**
+     * Returns a future that completes with the transaction corresponding to [id] once it has been committed. Do not warn when run inside
+     * a DB transaction.
+     */
+    fun trackTransactionWithNoWarning(id: SecureHash): CordaFuture<SignedTransaction>
 }
 
 /**
```

### node/src/main/kotlin/net/corda/node/services/persistence/DBTransactionStorage.kt
```diff
@@ -133,6 +133,8 @@ class DBTransactionStorage(private val database: CordaPersistence, cacheFactory:
             val actTx = tx.peekableValue ?: return 0
             return actTx.sigs.sumBy { it.size + transactionSignatureOverheadEstimate } + actTx.txBits.size
         }
+
+        private val log = contextLogger()
     }
 
     private val txStorage = ThreadBox(createTransactionsMap(cacheFactory))
@@ -211,12 +213,24 @@ class DBTransactionStorage(private val database: CordaPersistence, cacheFactory:
     }
 
     override fun trackTransaction(id: SecureHash): CordaFuture<SignedTransaction> {
+
+        if (contextTransactionOrNull != null) {
+            log.warn("trackTransaction is called with an already existing, open DB transaction. As a result, there might be transactions missing from the returned data feed, because of race conditions.")
+        }
+
+        return trackTransactionWithNoWarning(id)
+    }
+
+    override fun trackTransactionWithNoWarning(id: SecureHash): CordaFuture<SignedTransaction> {
+        val updateFuture = updates.filter { it.id == id }.toFuture()
         return database.transaction {
             txStorage.locked {
                 val existingTransaction = getTransaction(id)
                 if (existingTransaction == null) {
                     updates.filter { it.id == id }.toFuture()
+                    updateFuture
                 } else {
+                    updateFuture.cancel(false)
                     doneFuture(existingTransaction)
                 }
             }
```

### node/src/main/kotlin/net/corda/node/services/statemachine/ActionExecutorImpl.kt
```diff
@@ -83,7 +83,7 @@ class ActionExecutorImpl(
 
     @Suspendable
     private fun executeTrackTransaction(fiber: FlowFiber, action: Action.TrackTransaction) {
-        services.validatedTransactions.trackTransaction(action.hash).thenMatch(
+        services.validatedTransactions.trackTransactionWithNoWarning(action.hash).thenMatch(
                 success = { transaction ->
                     fiber.scheduleEvent(Event.TransactionCommitted(transaction))
                 },
```

### node/src/test/kotlin/net/corda/node/messaging/TwoPartyTradeFlowTests.kt
```diff
@@ -733,6 +733,12 @@ class TwoPartyTradeFlowTests(private val anonymous: Boolean) {
             }
         }
 
+        override fun trackTransactionWithNoWarning(id: SecureHash): CordaFuture<SignedTransaction> {
+            return database.transaction {
+                delegate.trackTransactionWithNoWarning(id)
+            }
+        }
+
         override fun track(): DataFeed<List<SignedTransaction>, SignedTransaction> {
             return database.transaction {
                 delegate.track()
```

### node/src/test/kotlin/net/corda/node/services/persistence/DBTransactionStorageTests.kt
```diff
@@ -1,6 +1,7 @@
 package net.corda.node.services.persistence
 
 import junit.framework.TestCase.assertTrue
+import net.corda.core.concurrent.CordaFuture
 import net.corda.core.contracts.StateRef
 import net.corda.core.crypto.Crypto
 import net.corda.core.crypto.SecureHash
@@ -17,12 +18,21 @@ import net.corda.testing.internal.TestingNamedCacheFactory
 import net.corda.testing.internal.configureDatabase
 import net.corda.testing.internal.createWireTransaction
 import net.corda.testing.node.MockServices.Companion.makeTestDataSourceProperties
+import org.apache.logging.log4j.LogManager
+import org.apache.logging.log4j.core.Appender
+import org.apache.logging.log4j.core.LoggerContext
+import org.apache.logging.log4j.core.appender.WriterAppender
 import org.assertj.core.api.Assertions.assertThat
 import org.junit.After
+import org.junit.Assert
 import org.junit.Before
 import org.junit.Rule
 import org.junit.Test
+import rx.plugins.RxJavaHooks
+import java.io.StringWriter
+import java.util.concurrent.Semaphore
 import java.util.concurrent.TimeUnit
+import kotlin.concurrent.thread
 import kotlin.test.assertEquals
 
 class DBTransactionStorageTests {
@@ -33,7 +43,7 @@ class DBTransactionStorageTests {
 
     @Rule
     @JvmField
-    val testSerialization = SerializationEnvironmentRule()
+    val testSerialization = SerializationEnvironmentRule(inheritable = true)
 
     private lateinit var database: CordaPersistence
     private lateinit var transactionStorage: DBTransactionStorage
@@ -198,6 +208,107 @@ class DBTransactionStorageTests {
         assertTransactionIsRetrievable(secondTransaction)
     }
 
+    @Suppress("UnstableApiUsage")
+    @Test(timeout=300_000)
+    fun `race condition - failure path`() {
+
+        // Insert a sleep into trackTransaction
+        RxJavaHooks.setOnObservableCreate {
+            Thread.sleep(1_000)
+            it
+        }
+        try {
+            `race condition - ok path`()
+        } finally {
+            // Remove sleep so it does not affect other tests
+            RxJavaHooks.setOnObservableCreate { it }
+        }
+    }
+
+    @Test(timeout=300_000)
+    fun `race condition - ok path`() {
+
+        // Arrange
+
+        val signedTransaction =  newTransaction()
+
+        val threadCount = 2
+        val finishedThreadsSemaphore = Semaphore(threadCount)
+        finishedThreadsSemaphore.acquire(threadCount)
+
+        // Act
+
+        thread(name = "addTransaction") {
+            transactionStorage.addTransaction(signedTransaction)
+            finishedThreadsSemaphore.release()
+        }
+
+        var result: CordaFuture<SignedTransaction>? = null
+        thread(name = "trackTransaction") {
+            result =  transactionStorage.trackTransaction(signedTransaction.id)
+            finishedThreadsSemaphore.release()
+        }
+
+        if (!finishedThreadsSemaphore.tryAcquire(threadCount, 1, TimeUnit.MINUTES)) {
+            Assert.fail("Threads did not finish")
+        }
+
+        // Assert
+
+        assertThat(result).isNotNull()
+        assertThat(result?.get(20, TimeUnit.SECONDS)?.id).isEqualTo(signedTransaction.id)
+    }
+
+    @Test(timeout=300_000)
+    fun `race condition - transaction warning`() {
+
+        // Arrange
+        val signedTransaction =  newTransaction()
+
+        // Act
+        val logMessages = collectLogsFrom {
+            database.transaction {
+                val result = transactionStorage.trackTransaction(signedTransaction.id)
+                result.cancel(false)
+            }
+        }
+
+        // Assert
+        assertThat(logMessages).contains("trackTransaction is called with an already existing, open DB transaction. As a result, there might be transactions missing from the returned data feed, because of race conditions.")
+    }
+
+    private fun collectLogsFrom(statement: () -> Unit): String {
+        // Create test appender
+        val stringWriter = StringWriter()
+        val appenderName = this::collectLogsFrom.name
+        val appender: Appender = WriterAppender.createAppender(
+                null,
+                null,
+                stringWriter,
+                appenderName,
+                false,
+                true
+        )
+        appender.start()
+
+        // Add test appender
+        val context = LogManager.getContext(false) as LoggerContext
+        val configuration = context.configuration
+        configuration.addAppender(appender)
+        configuration.loggers.values.forEach { it.addAppender(appender, null, null) }
+
+        try {
+            statement()
+        } finally {
+            // Remove test appender
+            configuration.loggers.values.forEach { it.removeAppender(appenderName) }
+            configuration.appenders.remove(appenderName)
+            appender.stop()
+        }
+
+        return stringWriter.toString()
+    }
+
     private fun newTransactionStorage(cacheSizeBytesOverride: Long? = null) {
         transactionStorage = DBTransactionStorage(database, TestingNamedCacheFactory(cacheSizeBytesOverride
                 ?: 1024))
```

### testing/node-driver/src/main/kotlin/net/corda/testing/node/internal/MockTransactionStorage.kt
```diff
@@ -21,6 +21,10 @@ open class MockTransactionStorage : WritableTransactionStorage, SingletonSeriali
         return getTransaction(id)?.let { doneFuture(it) } ?: _updatesPublisher.filter { it.id == id }.toFuture()
     }
 
+    override fun trackTransactionWithNoWarning(id: SecureHash): CordaFuture<SignedTransaction> {
+        return trackTransaction(id)
+    }
+
     override fun track(): DataFeed<List<SignedTransaction>, SignedTransaction> {
         return DataFeed(txns.values.mapNotNull { if (it.isVerified) it.stx else null }, _updatesPublisher)
     }
```
