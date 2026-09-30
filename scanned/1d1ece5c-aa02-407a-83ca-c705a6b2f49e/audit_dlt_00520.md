# [?] fix: fix race condition in FullPruningDb read methods (#10920)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-06-02
Source: https://github.com/NethermindEth/nethermind/commit/afddfd76f4c6cf5ca36be76e515cd7cffbaa8181
Type: security-commit

## Details
fix: fix race condition in FullPruningDb read methods (#10920)

* Update FullPruningDb.cs

* Update FullPruningDb.cs

* Update FullPruningDb.cs

* fix: capture _pruningContext locally in StartWriteBatch

Same race-condition class as the read methods: the field is read twice
in the ternary, so a concurrent FinishPruning clearing it to null between
the null check and the .CloningDb dereference would throw NRE.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

* Apply suggestion from @LukaszRozmej

---------

Co-authored-by: Lukasz Rozmej <lukasz.rozmej@gmail.com>
Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

## Patch
### src/Nethermind/Nethermind.Db/FullPruning/FullPruningDb.cs
```diff
@@ -31,7 +31,7 @@ public class FullPruningDb : IDb, IFullPruningDb, ITunableDb
 
         // current pruning context, secondary DB that the state will be written to, as well as state trie will be copied to
         // this will be null if no full pruning is in progress
-        private PruningContext? _pruningContext;
+        private volatile PruningContext? _pruningContext;
         private Lock _startLock = new();
 
         public FullPruningDb(DbSettings settings, IDbFactory dbFactory, Action? updateDuplicateWriteMetrics = null)
@@ -53,9 +53,10 @@ public byte[]? this[ReadOnlySpan<byte> key]
         public byte[]? Get(ReadOnlySpan<byte> key, ReadFlags flags = ReadFlags.None)
         {
             byte[]? value = _currentDb.Get(key, flags); // we are reading from the main DB
-            if (value is not null && _pruningContext?.DuplicateReads == true && (flags & ReadFlags.SkipDuplicateRead) == 0)
+            PruningContext? pruningContext = _pruningContext;
+            if (value is not null && pruningContext?.DuplicateReads == true && (flags & ReadFlags.SkipDuplicateRead) == 0)
             {
-                Duplicate(_pruningContext.CloningDb, key, value, WriteFlags.None);
+                Duplicate(pruningContext.CloningDb, key, value, WriteFlags.None);
             }
 
             return value;
@@ -64,9 +65,10 @@ public byte[]? this[ReadOnlySpan<byte> key]
         public Span<byte> GetSpan(scoped ReadOnlySpan<byte> key, ReadFlags flags = ReadFlags.None)
         {
             Span<byte> value = _currentDb.GetSpan(key, flags); // we are reading from the main DB
-            if (!value.IsNull() && _pruningContext?.DuplicateReads == true && (flags & ReadFlags.SkipDuplicateRead) == 0)
+            PruningContext? pruningContext = _pruningContext;
+            if (!value.IsNull() && pruningContext?.DuplicateReads == true && (flags & ReadFlags.SkipDuplicateRead) == 0)
             {
-                Duplicate(_pruningContext.CloningDb, key, value, WriteFlags.None);
+                Duplicate(pruningContext.CloningDb, key, value, WriteFlags.None);
             }
 
             return value;
@@ -75,9 +77,10 @@ public Span<byte> GetSpan(scoped ReadOnlySpan<byte> key, ReadFlags flags = ReadF
         public MemoryManager<byte>? GetOwnedMemory(ReadOnlySpan<byte> key, ReadFlags flags = ReadFlags.None)
         {
             MemoryManager<byte>? memoryManager = _currentDb.GetOwnedMemory(key, flags);
-            if (memoryManager is not null && _pruningContext?.DuplicateReads == true && (flags & ReadFlags.SkipDuplicateRead) == 0)
+            PruningContext? pruningContext = _pruningContext;
+            if (memoryManager is not null && pruningContext?.DuplicateReads == true && (flags & ReadFlags.SkipDuplicateRead) == 0)
             {
-                Duplicate(_pruningContext.CloningDb, key, memoryManager.GetSpan(), WriteFlags.None);
+                Duplicate(pruningContext.CloningDb, key, memoryManager.GetSpan(), WriteFlags.None);
             }
 
             return memoryManager;
@@ -122,10 +125,13 @@ private void DuplicateMerge(IMergeableKeyValueStore db, ReadOnlySpan<byte> key,
         }
 
         // we also need to duplicate writes that are in batches
-        public IWriteBatch StartWriteBatch() =>
-            _pruningContext is null
+        public IWriteBatch StartWriteBatch()
+        {
+            IDb? cloningDb = _pruningContext?.CloningDb;
+            return cloningDb is null
                 ? _currentDb.StartWriteBatch()
-                : new DuplicatingWriteBatch(_currentDb.StartWriteBatch(), _pruningContext.CloningDb.StartWriteBatch(), this);
+                : new DuplicatingWriteBatch(_currentDb.StartWriteBatch(), cloningDb.StartWriteBatch(), this);
+        }
 
         public void Dispose()
         {
```
