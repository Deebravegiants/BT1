# [?] [Pruning Bugfix] Prevent race condition in key deletion. (#760)

## Summary
Severity: Unknown
Chain: Ethereum
Component: hyperledger/besu
Published: 2020-05-06
Source: https://github.com/besu-eth/besu/commit/43eccbbb67b4c08baca4e51f28eccbf484ca6b78
Type: security-commit

## Details
[Pruning Bugfix] Prevent race condition in key deletion. (#760)

* add doomed key check (busy-waiting for now)

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* optional and logging

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* remove logging

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* sleeping and hardening

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* rename segments

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* move away from atomic references to regular vars

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* remove hardened segment parameter

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* increase sleep

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* spotless

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* remove unnecessary interface

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* rename

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* move commit waiting outside of timer

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* set default lock timeout to 1ms

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* add default lock timeout to tests

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* Revert "rename segments"

This reverts commit 184eefaaa0ccc857b0caff2b382f8338ff225d5d.

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* fix jmh compilation error

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* add documentation

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* bump up sleep to 1ms

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* (POC) Add lock to ensure that we don't prune while comitting

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* remove unnecessary persist (#569)

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* flesh out @mbaxter's idea and remove my code

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* iterator changes

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* hybridize with doomed key

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* comment

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* move doomed key unset to after node added listener

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* update instead of getting and setting doomedKeyRef in commit

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* comment

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* invert condition

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* remove locks

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* remove `removeAllKeysUnless`

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* more remove removeAllKeysUnless

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* reuse streamKeys

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* remove test

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* set default lock timeout to 1ms

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* add default lock timeout to tests

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* fix jmh compilation error

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* revert back to locks instead of doomedkey

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* change delete to not guarantee deletion

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* plugin hash

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* javadoc

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* Revert "change delete to not guarantee deletion"

This reverts commit 2289bb34cfe73bb34990db3b5ef3d614222b8c5b.

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* skip key deletion on timeout

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* clear in rollback

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* Revert "fix jmh compilation error"

This reverts commit b64ecf86568789583966e534685258d484987deb.

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* Revert "add default lock timeout to tests"

This reverts commit aff6aa6065a02bbc7eaa313d58034de48dd1d9ce.

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* Revert "set default lock timeout to 1ms"

This reverts commit 267fe0a642bf9cca89d53e09830454b7137324e6.

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* use noSlowDown write option instead of global timeout

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* add back tests

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* close tryDeleteOptions

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* remove unnecessary lock

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* move increment inside try

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* use StorageException subclass instead of field

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* revert accidental deletion in javadoc

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* tryDelete javadoc

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* add trace for skipping key deletion

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* merge catch and finally try blocks

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* switch from exception to boolean return value

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* tweak

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* changelog changes

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* add api back

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

* add back throws javadoc

Signed-off-by: Ratan Rai Sur <ratan.r.sur@gmail.com>

Co-authored-by: Meredith Baxter <meredith.baxter@consensys.net>
Co-authored-by: MadelineMurray <43356962+MadelineMurray@users.noreply.github.com>

## Patch
### CHANGELOG.md
```diff
@@ -26,6 +26,7 @@ permissions on the directory allow other users and groups to r/w. Ideally this s
 
 ### Bug Fixes
 
+ - MerkleTrieException when pruning should no longer occur. Using `--pruning-enabled=true` will no longer accidentaly delete keys in certain edge cases. [\#760](https://github.com/hyperledger/besu/pull/760).
 - Full help not displayed unless explicitly requested. [\#437](https://github.com/hyperledger/besu/pull/437)
 - Compatibility with undocumented Geth `eth_subscribe` fields [\#654](https://github.com/hyperledger/besu/pull/654)
 - Current block number included as part of `eth_getWork` response [\#849](https://github.com/hyperledger/besu/pull/849)
```

### ethereum/core/src/main/java/org/hyperledger/besu/ethereum/storage/keyvalue/WorldStateKeyValueStorage.java
```diff
@@ -21,10 +21,14 @@
 import org.hyperledger.besu.plugin.services.storage.KeyValueStorageTransaction;
 import org.hyperledger.besu.util.Subscribers;
 
-import java.util.ArrayList;
-import java.util.List;
+import java.util.HashSet;
 import java.util.Optional;
+import java.util.Set;
+import java.util.concurrent.atomic.AtomicInteger;
+import java.util.concurrent.locks.Lock;
+import java.util.concurrent.locks.ReentrantLock;
 import java.util.function.Predicate;
+import java.util.stream.Stream;
 
 import org.apache.tuweni.bytes.Bytes;
 import org.apache.tuweni.bytes.Bytes32;
@@ -33,6 +37,7 @@ public class WorldStateKeyValueStorage implements WorldStateStorage {
 
   private final Subscribers<NodesAddedListener> nodeAddedListeners = Subscribers.create();
   private final KeyValueStorage keyValueStorage;
+  private final ReentrantLock lock = new ReentrantLock();
 
   public WorldStateKeyValueStorage(final KeyValueStorage keyValueStorage) {
     this.keyValueStorage = keyValueStorage;
@@ -83,12 +88,27 @@ public boolean isWorldStateAvailable(final Bytes32 rootHash) {
 
   @Override
   public Updater updater() {
-    return new Updater(keyValueStorage.startTransaction(), nodeAddedListeners);
+    return new Updater(lock, keyValueStorage.startTransaction(), nodeAddedListeners);
   }
 
   @Override
   public long prune(final Predicate<byte[]> inUseCheck) {
-    return keyValueStorage.removeAllKeysUnless(inUseCheck);
+    final AtomicInteger prunedKeys = new AtomicInteger(0);
+    try (final Stream<byte[]> keys = keyValueStorage.streamKeys()) {
+      keys.forEach(
+          key -> {
+            lock.lock();
+            try {
+              if (!inUseCheck.test(key) && keyValueStorage.tryDelete(key)) {
+                prunedKeys.incrementAndGet();
+              }
+            } finally {
+              lock.unlock();
+            }
+          });
+    }
+
+    return prunedKeys.get();
   }
 
   @Override
@@ -105,11 +125,14 @@ public static class Updater implements WorldStateStorage.Updater {
 
     private final KeyValueStorageTransaction transaction;
     private final Subscribers<NodesAddedListener> nodeAddedListeners;
-    private final List<Bytes32> addedNodes = new ArrayList<>();
+    private final Set<Bytes32> addedNodes = new HashSet<>();
+    private final Lock lock;
 
     public Updater(
+        final Lock lock,
         final KeyValueStorageTransaction transaction,
         final Subscribers<NodesAddedListener> nodeAddedListeners) {
+      this.lock = lock;
       this.transaction = transaction;
       this.nodeAddedListeners = nodeAddedListeners;
     }
@@ -156,12 +179,18 @@ public Updater putAccountStorageTrieNode(final Bytes32 nodeHash, final Bytes nod
 
     @Override
     public void commit() {
-      nodeAddedListeners.forEach(listener -> listener.onNodesAdded(addedNodes));
-      transaction.commit();
+      lock.lock();
+      try {
+        nodeAddedListeners.forEach(listener -> listener.onNodesAdded(addedNodes));
+        transaction.commit();
+      } finally {
+        lock.unlock();
+      }
     }
 
     @Override
     public void rollback() {
+      addedNodes.clear();
       transaction.rollback();
     }
   }
```

### ethereum/core/src/test/java/org/hyperledger/besu/ethereum/worldstate/MarkSweepPrunerTest.java
```diff
@@ -56,8 +56,9 @@ public class MarkSweepPrunerTest {
   private final BlockDataGenerator gen = new BlockDataGenerator();
   private final NoOpMetricsSystem metricsSystem = new NoOpMetricsSystem();
   private final Map<Bytes, byte[]> hashValueStore = spy(new HashMap<>());
-  private final InMemoryKeyValueStorage stateStorage = spy(new TestInMemoryStorage(hashValueStore));
-  private final WorldStateStorage worldStateStorage = new WorldStateKeyValueStorage(stateStorage);
+  private final InMemoryKeyValueStorage stateStorage = new TestInMemoryStorage(hashValueStore);
+  private final WorldStateStorage worldStateStorage =
+      spy(new WorldStateKeyValueStorage(stateStorage));
   private final WorldStateArchive worldStateArchive =
       new WorldStateArchive(
           worldStateStorage, new WorldStatePreimageKeyValueStorage(new InMemoryKeyValueStorage()));
@@ -137,11 +138,11 @@ public void sweepBefore_shouldSweepStateRootFirst() {
     pruner.sweepBefore(markBlock.getNumber());
 
     // Check stateRoots are marked first
-    InOrder inOrder = inOrder(hashValueStore, stateStorage);
+    InOrder inOrder = inOrder(hashValueStore, worldStateStorage);
     for (Bytes32 stateRoot : stateRoots) {
       inOrder.verify(hashValueStore).remove(stateRoot);
     }
-    inOrder.verify(stateStorage).removeAllKeysUnless(any());
+    inOrder.verify(worldStateStorage).prune(any());
   }
 
   @Test
@@ -172,11 +173,11 @@ public void sweepBefore_shouldNotRemoveMarkedStateRoots() {
     pruner.sweepBefore(markBlock.getNumber());
 
     // Check stateRoots are marked first
-    InOrder inOrder = inOrder(hashValueStore, stateStorage);
+    InOrder inOrder = inOrder(hashValueStore, worldStateStorage);
     for (Bytes32 stateRoot : stateRoots) {
       inOrder.verify(hashValueStore).remove(stateRoot);
     }
-    inOrder.verify(stateStorage).removeAllKeysUnless(any());
+    inOrder.verify(worldStateStorage).prune(any());
 
     assertThat(stateStorage.containsKey(markedRoot.toArray())).isTrue();
   }
```

### plugin-api/build.gradle
```diff
@@ -64,7 +64,7 @@ Calculated : ${currentHash}
 tasks.register('checkAPIChanges', FileStateChecker) {
   description = "Checks that the API for the Plugin-API project does not change without deliberate thought"
   files = sourceSets.main.allJava.files
-  knownHash = 'wjORmE9I35CVqZIk78t8zgZUo9oIRy2fvu0x+CFnzaU='
+  knownHash = 'x6hLH75JBKLM8mNFz7n0ALRw4TWiDONJuum53da4jTY='
 }
 check.dependsOn('checkAPIChanges')
 
```

### plugin-api/src/main/java/org/hyperledger/besu/plugin/services/storage/KeyValueStorage.java
```diff
@@ -21,6 +21,7 @@
 import java.util.Optional;
 import java.util.Set;
 import java.util.function.Predicate;
+import java.util.stream.Stream;
 
 /**
  * Responsible for storing values against keys.
@@ -60,17 +61,36 @@ public interface KeyValueStorage extends Closeable {
    */
   Optional<byte[]> get(byte[] key) throws StorageException;
 
+  /**
+   * Returns a stream of all keys.
+   *
+   * @return A stream of all keys in storage.
+   * @throws StorageException problem encountered during the retrieval attempt.
+   */
+  Stream<byte[]> streamKeys() throws StorageException;
+
   /**
    * Performs an evaluation against each key in the store, keeping the entries that pass, removing
    * those that fail.
    *
    * @param retainCondition predicate to evaluate each key against, unless the result is {@code
    *     null}, both the key and associated value must be removed.
    * @return the number of keys removed.
-   * @throws StorageException problem encountered when removing data.
+   * @throws StorageException problem encountered during the retrieval attempt.
    */
   long removeAllKeysUnless(Predicate<byte[]> retainCondition) throws StorageException;
 
+  /**
+   * Delete the value corresponding to the given key if a write lock can be instantly acquired on
+   * the underlying storage. Do nothing otherwise.
+   *
+   * @param key The key to delete.
+   * @throws StorageException any problem encountered during the deletion attempt.
+   * @return false if the lock on the underlying storage could not be instantly acquired, true
+   *     otherwise
+   */
+  boolean tryDelete(byte[] key) throws StorageException;
+
   /**
    * Performs an evaluation against each key in the store, returning the set of entries that pass.
    *
```

### plugins/rocksdb/src/main/java/org/hyperledger/besu/plugin/services/storage/rocksdb/RocksDbKeyIterator.java
```diff
@@ -0,0 +1,97 @@
+/*
+ * Copyright ConsenSys AG.
+ *
+ * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
+ * the License. You may obtain a copy of the License at
+ *
+ * http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
+ * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
+ * specific language governing permissions and limitations under the License.
+ *
+ * SPDX-License-Identifier: Apache-2.0
+ */
+
+package org.hyperledger.besu.plugin.services.storage.rocksdb;
+
+import static com.google.common.base.Preconditions.checkState;
+
+import java.util.Iterator;
+import java.util.NoSuchElementException;
+import java.util.Spliterator;
+import java.util.Spliterators;
+import java.util.concurrent.atomic.AtomicBoolean;
+import java.util.stream.Stream;
+import java.util.stream.StreamSupport;
+
+import org.apache.logging.log4j.LogManager;
+import org.apache.logging.log4j.Logger;
+import org.rocksdb.RocksDBException;
+import org.rocksdb.RocksIterator;
+
+public class RocksDbKeyIterator implements Iterator<byte[]>, AutoCloseable {
+  private static final Logger LOG = LogManager.getLogger();
+
+  private final RocksIterator rocksIterator;
+  private final AtomicBoolean closed = new AtomicBoolean(false);
+
+  private RocksDbKeyIterator(final RocksIterator rocksIterator) {
+    this.rocksIterator = rocksIterator;
+  }
+
+  public static RocksDbKeyIterator create(final RocksIterator rocksIterator) {
+    return new RocksDbKeyIterator(rocksIterator);
+  }
+
+  @Override
+  public boolean hasNext() {
+    assertOpen();
+    return rocksIterator.isValid();
+  }
+
+  @Override
+  public byte[] next() {
+    assertOpen();
+    try {
+      rocksIterator.status();
+    } catch (final RocksDBException e) {
+      LOG.error(
+          String.format("%s encountered a problem while iterating.", getClass().getSimpleName()),
+          e);
+    }
+    if (!hasNext()) {
+      throw new NoSuchElementException();
+    }
+    final byte[] key = rocksIterator.key();
+    rocksIterator.next();
+    return key;
+  }
+
+  public Stream<byte[]> toStream() {
+    assertOpen();
+    final Spliterator<byte[]> spliterator =
+        Spliterators.spliteratorUnknownSize(
+            this,
+            Spliterator.IMMUTABLE
+                | Spliterator.DISTINCT
+                | Spliterator.NONNULL
+                | Spliterator.ORDERED
+                | Spliterator.SORTED);
+
+    return StreamSupport.stream(spliterator, false).onClose(this::close);
+  }
+
+  private void assertOpen() {
+    checkState(
+        !closed.get(),
+        String.format("Attempt to read from a closed %s", getClass().getSimpleName()));
+  }
+
+  @Override
+  public void close() {
+    if (closed.compareAndSet(false, true)) {
+      rocksIterator.close();
+    }
+  }
+}
```

### plugins/rocksdb/src/main/java/org/hyperledger/besu/plugin/services/storage/rocksdb/segmented/RocksDBColumnarKeyValueStorage.java
```diff
@@ -15,19 +15,20 @@
 package org.hyperledger.besu.plugin.services.storage.rocksdb.segmented;
 
 import static java.util.Objects.requireNonNullElse;
+import static java.util.stream.Collectors.toUnmodifiableSet;
 
 import org.hyperledger.besu.plugin.services.MetricsSystem;
 import org.hyperledger.besu.plugin.services.exception.StorageException;
 import org.hyperledger.besu.plugin.services.metrics.OperationTimer;
 import org.hyperledger.besu.plugin.services.storage.SegmentIdentifier;
 import org.hyperledger.besu.plugin.services.storage.rocksdb.RocksDBMetrics;
 import org.hyperledger.besu.plugin.services.storage.rocksdb.RocksDBMetricsFactory;
+import org.hyperledger.besu.plugin.services.storage.rocksdb.RocksDbKeyIterator;
 import org.hyperledger.besu.plugin.services.storage.rocksdb.RocksDbUtil;
 import org.hyperledger.besu.plugin.services.storage.rocksdb.configuration.RocksDBConfiguration;
 import org.hyperledger.besu.services.kvstore.SegmentedKeyValueStorage;
 import org.hyperledger.besu.services.kvstore.SegmentedKeyValueStorageTransactionTransitionValidatorDecorator;
 
-import java.io.Closeable;
 import java.nio.charset.StandardCharsets;
 import java.util.ArrayList;
 import java.util.List;
@@ -37,9 +38,9 @@
 import java.util.concurrent.atomic.AtomicBoolean;
 import java.util.function.Predicate;
 import java.util.stream.Collectors;
+import java.util.stream.Stream;
 
 import com.google.common.collect.ImmutableMap;
-import com.google.common.collect.Sets;
 import org.apache.logging.log4j.LogManager;
 import org.apache.logging.log4j.Logger;
 import org.apache.tuweni.bytes.Bytes;
@@ -53,12 +54,13 @@
 import org.rocksdb.RocksDBException;
 import org.rocksdb.RocksIterator;
 import org.rocksdb.Statistics;
+import org.rocksdb.Status;
 import org.rocksdb.TransactionDB;
 import org.rocksdb.TransactionDBOptions;
 import org.rocksdb.WriteOptions;
 
 public class RocksDBColumnarKeyValueStorage
-    implements SegmentedKeyValueStorage<ColumnFamilyHandle>, Closeable {
+    implements SegmentedKeyValueStorage<ColumnFamilyHandle> {
 
   static {
     RocksDbUtil.loadNativeLibrary();
@@ -73,6 +75,7 @@ public class RocksDBColumnarKeyValueStorage
   private final AtomicBoolean closed = new AtomicBoolean(false);
   private final Map<String, ColumnFamilyHandle> columnHandlesByName;
   private final RocksDBMetrics metrics;
+  private final WriteOptions tryDeleteOptions = new WriteOptions().setNoSlowdown(true);
 
   public RocksDBColumnarKeyValueStorage(
       final RocksDBConfiguration configuration,
@@ -128,7 +131,6 @@ public RocksDBColumnarKeyValueStorage(
         builder.put(segmentName, columnHandle);
       }
       columnHandlesByName = builder.build();
-
     } catch (final RocksDBException e) {
       throw new StorageException(e);
     }
@@ -164,6 +166,13 @@ public Transaction<ColumnFamilyHandle> startTransaction() throws StorageExceptio
         new RocksDbTransaction(db.beginTransaction(options), options));
   }
 
+  @Override
+  public Stream<byte[]> streamKeys(final ColumnFamilyHandle segmentHandle) {
+    final RocksIterator rocksIterator = db.newIterator(segmentHandle);
+    rocksIterator.seekToFirst();
+    return RocksDbKeyIterator.create(rocksIterator).toStream();
+  }
+
   @Override
   public long removeAllKeysUnless(
       final ColumnFamilyHandle segmentHandle, final Predicate<byte[]> inUseCheck) {
@@ -183,18 +192,23 @@ public long removeAllKeysUnless(
   }
 
   @Override
-  public Set<byte[]> getAllKeysThat(
-      final ColumnFamilyHandle segmentHandle, final Predicate<byte[]> returnCondition) {
-    final Set<byte[]> returnedKeys = Sets.newIdentityHashSet();
-    try (final RocksIterator rocksIterator = db.newIterator(segmentHandle)) {
-      for (rocksIterator.seekToFirst(); rocksIterator.isValid(); rocksIterator.next()) {
-        final byte[] key = rocksIterator.key();
-        if (returnCondition.test(key)) {
-          returnedKeys.add(key);
-        }
+  public boolean tryDelete(final ColumnFamilyHandle segmentHandle, final byte[] key) {
+    try {
+      db.delete(segmentHandle, tryDeleteOptions, key);
+      return true;
+    } catch (RocksDBException e) {
+      if (e.getStatus().getCode() == Status.Code.Incomplete) {
+        return false;
+      } else {
+        throw new StorageException(e);
       }
     }
-    return returnedKeys;
+  }
+
+  @Override
+  public Set<byte[]> getAllKeysThat(
+      final ColumnFamilyHandle segmentHandle, final Predicate<byte[]> returnCondition) {
+    return streamKeys(segmentHandle).filter(returnCondition).collect(toUnmodifiableSet());
   }
 
   @Override
@@ -284,6 +298,7 @@ public void rollback() {
     }
 
     private void close() {
+      tryDeleteOptions.close();
       innerTx.close();
       options.close();
     }
```

### plugins/rocksdb/src/main/java/org/hyperledger/besu/plugin/services/storage/rocksdb/unsegmented/RocksDBKeyValueStorage.java
```diff
@@ -14,13 +14,16 @@
  */
 package org.hyperledger.besu.plugin.services.storage.rocksdb.unsegmented;
 
+import static java.util.stream.Collectors.toUnmodifiableSet;
+
 import org.hyperledger.besu.plugin.services.MetricsSystem;
 import org.hyperledger.besu.plugin.services.exception.StorageException;
 import org.hyperledger.besu.plugin.services.metrics.OperationTimer;
 import org.hyperledger.besu.plugin.services.storage.KeyValueStorage;
 import org.hyperledger.besu.plugin.services.storage.KeyValueStorageTransaction;
 import org.hyperledger.besu.plugin.services.storage.rocksdb.RocksDBMetrics;
 import org.hyperledger.besu.plugin.services.storage.rocksdb.RocksDBMetricsFactory;
+import org.hyperledger.besu.plugin.services.storage.rocksdb.RocksDbKeyIterator;
 import org.hyperledger.besu.plugin.services.storage.rocksdb.RocksDbUtil;
 import org.hyperledger.besu.plugin.services.storage.rocksdb.configuration.RocksDBConfiguration;
 import org.hyperledger.besu.services.kvstore.KeyValueStorageTransactionTransitionValidatorDecorator;
@@ -29,8 +32,8 @@
 import java.util.Set;
 import java.util.concurrent.atomic.AtomicBoolean;
 import java.util.function.Predicate;
+import java.util.stream.Stream;
 
-import com.google.common.collect.Sets;
 import org.apache.logging.log4j.LogManager;
 import org.apache.logging.log4j.Logger;
 import org.rocksdb.BlockBasedTableConfig;
@@ -39,6 +42,7 @@
 import org.rocksdb.RocksDBException;
 import org.rocksdb.RocksIterator;
 import org.rocksdb.Statistics;
+import org.rocksdb.Status;
 import org.rocksdb.TransactionDB;
 import org.rocksdb.TransactionDBOptions;
 import org.rocksdb.WriteOptions;
@@ -56,6 +60,7 @@ public class RocksDBKeyValueStorage implements KeyValueStorage {
   private final TransactionDB db;
   private final AtomicBoolean closed = new AtomicBoolean(false);
   private final RocksDBMetrics rocksDBMetrics;
+  private final WriteOptions tryDeleteOptions = new WriteOptions().setNoSlowdown(true);
 
   public RocksDBKeyValueStorage(
       final RocksDBConfiguration configuration,
@@ -116,6 +121,18 @@ public Optional<byte[]> get(final byte[] key) throws StorageException {
     }
   }
 
+  @Override
+  public Set<byte[]> getAllKeysThat(final Predicate<byte[]> returnCondition) {
+    return streamKeys().filter(returnCondition).collect(toUnmodifiableSet());
+  }
+
+  @Override
+  public Stream<byte[]> streamKeys() {
+    final RocksIterator rocksIterator = db.newIterator();
+    rocksIterator.seekToFirst();
+    return RocksDbKeyIterator.create(rocksIterator).toStream();
+  }
+
   @Override
   public long removeAllKeysUnless(final Predicate<byte[]> retainCondition) throws StorageException {
     long removedNodeCounter = 0;
@@ -134,17 +151,17 @@ public long removeAllKeysUnless(final Predicate<byte[]> retainCondition) throws
   }
 
   @Override
-  public Set<byte[]> getAllKeysThat(final Predicate<byte[]> returnCondition) {
-    final Set<byte[]> returnedKeys = Sets.newIdentityHashSet();
-    try (final RocksIterator rocksIterator = db.newIterator()) {
-      for (rocksIterator.seekToFirst(); rocksIterator.isValid(); rocksIterator.next()) {
-        final byte[] key = rocksIterator.key();
-        if (returnCondition.test(key)) {
-          returnedKeys.add(key);
-        }
+  public boolean tryDelete(final byte[] key) {
+    try {
+      db.delete(tryDeleteOptions, key);
+      return true;
+    } catch (RocksDBException e) {
+      if (e.getStatus().getCode() == Status.Code.Incomplete) {
+        return false;
+      } else {
+        throw new StorageException(e);
       }
     }
-    return returnedKeys;
   }
 
   @Override
@@ -158,6 +175,7 @@ public KeyValueStorageTransaction startTransaction() throws StorageException {
   @Override
   public void close() {
     if (closed.compareAndSet(false, true)) {
+      tryDeleteOptions.close();
       txOptions.close();
       options.close();
       db.close();
```

### plugins/rocksdb/src/test/java/org/hyperledger/besu/plugin/services/storage/rocksdb/unsegmented/RocksDBColumnarKeyValueStorageTest.java
```diff
@@ -73,13 +73,22 @@ public void canRemoveThroughSegmentIteration() throws Exception {
     tx.put(barSegment, bytesOf(6), bytesOf(6));
     tx.commit();
 
-    final long removedFromFoo =
-        store.removeAllKeysUnless(fooSegment, x -> Arrays.equals(x, bytesOf(3)));
-    final long removedFromBar =
-        store.removeAllKeysUnless(barSegment, x -> Arrays.equals(x, bytesOf(4)));
-
-    assertThat(removedFromFoo).isEqualTo(2);
-    assertThat(removedFromBar).isEqualTo(2);
+    store
+        .streamKeys(fooSegment)
+        .forEach(
+            key -> {
+              if (!Arrays.equals(key, bytesOf(3))) store.tryDelete(fooSegment, key);
+            });
+    store
+        .streamKeys(barSegment)
+        .forEach(
+            key -> {
+              if (!Arrays.equals(key, bytesOf(4))) store.tryDelete(barSegment, key);
+            });
+
+    for (final ColumnFamilyHandle segment : Set.of(fooSegment, barSegment)) {
+      assertThat(store.streamKeys(segment).count()).isEqualTo(1);
+    }
 
     assertThat(store.get(fooSegment, bytesOf(1))).isEmpty();
     assertThat(store.get(fooSegment, bytesOf(2))).isEmpty();
```

### services/kvstore/src/main/java/org/hyperledger/besu/services/kvstore/InMemoryKeyValueStorage.java
```diff
@@ -29,7 +29,9 @@
 import java.util.concurrent.locks.ReadWriteLock;
 import java.util.concurrent.locks.ReentrantReadWriteLock;
 import java.util.function.Predicate;
+import java.util.stream.Stream;
 
+import com.google.common.collect.ImmutableSet;
 import org.apache.tuweni.bytes.Bytes;
 
 public class InMemoryKeyValueStorage implements KeyValueStorage {
@@ -72,6 +74,22 @@ public Optional<byte[]> get(final byte[] key) throws StorageException {
     }
   }
 
+  @Override
+  public Set<byte[]> getAllKeysThat(final Predicate<byte[]> returnCondition) {
+    return streamKeys().filter(returnCondition).collect(toUnmodifiableSet());
+  }
+
+  @Override
+  public Stream<byte[]> streamKeys() {
+    final Lock lock = rwLock.readLock();
+    lock.lock();
+    try {
+      return ImmutableSet.copyOf(hashValueStore.keySet()).stream().map(Bytes::toArrayUnsafe);
+    } finally {
+      lock.unlock();
+    }
+  }
+
   @Override
   public long removeAllKeysUnless(final Predicate<byte[]> retainCondition) throws StorageException {
     final Lock lock = rwLock.writeLock();
@@ -86,17 +104,17 @@ public long removeAllKeysUnless(final Predicate<byte[]> retainCondition) throws
   }
 
   @Override
-  public Set<byte[]> getAllKeysThat(final Predicate<byte[]> returnCondition) {
-    final Lock lock = rwLock.readLock();
-    lock.lock();
-    try {
-      return hashValueStore.keySet().stream()
-          .map(Bytes::toArrayUnsafe)
-          .filter(returnCondition)
-          .collect(toUnmodifiableSet());
-    } finally {
-      lock.unlock();
+  public boolean tryDelete(final byte[] key) {
+    final Lock lock = rwLock.writeLock();
+    if (lock.tryLock()) {
+      try {
+        hashValueStore.remove(Bytes.wrap(key));
+      } finally {
+        lock.unlock();
+      }
+      return true;
     }
+    return false;
   }
 
   @Override
```

### services/kvstore/src/main/java/org/hyperledger/besu/services/kvstore/LimitedInMemoryKeyValueStorage.java
```diff
@@ -14,6 +14,8 @@
  */
 package org.hyperledger.besu.services.kvstore;
 
+import static java.util.stream.Collectors.toUnmodifiableSet;
+
 import org.hyperledger.besu.plugin.services.exception.StorageException;
 import org.hyperledger.besu.plugin.services.storage.KeyValueStorage;
 import org.hyperledger.besu.plugin.services.storage.KeyValueStorageTransaction;
@@ -27,10 +29,11 @@
 import java.util.concurrent.locks.ReadWriteLock;
 import java.util.concurrent.locks.ReentrantReadWriteLock;
 import java.util.function.Predicate;
-import java.util.stream.Collectors;
+import java.util.stream.Stream;
 
 import com.google.common.cache.Cache;
 import com.google.common.cache.CacheBuilder;
+import com.google.common.collect.ImmutableSet;
 import org.apache.tuweni.bytes.Bytes;
 
 /**
@@ -76,19 +79,47 @@ public Optional<byte[]> get(final byte[] key) {
     }
   }
 
+  @Override
+  public Set<byte[]> getAllKeysThat(final Predicate<byte[]> returnCondition) {
+    return streamKeys().filter(returnCondition).collect(toUnmodifiableSet());
+  }
+
+  @Override
+  public Stream<byte[]> streamKeys() {
+    final Lock lock = rwLock.readLock();
+    lock.lock();
+    try {
+      return ImmutableSet.copyOf(storage.asMap().keySet()).stream().map(Bytes::toArrayUnsafe);
+    } finally {
+      lock.unlock();
+    }
+  }
+
   @Override
   public long removeAllKeysUnless(final Predicate<byte[]> retainCondition) throws StorageException {
-    final long initialSize = storage.size();
-    storage.asMap().keySet().removeIf(key -> !retainCondition.test(key.toArrayUnsafe()));
-    return initialSize - storage.size();
+    final Lock lock = rwLock.writeLock();
+    lock.lock();
+    try {
+      final long initialSize = storage.size();
+      storage.asMap().keySet().removeIf(key -> !retainCondition.test(key.toArrayUnsafe()));
+      return initialSize - storage.size();
+    } finally {
+      lock.unlock();
+    }
   }
 
   @Override
-  public Set<byte[]> getAllKeysThat(final Predicate<byte[]> returnCondition) {
-    return storage.asMap().keySet().stream()
-        .map(Bytes::toArrayUnsafe)
-        .filter(returnCondition)
-        .collect(Collectors.toSet());
+  public boolean tryDelete(final byte[] key) {
+    final Lock lock = rwLock.writeLock();
+    if (lock.tryLock()) {
+      try {
+        storage.invalidate(Bytes.wrap(key));
+      } finally {
+        lock.unlock();
+      }
+      return true;
+    }
+    return false;
   }
 
   @Override
```

### services/kvstore/src/main/java/org/hyperledger/besu/services/kvstore/SegmentedKeyValueStorage.java
```diff
@@ -21,6 +21,7 @@
 import java.util.Optional;
 import java.util.Set;
 import java.util.function.Predicate;
+import java.util.stream.Stream;
 
 /**
  * Service provided by besu to facilitate persistent data storage.
@@ -49,7 +50,37 @@ default boolean containsKey(final S segment, final byte[] key) throws StorageExc
    */
   Transaction<S> startTransaction() throws StorageException;
 
-  long removeAllKeysUnless(S segmentHandle, Predicate<byte[]> inUseCheck);
+  /**
+   * Returns a stream of all keys for the segment.
+   *
+   * @param segmentHandle The segment handle whose keys we want to stream.
+   * @return A stream of all keys in the specified segment.
+   */
+  Stream<byte[]> streamKeys(final S segmentHandle);
+
+  /**
+   * Performs an evaluation against each key in the store, keeping the entries that pass, removing
+   * those that fail.
+   *
+   * @param segmentHandle The segment handle whose keys we want to stream.
+   * @param retainCondition predicate to evaluate each key against, unless the result is {@code
+   *     null}, both the key and associated value must be removed.
+   * @return the number of keys removed.
+   */
+  long removeAllKeysUnless(final S segmentHandle, Predicate<byte[]> retainCondition)
+      throws StorageException;
+
+  /**
+   * Delete the value corresponding to the given key in the given segment if a write lock can be
+   * instantly acquired on the underlying storage. Do nothing otherwise.
+   *
+   * @param segmentHandle The segment handle whose keys we want to stream.
+   * @param key The key to delete.
+   * @throws StorageException any problem encountered during the deletion attempt.
+   * @return false if the lock on the underlying storage could not be instantly acquired, true
+   *     otherwise
+   */
+  boolean tryDelete(S segmentHandle, byte[] key) throws StorageException;
 
   Set<byte[]> getAllKeysThat(S segmentHandle, Predicate<byte[]> returnCondition);
 
```
