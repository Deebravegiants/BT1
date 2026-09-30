# [?] Fix full pruning crash on hash. (#7907)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2024-12-13
Source: https://github.com/NethermindEth/nethermind/commit/ac486e46e87499e63d64059add5c709d13e69f15
Type: security-commit

## Details
Fix full pruning crash on hash. (#7907)

## Patch
### src/Nethermind/Nethermind.Blockchain.Test/FullPruning/FullPrunerTests.cs
```diff
@@ -248,7 +248,14 @@ public TestContext(
                     FullPruningMaxDegreeOfParallelism = degreeOfParallelism,
                     FullPruningMemoryBudgetMb = fullScanMemoryBudgetMb,
                     FullPruningCompletionBehavior = completionBehavior
-                }, BlockTree, StateReader, ProcessExitSource, _chainEstimations, DriveInfo, Substitute.For<IPruningTrieStore>(), LimboLogs.Instance);
+                },
+                BlockTree,
+                StateReader,
+                ProcessExitSource,
+                _chainEstimations,
+                DriveInfo,
+                new TrieStore(NodeStorage, LimboLogs.Instance),
+                LimboLogs.Instance);
         }
 
         public async Task RunFullPruning()
```

### src/Nethermind/Nethermind.Trie/Pruning/TrieStore.cs
```diff
@@ -1004,13 +1004,13 @@ public void PersistCache(CancellationToken cancellationToken)
             // need existing node will have to read back from db causing copy-on-read mechanism to copy the node.
             void ClearCommitSetQueue()
             {
-                while (_commitSetQueue.TryPeek(out BlockCommitSet commitSet) && commitSet.IsSealed)
+                while (CommitSetQueue.TryPeek(out BlockCommitSet commitSet) && commitSet.IsSealed)
                 {
-                    if (!_commitSetQueue.TryDequeue(out commitSet)) break;
+                    if (!CommitSetQueue.TryDequeue(out commitSet)) break;
                     if (!commitSet.IsSealed)
                     {
                         // Oops
-                        _commitSetQueue.Enqueue(commitSet);
+                        CommitSetQueue.Enqueue(commitSet);
                         break;
                     }
 
@@ -1019,7 +1019,7 @@ void ClearCommitSetQueue()
                 }
             }
 
-            if (!(_commitSetQueue?.IsEmpty ?? true))
+            if (!CommitSetQueue.IsEmpty)
             {
                 // We persist outside of lock first.
                 ClearCommitSetQueue();
```

### src/Nethermind/Nethermind.Trie/Pruning/TrieStoreDirtyNodesCache.cs
```diff
@@ -406,7 +406,7 @@ public void Dump()
 
     public void ClearLivePruningTracking()
     {
-        _persistedLastSeen.Clear();
+        _persistedLastSeen?.Clear();
         _pastPathHash?.Clear();
     }
 
```
