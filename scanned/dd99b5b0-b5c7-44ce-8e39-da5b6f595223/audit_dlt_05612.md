# [?] fix: PatriciaTree commit deadlock on bounded scheduler (#11299)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-04-22
Source: https://github.com/NethermindEth/nethermind/commit/3e8bbfce08e990493503a37e53149f0a6ddbff92
Type: security-commit

## Details
fix: PatriciaTree commit deadlock on bounded scheduler (#11299)

* refactor: optimize task creation for path commits in PatriciaTree

* refactor: replace Task.Factory.StartNew with Task.Run for improved task creation in PatriciaTree

* retrun back factory

* fix: always return concurrency quota on commit failure in PatriciaTree

* test: add test to ensure commit does not deadlock on bounded scheduler in PatriciaTree

* Update src/Nethermind/Nethermind.Trie/PatriciaTree.cs

Co-authored-by: Lukasz Rozmej <lukasz.rozmej@gmail.com>

---------

Co-authored-by: Lukasz Rozmej <lukasz.rozmej@gmail.com>

## Patch
### src/Nethermind/Nethermind.Trie.Test/TrieTests.cs
```diff
@@ -1299,5 +1299,34 @@ public void WarmUpPath_DoesNotThrow()
             patriciaTree.Invoking(t => t.WarmUpPath(Bytes.FromHexString("00000000000cc"))).Should().NotThrow();  // Non-existent key
             patriciaTree.Invoking(t => t.WarmUpPath(Bytes.FromHexString("fffffffffffff"))).Should().NotThrow();  // Completely different path
         }
+
+        [Test]
+        public void Commit_DoesNotDeadlock_WhenRunOnBoundedScheduler()
+        {
+            // Commit should not deadlock on a bounded scheduler (e.g. NewBlock P2P message on BackgroundTaskScheduler).
+            ConcurrentExclusiveSchedulerPair schedulerPair = new(TaskScheduler.Default, maxConcurrencyLevel: 1);
+
+            Task task = Task.Factory.StartNew(() =>
+            {
+                MemDb memDb = new();
+                using IPruningTrieStore trieStore = CreateTrieStore(memDb);
+                PatriciaTree tree = new(trieStore, _logManager);
+
+                Span<byte> buffer = stackalloc byte[32];
+                for (int i = 0; i < 100; i++)
+                {
+                    BinaryPrimitives.WriteInt32BigEndian(buffer, i);
+                    Hash256 key = Keccak.Compute(buffer);
+                    tree.Set(key.Bytes, key.BytesToArray());
+                }
+
+                using (trieStore.BeginBlockCommit(0))
+                {
+                    tree.Commit();
+                }
+            }, CancellationToken.None, TaskCreationOptions.None, schedulerPair.ConcurrentScheduler);
+
+            task.Wait(TimeSpan.FromSeconds(10)).Should().BeTrue("Commit deadlocked on bounded scheduler");
+        }
     }
 }
```

### src/Nethermind/Nethermind.Trie/PatriciaTree.cs
```diff
@@ -305,17 +305,24 @@ void Trace(TrieNode node, ref TreePath path, int i)
             void TraceSkipInlineNode(TrieNode node) => _logger.Trace($"Skipping commit of an inlined {node}");
         }
 
-        private async Task CreateTaskForPath(ICommitter committer, TrieNode node, int maxLevelForConcurrentCommit, TreePath childPath, TrieNode childNode, int idx)
-        {
-            // Background task
-            await Task.Yield();
-            TrieNode newChild = Commit(committer, ref childPath, childNode!, maxLevelForConcurrentCommit);
-            if (!ReferenceEquals(childNode, newChild))
+        private Task CreateTaskForPath(ICommitter committer, TrieNode node, int maxLevelForConcurrentCommit, TreePath childPath, TrieNode childNode, int idx) => Task.Factory.StartNew(
+            _ =>
             {
-                node[idx] = newChild;
-            }
-            committer.ReturnConcurrencyQuota();
-        }
+                try
+                {
+                    TrieNode newChild = Commit(committer, ref childPath, childNode!, maxLevelForConcurrentCommit);
+                    if (!ReferenceEquals(childNode, newChild))
+                        node[idx] = newChild;
+                }
+                finally
+                {
+                    committer.ReturnConcurrencyQuota();
+                }
+            },
+            state: null,
+            CancellationToken.None,
+            TaskCreationOptions.None,
+            TaskScheduler.Default);
 
         public void UpdateRootHash(bool canBeParallel = true)
         {
```
