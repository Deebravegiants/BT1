# [?] Fixes #9577: resolve race condition in StateSyncFeedTests.Big_test (#9972)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2025-12-29
Source: https://github.com/NethermindEth/nethermind/commit/fee0f239e070415f598cd4c9a382d656479640ea
Type: security-commit

## Details
Fixes #9577: resolve race condition in StateSyncFeedTests.Big_test (#9972)

* fix(sync): resolve race condition in StateSyncFeedTests.Big_test (#9577)

* fix(sync): Isolate block tree cache in StateSyncFeedTestsBase to fix parallel test failures

* changes

---------

Co-authored-by: Lukasz Rozmej <lukasz.rozmej@gmail.com>

## Patch
### src/Nethermind/Nethermind.Synchronization.Test/FastSync/StateSyncFeedTestsBase.cs
```diff
@@ -43,8 +43,8 @@ public abstract class StateSyncFeedTestsBase(int defaultPeerCount = 1, int defau
 {
     public const int TimeoutLength = 20000;
 
-    private static IBlockTree? _blockTree;
-    protected static IBlockTree BlockTree => LazyInitializer.EnsureInitialized(ref _blockTree, static () => Build.A.BlockTree().OfChainLength(100).TestObject);
+    // Chain length used for test block trees, use a constant to avoid shared state
+    private const int TestChainLength = 100;
 
     protected ILogger _logger;
     protected ILogManager _logManager = null!;
@@ -93,9 +93,12 @@ protected IContainer PrepareDownloader(DbContext dbContext, Action<SyncPeerMock>
 
         builder.RegisterBuildCallback((ctx) =>
         {
+            IBlockTree blockTree = ctx.Resolve<IBlockTree>();
             ISyncPeerPool peerPool = ctx.Resolve<ISyncPeerPool>();
-            foreach (ISyncPeer syncPeer in syncPeers)
+            foreach (SyncPeerMock syncPeer in syncPeers)
             {
+                // Set per-test block tree to avoid race conditions during parallel execution
+                syncPeer.SetBlockTree(blockTree);
                 peerPool.AddPeer(syncPeer);
             }
         });
@@ -121,9 +124,10 @@ protected ContainerBuilder BuildTestContainerBuilder(DbContext dbContext, int sy
             .AddSingleton<INodeStorage>(dbContext.LocalNodeStorage)
 
             // Use factory function to make it lazy in case test need to replace IBlockTree
+            // Cache key includes type name so different inherited test classes don't share the same blocktree
             .AddSingleton<IBlockTree>((ctx) => CachedBlockTreeBuilder.BuildCached(
-                $"{nameof(StateSyncFeedTestsBase)}{dbContext.RemoteStateTree.RootHash}{BlockTree.BestSuggestedHeader!.Number}",
-                () => Build.A.BlockTree().WithStateRoot(dbContext.RemoteStateTree.RootHash).OfChainLength((int)BlockTree.BestSuggestedHeader!.Number)))
+                $"{GetType().Name}{dbContext.RemoteStateTree.RootHash}{TestChainLength}",
+                () => Build.A.BlockTree().WithStateRoot(dbContext.RemoteStateTree.RootHash).OfChainLength(TestChainLength)))
 
             .Add<SafeContext>();
 
@@ -280,6 +284,9 @@ protected class SyncPeerMock : BaseSyncPeerMock
         private readonly Func<IReadOnlyList<Hash256>, Task<IOwnedReadOnlyList<byte[]>>>? _executorResultFunction;
         private readonly long _maxRandomizedLatencyMs;
 
+        // Per-test block tree to avoid race conditions during parallel test execution
+        private IBlockTree? _blockTree;
+
         public SyncPeerMock(
             IDb stateDb,
             IDb codeDb,
@@ -345,6 +352,11 @@ public void SetFilter(Hash256[]? availableHashes)
             _filter = availableHashes;
         }
 
+        public void SetBlockTree(IBlockTree blockTree)
+        {
+            _blockTree = blockTree;
+        }
+
         public override bool TryGetSatelliteProtocol<T>(string protocol, out T protocolHandler) where T : class
         {
             if (protocol == Protocol.Snap)
@@ -358,7 +370,7 @@ public override bool TryGetSatelliteProtocol<T>(string protocol, out T protocolH
 
         public override Task<BlockHeader?> GetHeadBlockHeader(Hash256? hash, CancellationToken token)
         {
-            return Task.FromResult(BlockTree.Head?.Header);
+            return Task.FromResult(_blockTree?.Head?.Header);
         }
 
         public override Task<IOwnedReadOnlyList<byte[]>> GetByteCodes(IReadOnlyList<ValueHash256> codeHashes, CancellationToken token)
```
