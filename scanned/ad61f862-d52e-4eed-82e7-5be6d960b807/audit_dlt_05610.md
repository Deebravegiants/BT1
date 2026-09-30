# [?] fix(flatdb): make snap finalize crash-durable and the restart wipe cheap (#11997)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-06-16
Source: https://github.com/NethermindEth/nethermind/commit/92b96a067b9dbbd6cf262b7d82db37f1e7b058c7
Type: security-commit

## Details
fix(flatdb): make snap finalize crash-durable and the restart wipe cheap (#11997)

* fix(flatdb): make snap finalize crash-durable and the restart wipe bounded

Two distinct restart-during-snap failures on FlatDb:

- #11457: FinalizeSync advanced the WAL-durable CurrentState pointer before
  flushing the snap/heal data (written with DisableWAL). An unclean shutdown in
  that window left the pointer ahead of still-unflushed data, so a state with
  holes was served as complete -> "transaction nonce is too high" on the first
  post-pivot block -> the canonical chain was deleted as "invalid" and sync got
  permanently stuck. Flush all data before advancing the pointer so the pointer
  is never durable ahead of the state it references.

- #11442: ClearAllColumns collected every key into a single write batch, holding
  them all in memory at once and exhausting memory when wiping a large,
  partially-synced DB on restart (a fresh sync starts empty, so there is nothing
  to clear -> flat RSS). It now streams keys and point-deletes them in bounded
  batches, committing periodically. The Metadata format markers are preserved
  (only CurrentState is reset, cf. #11996). Kept entirely within the FlatDb
  persistence layer; no core DB changes.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* chore(flatdb): trim comments and harden the clear batch loop

Address review feedback:
- Trim the verbose comments flagged by @LukaszRozmej.
- Create the next write batch before disposing the current one so a throw from
  StartWriteBatch can't lead to a double dispose in the finally block.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### src/Nethermind/Nethermind.State.Flat.Test/Persistence/ClearAllColumnsBatchingTests.cs
```diff
@@ -0,0 +1,46 @@
+// SPDX-FileCopyrightText: 2026 Demerzel Solutions Limited
+// SPDX-License-Identifier: LGPL-3.0-only
+
+using System.Buffers.Binary;
+using System.Linq;
+using Nethermind.Core.Crypto;
+using Nethermind.Db;
+using Nethermind.State.Flat.Persistence;
+using NUnit.Framework;
+
+namespace Nethermind.State.Flat.Test.Persistence;
+
+[TestFixture]
+public class ClearAllColumnsBatchingTests
+{
+    // #11442/#11996: seed more keys than one batch, then confirm the column is fully wiped across batch
+    // boundaries while the Metadata format markers survive and only CurrentState resets.
+    [Test]
+    public void ClearAllColumns_clears_data_across_batch_boundaries_and_preserves_format_markers()
+    {
+        using MemColumnsDb<FlatDbColumns> db = new();
+        IDb metadata = db.GetColumnDb(FlatDbColumns.Metadata);
+        IDb storage = db.GetColumnDb(FlatDbColumns.Storage);
+
+        BasePersistence.SetLayout(metadata, FlatLayout.Flat); // writes Layout + SlotEncoding=Rlp
+        BasePersistence.SetCurrentState(metadata,
+            new StateId(123, new ValueHash256("0x1111111111111111111111111111111111111111111111111111111111111111")));
+
+        const int keyCount = 25_000; // spans multiple 10k batches
+        for (int i = 0; i < keyCount; i++)
+        {
+            byte[] key = new byte[4];
+            BinaryPrimitives.WriteInt32BigEndian(key, i);
+            storage.Set(key, [0x01]);
+        }
+
+        BasePersistence.ClearAllColumns(db);
+
+        using (Assert.EnterMultipleScope())
+        {
+            Assert.That(storage.GetAllKeys().Any(), Is.False, "all data should be wiped");
+            Assert.That(BasePersistence.ReadLayout(metadata), Is.EqualTo(FlatLayout.Flat));
+            Assert.That(BasePersistence.ReadCurrentState(metadata), Is.EqualTo(new StateId(-1, ValueKeccak.EmptyTreeHash)));
+        }
+    }
+}
```

### src/Nethermind/Nethermind.State.Flat.Test/Sync/FlatTreeSyncStoreTests.cs
```diff
@@ -2,6 +2,7 @@
 // SPDX-License-Identifier: LGPL-3.0-only
 
 using System;
+using System.Collections.Generic;
 using Nethermind.Core;
 using Nethermind.Core.Crypto;
 using Nethermind.Core.Extensions;
@@ -81,4 +82,42 @@ public void EnsureStorageEmpty_deletes_all_storage_entries()
         Assert.That(HasStorageEntries(address), Is.False, "Storage entries should be deleted after EnsureStorageEmpty");
     }
 
+    [Test]
+    public void FinalizeSync_flushes_data_before_advancing_the_state_pointer()
+    {
+        // #11457: the state pointer must advance only after the (DisableWAL) data is flushed.
+        List<string> log = [];
+        OrderRecordingPersistence spy = new(_persistence, log);
+        FlatTreeSyncStore store = new(spy, Substitute.For<IPersistenceManager>(), LimboLogs.Instance);
+        BlockHeader pivot = Build.A.BlockHeader.WithNumber(123).WithStateRoot(TestItem.KeccakA).TestObject;
+
+        store.FinalizeSync(pivot);
+
+        int firstFlush = log.IndexOf("flush");
+        int firstAdvance = log.IndexOf("advance-pointer");
+        Assert.That(firstFlush, Is.GreaterThanOrEqualTo(0), "data must be flushed during finalize");
+        Assert.That(firstAdvance, Is.GreaterThan(firstFlush), "state pointer must advance only after the data flush");
+
+        using IPersistence.IPersistenceReader reader = _persistence.CreateReader();
+        Assert.That(reader.CurrentState.BlockNumber, Is.EqualTo(123), "state pointer should end at the pivot block");
+    }
+
+    private sealed class OrderRecordingPersistence(IPersistence inner, List<string> log) : IPersistence
+    {
+        public IPersistence.IPersistenceReader CreateReader(ReaderFlags flags = ReaderFlags.None) => inner.CreateReader(flags);
+
+        public IPersistence.IWriteBatch CreateWriteBatch(in StateId from, in StateId to, WriteFlags flags = WriteFlags.None)
+        {
+            if (to != StateId.Sync) log.Add("advance-pointer");
+            return inner.CreateWriteBatch(from, to, flags);
+        }
+
+        public void Flush()
+        {
+            log.Add("flush");
+            inner.Flush();
+        }
+
+        public void Clear() => inner.Clear();
+    }
 }
```

### src/Nethermind/Nethermind.State.Flat/Persistence/BasePersistence.cs
```diff
@@ -176,24 +176,40 @@ private static void WarnRawDeprecated(ILogger logger)
 
     internal static void ClearAllColumns(IColumnsDb<FlatDbColumns> db)
     {
-        using IColumnsWriteBatch<FlatDbColumns> batch = db.StartWriteBatch();
-        foreach (FlatDbColumns column in Enum.GetValues<FlatDbColumns>())
-        {
-            if (column == FlatDbColumns.Metadata)
-            {
-                // Reset only the state metadata. The on-disk format markers (layout, slot encoding)
-                // and any other metadata are preserved, otherwise a re-synced DB would be read back
-                // with the wrong slot encoding (e.g. RLP-wrapped slots misread as legacy raw).
-                batch.GetColumnBatch(column).Remove(CurrentStateKey);
-                continue;
-            }
+        // Delete in bounded batches; a single batch over every key exhausts memory when wiping a large
+        // partially-synced DB on restart. #11442
+        const int batchSize = 10_000;
 
-            IWriteBatch columnBatch = batch.GetColumnBatch(column);
-            foreach (byte[] key in db.GetColumnDb(column).GetAllKeys())
+        IColumnsWriteBatch<FlatDbColumns> batch = db.StartWriteBatch();
+        try
+        {
+            int count = 0;
+            foreach (FlatDbColumns column in Enum.GetValues<FlatDbColumns>())
             {
-                columnBatch.Remove(key);
+                if (column == FlatDbColumns.Metadata)
+                {
+                    // Preserve the format markers; wiping them makes a re-synced RLP DB read back as raw. #11996
+                    batch.GetColumnBatch(column).Remove(CurrentStateKey);
+                    continue;
+                }
+
+                foreach (byte[] key in db.GetColumnDb(column).GetAllKeys())
+                {
+                    batch.GetColumnBatch(column).Remove(key);
+                    if (++count == batchSize)
+                    {
+                        IColumnsWriteBatch<FlatDbColumns> next = db.StartWriteBatch();
+                        batch.Dispose(); // commit the chunk
+                        batch = next;
+                        count = 0;
+                    }
+                }
             }
         }
+        finally
+        {
+            batch.Dispose();
+        }
     }
 
     internal static void CreateStorageRange(
```

### src/Nethermind/Nethermind.State.Flat/Sync/FlatTreeSyncStore.cs
```diff
@@ -241,6 +241,10 @@ public void FinalizeSync(BlockHeader pivotHeader)
         StateId from = reader.CurrentState;
         StateId to = new(pivotHeader);
 
+        // Snap/heal writes use DisableWAL and are only crash-durable once flushed. Flush before advancing the
+        // WAL-durable pointer, so a crash can't leave CurrentState pointing past unflushed (holed) data. #11457
+        persistence.Flush();
+
         // Create and immediately dispose to increment state ID
         // This pattern is used by Importer - the from->to transition updates the current state pointer
         using (persistence.CreateWriteBatch(from, to))
```
