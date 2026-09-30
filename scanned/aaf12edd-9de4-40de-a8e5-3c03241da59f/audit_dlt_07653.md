# [?] Fix crash on after db dispose and concurrent full pruning start (#9111)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2025-08-11
Source: https://github.com/NethermindEth/nethermind/commit/d48a52bce106a60f8c66eaa90f88b8cbf5961265
Type: security-commit

## Details
Fix crash on after db dispose and concurrent full pruning start (#9111)

Fix crash on db dispose and concurrennt t full pruning start

## Patch
### src/Nethermind/Nethermind.Db.Rocks/DbOnTheRocks.cs
```diff
@@ -340,6 +340,18 @@ protected virtual long FetchTotalPropertyValue(string propertyName)
 
     public IDbMeta.DbMetric GatherMetric(bool includeSharedCache = false)
     {
+        if (_isDisposed)
+        {
+            return new IDbMeta.DbMetric()
+            {
+                Size = 0,
+                CacheSize = 0,
+                IndexSize = 0,
+                MemtableSize = 0,
+                TotalReads = _totalReads,
+                TotalWrites = _totalWrites,
+            };
+        }
         return new IDbMeta.DbMetric()
         {
             Size = GetSize(),
@@ -907,8 +919,8 @@ public unsafe ReadOnlySpan<byte> GetNativeSlice(scoped ReadOnlySpan<byte> key, C
         fixed (byte* ptr = &MemoryMarshal.GetReference(key))
         {
             slice = cf is null
-                        ? Native.Instance.rocksdb_get_pinned(db, read_options, ptr, skLength, out errPtr)
-                        : Native.Instance.rocksdb_get_pinned_cf(db, read_options, cf.Handle, ptr, skLength, out errPtr);
+                ? Native.Instance.rocksdb_get_pinned(db, read_options, ptr, skLength, out errPtr)
+                : Native.Instance.rocksdb_get_pinned_cf(db, read_options, cf.Handle, ptr, skLength, out errPtr);
         }
 
         if (errPtr != IntPtr.Zero) ThrowRocksDbException(errPtr);
```

### src/Nethermind/Nethermind.Db.Test/DbOnTheRocksTests.cs
```diff
@@ -397,6 +397,13 @@ public void TestExtractOptions()
             parsedOptions["optimize_filters_for_hits"].Should().Be("false");
             parsedOptions["memtable_whole_key_filtering"].Should().Be("true");
         }
+
+        [Test]
+        public void Can_GetMetric_AfterDispose()
+        {
+            _db.Dispose();
+            _db.GatherMetric().Size.Should().Be(0);
+        }
     }
 
     class CorruptedDbOnTheRocks : DbOnTheRocks
```

### src/Nethermind/Nethermind.Db/FullPruning/FullPruningDb.cs
```diff
@@ -31,6 +31,7 @@ public class FullPruningDb : IDb, IFullPruningDb, ITunableDb
         // current pruning context, secondary DB that the state will be written to, as well as state trie will be copied to
         // this will be null if no full pruning is in progress
         private PruningContext? _pruningContext;
+        private Lock _startLock = new Lock();
 
         public FullPruningDb(DbSettings settings, IDbFactory dbFactory, Action? updateDuplicateWriteMetrics = null)
         {
@@ -174,6 +175,16 @@ DbSettings ClonedDbSettings()
                 return clonedDbSettings;
             }
 
+            // CreateDb itself is slow, so there could be a situation where multiple start pruning attempt was
+            // created while waiting for this lock.
+            using Lock.Scope _ = _startLock.EnterScope();
+
+            if (!CanStartPruning)
+            {
+                context = null;
+                return false;
+            }
+
             // create new pruning context with new sub DB and try setting it as current
             // returns true when new pruning is started
             // returns false only on multithreaded access, returns started pruning context then
@@ -186,6 +197,7 @@ DbSettings ClonedDbSettings()
                 return true;
             }
 
+            newContext.Dispose();
             return false;
         }
 
```
