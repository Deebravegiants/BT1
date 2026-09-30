# [?] Fix crash after full pruning complete when db metrics is enabled (#5458)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2023-03-20
Source: https://github.com/NethermindEth/nethermind/commit/9794f66e8426c7f0513b80ad6f0b66d2568e28a2
Type: security-commit

## Details
Fix crash after full pruning complete when db metrics is enabled (#5458)

## Patch
### src/Nethermind/Nethermind.Db.Rocks/DbOnTheRocks.cs
```diff
@@ -61,6 +61,8 @@ public class DbOnTheRocks : IDbWithSpan, ITunableDb
 
     private string CorruptMarkerPath => Path.Join(_fullPath, "corrupt.marker");
 
+    private List<DbMetricsUpdater> _metricsUpdaters = new();
+
     protected static void InitCache(IDbConfig dbConfig)
     {
         if (Interlocked.CompareExchange(ref _cacheInitialized, 1, 0) == 0)
@@ -128,17 +130,22 @@ private RocksDb Init(string basePath, string dbPath, IDbConfig dbConfig, ILogMan
 
             if (dbConfig.EnableMetricsUpdater)
             {
-                new DbMetricsUpdater(Name, DbOptions, db, null, dbConfig, _logger).StartUpdating();
+                _metricsUpdaters.Add(new DbMetricsUpdater(Name, DbOptions, db, null, dbConfig, _logger));
                 if (columnFamilies != null)
                 {
                     foreach (ColumnFamilies.Descriptor columnFamily in columnFamilies)
                     {
                         if (db.TryGetColumnFamily(columnFamily.Name, out ColumnFamilyHandle handle))
                         {
-                            new DbMetricsUpdater(Name + "_" + columnFamily.Name, DbOptions, db, handle, dbConfig, _logger).StartUpdating();
+                            _metricsUpdaters.Add(new DbMetricsUpdater(Name + "_" + columnFamily.Name, DbOptions, db, handle, dbConfig, _logger));
                         }
                     }
                 }
+
+                foreach (DbMetricsUpdater metricsUpdater in _metricsUpdaters)
+                {
+                    metricsUpdater.StartUpdating();
+                }
             }
 
             return db;
@@ -738,6 +745,12 @@ public void Dispose()
         _isDisposing = true;
 
         if (_logger.IsInfo) _logger.Info($"Disposing DB {Name}");
+
+        foreach (DbMetricsUpdater dbMetricsUpdater in _metricsUpdaters)
+        {
+            dbMetricsUpdater.Dispose();
+        }
+
         InnerFlush();
         ReleaseUnmanagedResources();
 
```

### src/Nethermind/Nethermind.Db.Rocks/Statistics/DbMetricsUpdater.cs
```diff
@@ -153,4 +153,9 @@ private void UpdateMetricsFromList(List<(string Name, long Value)> levelStats)
 
     [GeneratedRegex("^Interval compaction: (\\d+)\\.\\d+.*GB write.*\\s+(\\d+)\\.\\d+.*MB\\/s write.*\\s+(\\d+)\\.\\d+.*GB read.*\\s+(\\d+)\\.\\d+.*MB\\/s read.*\\s+(\\d+)\\.\\d+.*seconds.*$", RegexOptions.Multiline)]
     private static partial Regex ExtractIntervalRegex();
+
+    public void Dispose()
+    {
+        _timer?.Dispose();
+    }
 }
```
