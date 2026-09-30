# [?] Fix/deadlock due to TCS setresult behaviour (#5055)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2022-12-27
Source: https://github.com/NethermindEth/nethermind/commit/0ffeb06eba29ca83778150c8b645ed2ca5583822
Type: security-commit

## Details
Fix/deadlock due to TCS setresult behaviour (#5055)

* Refactor to reduce code duplication

* Fix random deadlock

## Patch
### src/Nethermind/Nethermind.Network/P2P/Request.cs
```diff
@@ -11,7 +11,7 @@ public class Request<TMsg, TResult>
     {
         public Request(TMsg message)
         {
-            CompletionSource = new TaskCompletionSource<TResult>();
+            CompletionSource = new TaskCompletionSource<TResult>(TaskCreationOptions.RunContinuationsAsynchronously);
             Message = message;
         }
 
```

### src/Nethermind/Nethermind.Specs/MainNetSpecProvider.cs
```diff
@@ -1,7 +1,6 @@
 // SPDX-FileCopyrightText: 2022 Demerzel Solutions Limited
 // SPDX-License-Identifier: LGPL-3.0-only
 
-using Nethermind.Core;
 using Nethermind.Core.Specs;
 using Nethermind.Int256;
 using Nethermind.Specs.Forks;
@@ -77,7 +76,7 @@ public IReleaseSpec GetSpec(ForkActivation forkActivation) =>
             //(GrayGlacierBlockNumber, PragueBlockTimestamp), (GrayGlacierBlockNumber, OsakaBlockTimestamp)
         };
 
-        private MainnetSpecProvider() { }
+        public MainnetSpecProvider() { }
 
         public static readonly MainnetSpecProvider Instance = new();
     }
```

### src/Nethermind/Nethermind.Synchronization.Test/BlockDownloaderTests.Merge.cs
```diff
@@ -2,30 +2,32 @@
 // SPDX-License-Identifier: LGPL-3.0-only
 
 using System;
+using System.Collections.Generic;
 using System.Threading;
 using System.Threading.Tasks;
 using FluentAssertions;
 using Nethermind.Blockchain;
-using Nethermind.Blockchain.Receipts;
 using Nethermind.Blockchain.Synchronization;
 using Nethermind.Consensus;
-using Nethermind.Consensus.Validators;
 using Nethermind.Core;
+using Nethermind.Core.Specs;
 using Nethermind.Core.Test.Builders;
 using Nethermind.Db;
 using Nethermind.Int256;
 using Nethermind.Logging;
 using Nethermind.Merge.Plugin;
-using Nethermind.Merge.Plugin.Handlers;
 using Nethermind.Merge.Plugin.Synchronization;
 using Nethermind.Merge.Plugin.Test;
 using Nethermind.Specs;
-using Nethermind.Specs.Forks;
+using Nethermind.Stats;
+using Nethermind.Stats.Model;
 using Nethermind.Synchronization.Blocks;
 using Nethermind.Synchronization.ParallelSync;
 using Nethermind.Synchronization.Peers;
+using Nethermind.Synchronization.Peers.AllocationStrategies;
 using Nethermind.Synchronization.Reporting;
 using NSubstitute;
+using NSubstitute.ClearExtensions;
 using NUnit.Framework;
 
 namespace Nethermind.Synchronization.Test;
@@ -48,32 +50,16 @@ public async Task Merge_Happy_path(long pivot, long headNumber, int options, int
             .InsertBeaconBlocks(pivot + 1, insertedBeaconBlocks, BlockTreeTests.BlockTreeTestScenario.ScenarioBuilder.TotalDifficultyMode.Null);
         BlockTree notSyncedTree = blockTrees.NotSyncedTree;
         BlockTree syncedTree = blockTrees.SyncedTree;
-        Context ctx = new(notSyncedTree);
+        MergeContext ctx = new();
+        ctx.BlockTreeScenario = blockTrees;
+
         DownloaderOptions downloaderOptions = (DownloaderOptions)options;
         bool withReceipts = downloaderOptions == DownloaderOptions.WithReceipts;
-        InMemoryReceiptStorage receiptStorage = new();
-        MemDb metadataDb = blockTrees.NotSyncedTreeBuilder.MetadataDb;
-        PoSSwitcher posSwitcher = new(new MergeConfig() { TerminalTotalDifficulty = "0" }, new SyncConfig(), metadataDb, notSyncedTree,
-            RopstenSpecProvider.Instance, LimboLogs.Instance);
-        BeaconPivot beaconPivot = new(new SyncConfig(), metadataDb, notSyncedTree, LimboLogs.Instance);
-        beaconPivot.EnsurePivot(blockTrees.SyncedTree.FindHeader(pivot, BlockTreeLookupOptions.None));
-        beaconPivot.ProcessDestination = blockTrees.SyncedTree.FindHeader(pivot, BlockTreeLookupOptions.None);
-
-        MergeBlockDownloader downloader = new(
-            posSwitcher,
-            beaconPivot,
-            ctx.Feed,
-            ctx.PeerPool,
-            notSyncedTree,
-            Always.Valid,
-            Always.Valid,
-            NullSyncReport.Instance,
-            receiptStorage,
-            RopstenSpecProvider.Instance,
-            CreateMergePeerChoiceStrategy(posSwitcher, beaconPivot),
-            new ChainLevelHelper(notSyncedTree, beaconPivot, new SyncConfig(), LimboLogs.Instance),
-            Substitute.For<ISyncProgressResolver>(),
-            LimboLogs.Instance);
+        ctx.MergeConfig = new MergeConfig() { TerminalTotalDifficulty = "0" };
+        ctx.BeaconPivot.EnsurePivot(blockTrees.SyncedTree.FindHeader(pivot, BlockTreeLookupOptions.None));
+        ctx.BeaconPivot.ProcessDestination = blockTrees.SyncedTree.FindHeader(pivot, BlockTreeLookupOptions.None);
+
+        BlockDownloader downloader = ctx.BlockDownloader;
 
         Response responseOptions = Response.AllCorrect;
         if (withReceipts)
@@ -96,8 +82,8 @@ public async Task Merge_Happy_path(long pivot, long headNumber, int options, int
             }
         }
 
-        receiptStorage.Count.Should().Be(withReceipts ? receiptCount : 0);
-        beaconPivot.ProcessDestination?.Number.Should().Be(insertedBeaconBlocks);
+        ctx.ReceiptStorage.Count.Should().Be(withReceipts ? receiptCount : 0);
+        ctx.BeaconPivot.ProcessDestination?.Number.Should().Be(insertedBeaconBlocks);
     }
 
     [TestCase(32L, DownloaderOptions.MoveToMain, 32, false)]
@@ -113,37 +99,20 @@ public async Task Can_reach_terminal_block(long headNumber, int options, int thr
             .InsertBeaconBlocks(17, headNumber, BlockTreeTests.BlockTreeTestScenario.ScenarioBuilder.TotalDifficultyMode.Null);
         BlockTree notSyncedTree = blockTrees.NotSyncedTree;
         BlockTree syncedTree = blockTrees.SyncedTree;
-        Context ctx = new(notSyncedTree);
+        MergeContext ctx = new();
+        ctx.BlockTreeScenario = blockTrees;
+
         DownloaderOptions downloaderOptions = (DownloaderOptions)options;
-        InMemoryReceiptStorage receiptStorage = new();
-        MemDb metadataDb = blockTrees.NotSyncedTreeBuilder.MetadataDb;
-        RopstenSpecProvider specProvider = new();
-        PoSSwitcher posSwitcher = new(new MergeConfig() { TerminalTotalDifficulty = $"{ttd}" }, new SyncConfig(), metadataDb, notSyncedTree,
-            specProvider, LimboLogs.Instance);
-        BeaconPivot beaconPivot = new(new SyncConfig(), metadataDb, notSyncedTree, LimboLogs.Instance);
+        ctx.MergeConfig = new MergeConfig() { TerminalTotalDifficulty = $"{ttd}" };
         if (withBeaconPivot)
-            beaconPivot.EnsurePivot(blockTrees.SyncedTree.FindHeader(16, BlockTreeLookupOptions.None));
-
-        MergeBlockDownloader downloader = new(
-            posSwitcher,
-            beaconPivot,
-            ctx.Feed,
-            ctx.PeerPool,
-            notSyncedTree,
-            Always.Valid,
-            Always.Valid,
-            NullSyncReport.Instance,
-            receiptStorage,
-            specProvider,
-            CreateMergePeerChoiceStrategy(posSwitcher, beaconPivot),
-            new ChainLevelHelper(notSyncedTree, beaconPivot, new SyncConfig(), LimboLogs.Instance),
-            Substitute.For<ISyncProgressResolver>(),
-            LimboLogs.Instance);
+            ctx.BeaconPivot.EnsurePivot(blockTrees.SyncedTree.FindHeader(16, BlockTreeLookupOptions.None));
+
+        BlockDownloader downloader = ctx.BlockDownloader;
 
         SyncPeerMock syncPeer = new(syncedTree, false, Response.AllCorrect, 16000000);
         PeerInfo peerInfo = new(syncPeer);
         await downloader.DownloadBlocks(peerInfo, new BlocksRequest(downloaderOptions), CancellationToken.None);
-        Assert.True(posSwitcher.HasEverReachedTerminalBlock());
+        Assert.True(ctx.PosSwitcher.HasEverReachedTerminalBlock());
     }
 
     [TestCase(32L, DownloaderOptions.MoveToMain, 16, false, 16)]
@@ -165,32 +134,15 @@ public async Task IfNoBeaconPivot_thenStopAtPoS(long headNumber, int options, in
         BlockTree notSyncedTree = blockTrees.NotSyncedTree;
         BlockTree syncedTree = blockTrees.SyncedTree;
 
-        Context ctx = new(notSyncedTree);
+        MergeContext ctx = new();
+        ctx.BlockTreeScenario = blockTrees;
+
         DownloaderOptions downloaderOptions = (DownloaderOptions)options;
-        InMemoryReceiptStorage receiptStorage = new();
-        MemDb metadataDb = blockTrees.NotSyncedTreeBuilder.MetadataDb;
-        RopstenSpecProvider specProvider = new();
-        PoSSwitcher posSwitcher = new(new MergeConfig() { TerminalTotalDifficulty = $"{ttd}" }, new SyncConfig(), metadataDb, notSyncedTree,
-            specProvider, LimboLogs.Instance);
-        BeaconPivot beaconPivot = new(new SyncConfig(), metadataDb, notSyncedTree, LimboLogs.Instance);
+        ctx.MergeConfig = new MergeConfig() { TerminalTotalDifficulty = $"{ttd}" };
         if (withBeaconPivot)
-            beaconPivot.EnsurePivot(blockTrees.SyncedTree.FindHeader(16, BlockTreeLookupOptions.None));
-
-        MergeBlockDownloader downloader = new(
-            posSwitcher,
-            beaconPivot,
-            ctx.Feed,
-            ctx.PeerPool,
-            notSyncedTree,
-            Always.Valid,
-            Always.Valid,
-            NullSyncReport.Instance,
-            receiptStorage,
-            specProvider,
-            CreateMergePeerChoiceStrategy(posSwitcher, beaconPivot),
-            new ChainLevelHelper(notSyncedTree, beaconPivot, new SyncConfig(), LimboLogs.Instance),
-            Substitute.For<ISyncProgressResolver>(),
-            LimboLogs.Instance);
+            ctx.BeaconPivot.EnsurePivot(blockTrees.SyncedTree.FindHeader(16, BlockTreeLookupOptions.None));
+
+        BlockDownloader downloader = ctx.BlockDownloader;
 
         SyncPeerMock syncPeer = new(syncedTree, false, Response.AllCorrect, 16000000);
         PeerInfo peerInfo = new(syncPeer);
@@ -208,32 +160,14 @@ public async Task WillSkipBlocksToIgnore(long pivot, long headNumber, int blocks
             .InsertBeaconPivot(pivot)
             .InsertBeaconHeaders(4, pivot - 1);
 
-        BlockTree notSyncedTree = blockTrees.NotSyncedTree;
         BlockTree syncedTree = blockTrees.SyncedTree;
-        Context ctx = new(notSyncedTree);
-        InMemoryReceiptStorage receiptStorage = new();
-        MemDb metadataDb = blockTrees.NotSyncedTreeBuilder.MetadataDb;
-        PoSSwitcher posSwitcher = new(new MergeConfig() { TerminalTotalDifficulty = "0" }, new SyncConfig(), metadataDb, notSyncedTree,
-            RopstenSpecProvider.Instance, LimboLogs.Instance);
-        BeaconPivot beaconPivot = new(new SyncConfig(), metadataDb, notSyncedTree, LimboLogs.Instance);
-        beaconPivot.EnsurePivot(blockTrees.SyncedTree.FindHeader(pivot, BlockTreeLookupOptions.None));
-        beaconPivot.ProcessDestination = blockTrees.SyncedTree.FindHeader(pivot, BlockTreeLookupOptions.None);
-
-        MergeBlockDownloader downloader = new(
-            posSwitcher,
-            beaconPivot,
-            ctx.Feed,
-            ctx.PeerPool,
-            notSyncedTree,
-            Always.Valid,
-            Always.Valid,
-            NullSyncReport.Instance,
-            receiptStorage,
-            RopstenSpecProvider.Instance,
-            CreateMergePeerChoiceStrategy(posSwitcher, beaconPivot),
-            new ChainLevelHelper(notSyncedTree, beaconPivot, new SyncConfig(), LimboLogs.Instance),
-            Substitute.For<ISyncProgressResolver>(),
-            LimboLogs.Instance);
+        MergeContext ctx = new();
+        ctx.BlockTreeScenario = blockTrees;
+
+        ctx.BeaconPivot.EnsurePivot(blockTrees.SyncedTree.FindHeader(pivot, BlockTreeLookupOptions.None));
+        ctx.BeaconPivot.ProcessDestination = blockTrees.SyncedTree.FindHeader(pivot, BlockTreeLookupOptions.None);
+
+        BlockDownloader downloader = ctx.BlockDownloader;
 
         Response responseOptions = Response.AllCorrect;
 
@@ -260,20 +194,15 @@ public async Task Recalculate_header_total_difficulty()
             .InsertOtherChainToMain(notSyncedTree, 1, 3) // Need to have the header inserted to LRU which mean we need to move the head forward
             .InsertBeaconHeaders(1, 3, tdMode: BlockTreeTests.BlockTreeTestScenario.ScenarioBuilder.TotalDifficultyMode.Null);
 
-        Context ctx = new(notSyncedTree);
-
-        InMemoryReceiptStorage receiptStorage = new();
-        MemDb metadataDb = blockTrees.NotSyncedTreeBuilder.MetadataDb;
-        PoSSwitcher posSwitcher = new(new MergeConfig() { TerminalTotalDifficulty = $"{ttd}" }, new SyncConfig(), metadataDb, notSyncedTree,
-            RopstenSpecProvider.Instance, LimboLogs.Instance);
-
-        BeaconPivot beaconPivot = new(new SyncConfig(), metadataDb, notSyncedTree, LimboLogs.Instance);
+        MergeContext ctx = new();
+        ctx.BlockTreeScenario = blockTrees;
+        ctx.MergeConfig = new MergeConfig() { TerminalTotalDifficulty = $"{ttd}" };
 
         BlockHeader lastHeader = syncedTree.FindHeader(3, BlockTreeLookupOptions.None);
         // Because the FindHeader recalculated the TD.
         lastHeader.TotalDifficulty = 0;
 
-        beaconPivot.EnsurePivot(lastHeader);
+        ctx.BeaconPivot.EnsurePivot(lastHeader);
 
         ISealValidator sealValidator = Substitute.For<ISealValidator>();
         sealValidator.ValidateSeal(Arg.Any<BlockHeader>(), Arg.Any<bool>()).Returns((info =>
@@ -283,22 +212,9 @@ public async Task Recalculate_header_total_difficulty()
             notSyncedTree.FindHeader(header.Hash, BlockTreeLookupOptions.DoNotCreateLevelIfMissing);
             return true;
         }));
+        ctx.SealValidator = sealValidator;
 
-        MergeBlockDownloader downloader = new(
-            posSwitcher,
-            beaconPivot,
-            ctx.Feed,
-            ctx.PeerPool,
-            notSyncedTree,
-            Always.Valid,
-            sealValidator,
-            NullSyncReport.Instance,
-            receiptStorage,
-            RopstenSpecProvider.Instance,
-            CreateMergePeerChoiceStrategy(posSwitcher, beaconPivot),
-            new ChainLevelHelper(notSyncedTree, beaconPivot, new SyncConfig(), LimboLogs.Instance),
-            Substitute.For<ISyncProgressResolver>(),
-            LimboLogs.Instance);
+        BlockDownloader downloader = ctx.BlockDownloader;
 
         SyncPeerMock syncPeer = new(syncedTree, false, Response.AllCorrect, 16000000);
         PeerInfo peerInfo = new(syncPeer);
@@ -316,39 +232,153 @@ public async Task Recalculate_header_total_difficulty()
         lastBestSuggestedBlock.TotalDifficulty.Should().NotBeEquivalentTo(UInt256.Zero);
     }
 
-    private BlockDownloader CreateMergeBlockDownloader(Context ctx)
+    [Test]
+    public async Task Does_not_deadlock_on_replace_peer()
     {
-        IBlockTree blockTree = Substitute.For<IBlockTree>();
-        MemDb metadataDb = new MemDb();
-        var testSpecProvider = new TestSpecProvider(London.Instance);
-        testSpecProvider.TerminalTotalDifficulty = 0;
-        PoSSwitcher posSwitcher = new(new MergeConfig() { TerminalTotalDifficulty = "0" }, new SyncConfig(), metadataDb, blockTree,
-            testSpecProvider, LimboLogs.Instance);
-        BeaconPivot beaconPivot = new(new SyncConfig(), metadataDb, blockTree, LimboLogs.Instance);
-        InMemoryReceiptStorage receiptStorage = new();
-
-        BlockCacheService blockCacheService = new();
-
-        return new MergeBlockDownloader(
-            posSwitcher,
-            beaconPivot,
-            ctx.Feed,
-            ctx.PeerPool,
-            ctx.BlockTree,
-            Always.Valid,
-            Always.Valid,
-            NullSyncReport.Instance,
-            receiptStorage,
-            testSpecProvider,
-            CreateMergePeerChoiceStrategy(posSwitcher, beaconPivot),
-            new ChainLevelHelper(blockTree, beaconPivot, new SyncConfig(), LimboLogs.Instance),
-            Substitute.For<ISyncProgressResolver>(),
-            LimboLogs.Instance);
+        BlockTreeTests.BlockTreeTestScenario.ScenarioBuilder blockTrees = BlockTreeTests.BlockTreeTestScenario
+            .GoesLikeThis()
+            .WithBlockTrees(0, 4)
+            .InsertBeaconPivot(3);
+        MergeContext ctx = new();
+        ctx.MergeConfig = new MergeConfig() { TerminalTotalDifficulty = "0" };
+        ctx.BlockTreeScenario = blockTrees;
+        ctx.BeaconPivot.EnsurePivot(blockTrees.SyncedTree.FindHeader(3, BlockTreeLookupOptions.None));
+
+        ManualResetEventSlim chainLevelHelperBlocker = new ManualResetEventSlim(false);
+        IChainLevelHelper chainLevelHelper = Substitute.For<IChainLevelHelper>();
+        chainLevelHelper
+            .When((clh) => clh.GetNextHeaders(Arg.Any<int>(), Arg.Any<int>()))
+            .Do((args) =>
+            {
+                chainLevelHelperBlocker.Wait();
+            });
+        ctx.ChainLevelHelper = chainLevelHelper;
+
+        IPeerAllocationStrategy peerAllocationStrategy = Substitute.For<IPeerAllocationStrategy>();
+
+        // Setup a peer of any kind
+        ISyncPeer syncPeer1 = Substitute.For<ISyncPeer>();
+        syncPeer1.Node.Returns(new Node(TestItem.PublicKeyA, "127.0.0.1", 9999));
+
+        // Setup so that first allocation goes to sync peer 1
+        peerAllocationStrategy
+            .Allocate(Arg.Any<PeerInfo?>(), Arg.Any<IEnumerable<PeerInfo>>(), Arg.Any<INodeStatsManager>(), Arg.Any<IBlockTree>())
+            .Returns(new PeerInfo(syncPeer1));
+        SyncPeerAllocation peerAllocation = new(peerAllocationStrategy, AllocationContexts.Blocks);
+        peerAllocation.AllocateBestPeer(new List<PeerInfo>(), Substitute.For<INodeStatsManager>(), ctx.BlockTree);
+        ctx.PeerPool
+            .Allocate(Arg.Any<IPeerAllocationStrategy>(), Arg.Any<AllocationContexts>(), Arg.Any<int>())
+            .Returns(Task.FromResult(peerAllocation));
+
+        // Need to be asleep at this time
+        ctx.Feed.FallAsleep();
+
+        CancellationTokenSource cts = new CancellationTokenSource();
+
+        Task ignored = ctx.BlockDownloader.Start(cts.Token);
+        await Task.Delay(TimeSpan.FromMilliseconds(100));
+
+        // Feed should activate and allocate the first peer
+        Task accidentalDeadlockTask = Task.Factory.StartNew(() => ctx.Feed.Activate(), TaskCreationOptions.LongRunning);
+        await Task.Delay(TimeSpan.FromMilliseconds(100));
+
+        // At this point, chain level helper is block, we then trigger replaced.
+        ISyncPeer syncPeer2 = Substitute.For<ISyncPeer>();
+        syncPeer2.Node.Returns(new Node(TestItem.PublicKeyB, "127.0.0.2", 9999));
+        syncPeer2.HeadNumber.Returns(4);
+
+        // It will now get replaced with syncPeer2
+        peerAllocationStrategy.ClearSubstitute();
+        peerAllocationStrategy
+            .Allocate(Arg.Any<PeerInfo?>(), Arg.Any<IEnumerable<PeerInfo>>(), Arg.Any<INodeStatsManager>(), Arg.Any<IBlockTree>())
+            .Returns(new PeerInfo(syncPeer2));
+        peerAllocation.AllocateBestPeer(new List<PeerInfo>(), Substitute.For<INodeStatsManager>(), ctx.BlockTree);
+        await Task.Delay(TimeSpan.FromMilliseconds(100));
+
+        // Release it
+        chainLevelHelperBlocker.Set();
+
+        // Just making sure...
+        await Task.Delay(TimeSpan.FromMilliseconds(100));
+
+        Assert.That(() => accidentalDeadlockTask.IsCompleted, Is.True.After(1000, 100));
+        cts.Cancel();
+        cts.Dispose();
     }
 
-    private IBetterPeerStrategy CreateMergePeerChoiceStrategy(IPoSSwitcher poSSwitcher, IBeaconPivot beaconPivot)
+    class MergeContext : Context
     {
-        TotalDifficultyBetterPeerStrategy preMergePeerStrategy = new(LimboLogs.Instance);
-        return new MergeBetterPeerStrategy(preMergePeerStrategy, poSSwitcher, beaconPivot, LimboLogs.Instance);
+        protected override ISpecProvider SpecProvider => _specProvider ??= new MainnetSpecProvider(); // PoSSwitcher changes TTD, so can't use MainnetSpecProvider.Instance
+
+        private BlockTreeTests.BlockTreeTestScenario.ScenarioBuilder? _blockTreeScenario = null;
+        public BlockTreeTests.BlockTreeTestScenario.ScenarioBuilder BlockTreeScenario
+        {
+            get =>
+                _blockTreeScenario ??
+                new BlockTreeTests.BlockTreeTestScenario.ScenarioBuilder();
+            set => _blockTreeScenario = value;
+        }
+
+        public override IBlockTree BlockTree => _blockTreeScenario?.NotSyncedTree ?? base.BlockTree;
+
+        private MemDb? _metadataDb = null;
+        private MemDb MetadataDb => (_metadataDb ?? _blockTreeScenario?.NotSyncedTreeBuilder?.MetadataDb) ?? (_metadataDb ??= new MemDb());
+
+        private MergeConfig _mergeConfig;
+        public MergeConfig MergeConfig
+        {
+            get => _mergeConfig ??= new MergeConfig() { TerminalTotalDifficulty = "58750000000000000000000" }; // Main block downloader test assume pre-merge
+            set => _mergeConfig = value;
+        }
+
+        private BeaconPivot? _beaconPivot = null;
+        public BeaconPivot BeaconPivot => _beaconPivot ??= new(new SyncConfig(), MetadataDb, BlockTree, LimboLogs.Instance);
+
+        private PoSSwitcher? _posSwitcher = null;
+        public PoSSwitcher PosSwitcher => _posSwitcher ??= new(
+            MergeConfig,
+            new SyncConfig(),
+            MetadataDb,
+            BlockTree,
+            SpecProvider,
+            LimboLogs.Instance);
+
+        protected override IBetterPeerStrategy BetterPeerStrategy => _betterPeerStrategy ??=
+            new MergeBetterPeerStrategy(new TotalDifficultyBetterPeerStrategy(LimboLogs.Instance), PosSwitcher, BeaconPivot, LimboLogs.Instance);
+
+        private IChainLevelHelper? _chainLevelHelper = null;
+        public IChainLevelHelper ChainLevelHelper
+        {
+            get =>
+                _chainLevelHelper ??= new ChainLevelHelper(
+                    BlockTree,
+                    BeaconPivot,
+                    new SyncConfig(),
+                    LimboLogs.Instance);
+            set => _chainLevelHelper = value;
+        }
+
+        private MergeBlockDownloader? _mergeBlockDownloader;
+        public override BlockDownloader BlockDownloader
+        {
+            get
+            {
+                return _mergeBlockDownloader ?? new(
+                    PosSwitcher,
+                    BeaconPivot,
+                    Feed,
+                    PeerPool,
+                    BlockTree,
+                    BlockValidator,
+                    SealValidator,
+                    NullSyncReport.Instance,
+                    ReceiptStorage,
+                    SpecProvider,
+                    BetterPeerStrategy,
+                    ChainLevelHelper,
+                    Substitute.For<ISyncProgressResolver>(),
+                    LimboLogs.Instance);
+            }
+        }
     }
 }
```

### src/Nethermind/Nethermind.Synchronization.Test/BlockDownloaderTests.cs
```diff
@@ -16,6 +16,7 @@
 using Nethermind.Consensus.Validators;
 using Nethermind.Core;
 using Nethermind.Core.Crypto;
+using Nethermind.Core.Specs;
 using Nethermind.Core.Test.Builders;
 using Nethermind.Crypto;
 using Nethermind.Db;
@@ -74,8 +75,7 @@ public async Task Happy_path(long headNumber, int options, int threshold)
             Context ctx = new();
             DownloaderOptions downloaderOptions = (DownloaderOptions)options;
             bool withReceipts = downloaderOptions == DownloaderOptions.WithReceipts;
-            InMemoryReceiptStorage receiptStorage = new();
-            BlockDownloader downloader = new(ctx.Feed, ctx.PeerPool, ctx.BlockTree, Always.Valid, Always.Valid, NullSyncReport.Instance, receiptStorage, RopstenSpecProvider.Instance, new BlocksSyncPeerAllocationStrategyFactory(), CreatePeerChoiceStrategy(), LimboLogs.Instance);
+            BlockDownloader downloader = ctx.BlockDownloader;
 
             Response responseOptions = Response.AllCorrect;
             if (withReceipts)
@@ -108,15 +108,15 @@ public async Task Happy_path(long headNumber, int options, int threshold)
                 }
             }
 
-            receiptStorage.Count.Should().Be(withReceipts ? receiptCount : 0);
+            ctx.ReceiptStorage.Count.Should().Be(withReceipts ? receiptCount : 0);
         }
 
         [Test]
         public async Task Ancestor_lookup_simple()
         {
             Context ctx = new();
             ctx.BlockTree = Build.A.BlockTree().OfChainLength(1024).TestObject;
-            BlockDownloader downloader = CreateBlockDownloader(ctx);
+            BlockDownloader downloader = ctx.BlockDownloader;
 
             Response blockResponseOptions = Response.AllCorrect;
             SyncPeerMock syncPeer = new(2048 + 1, false, blockResponseOptions);
@@ -145,7 +145,7 @@ public async Task Ancestor_lookup_headers()
         {
             Context ctx = new();
             ctx.BlockTree = Build.A.BlockTree().OfChainLength(1024).TestObject;
-            BlockDownloader downloader = CreateBlockDownloader(ctx);
+            BlockDownloader downloader = ctx.BlockDownloader;
 
             Response responseOptions = Response.AllCorrect;
             SyncPeerMock syncPeer = new(2048 + 1, false, responseOptions);
@@ -172,7 +172,7 @@ public void Ancestor_failure()
         {
             Context ctx = new();
             ctx.BlockTree = Build.A.BlockTree().OfChainLength(2048 + 1).TestObject;
-            BlockDownloader downloader = CreateBlockDownloader(ctx);
+            BlockDownloader downloader = ctx.BlockDownloader;
 
             Response blockResponseOptions = Response.AllCorrect;
             SyncPeerMock syncPeer = new(2072 + 1, true, blockResponseOptions);
@@ -188,7 +188,7 @@ public void Ancestor_failure_blocks()
         {
             Context ctx = new();
             ctx.BlockTree = Build.A.BlockTree().OfChainLength(2048 + 1).TestObject;
-            BlockDownloader downloader = CreateBlockDownloader(ctx);
+            BlockDownloader downloader = ctx.BlockDownloader;
 
             Response responseOptions = Response.AllCorrect;
             SyncPeerMock syncPeer = new(2072 + 1, true, responseOptions);
@@ -207,11 +207,11 @@ public void Ancestor_failure_blocks()
         [TestCase(0, false)]
         public async Task Can_sync_with_peer_when_it_times_out_on_full_batch(int ignoredBlocks, bool mergeDownloader)
         {
-            Context ctx = new();
+            Context ctx = mergeDownloader ? new MergeContext() : new Context();
             SyncBatchSize syncBatchSize = new SyncBatchSize(LimboLogs.Instance);
             syncBatchSize.ExpandUntilMax();
             ctx.SyncBatchSize = syncBatchSize;
-            BlockDownloader downloader = mergeDownloader ? CreateMergeBlockDownloader(ctx) : CreateBlockDownloader(ctx);
+            BlockDownloader downloader = ctx.BlockDownloader;
 
             ISyncPeer syncPeer = Substitute.For<ISyncPeer>();
             syncPeer.GetBlockHeaders(Arg.Any<long>(), Arg.Any<int>(), Arg.Any<int>(), Arg.Any<CancellationToken>())
@@ -245,8 +245,8 @@ public async Task Can_sync_with_peer_when_it_times_out_on_full_batch(int ignored
         [TestCase(32, 16, 100, false)]
         public async Task Can_sync_partially_when_only_some_bodies_is_available(int blockCount, int availableBlock, int minResponseLength, bool mergeDownloader)
         {
-            Context ctx = new();
-            BlockDownloader downloader = mergeDownloader ? CreateMergeBlockDownloader(ctx) : CreateBlockDownloader(ctx);
+            Context ctx = mergeDownloader ? new MergeContext() : new Context();
+            BlockDownloader downloader = ctx.BlockDownloader;
 
             ISyncPeer syncPeer = Substitute.For<ISyncPeer>();
             syncPeer.GetBlockHeaders(Arg.Any<long>(), Arg.Any<int>(), Arg.Any<int>(), Arg.Any<CancellationToken>())
@@ -295,7 +295,7 @@ public async Task Can_sync_partially_when_only_some_bodies_is_available(int bloc
         public async Task Headers_already_known()
         {
             Context ctx = new();
-            BlockDownloader downloader = CreateBlockDownloader(ctx);
+            BlockDownloader downloader = ctx.BlockDownloader;
 
             ISyncPeer syncPeer = Substitute.For<ISyncPeer>();
             syncPeer.GetBlockHeaders(Arg.Any<long>(), Arg.Any<int>(), Arg.Any<int>(), Arg.Any<CancellationToken>())
@@ -319,7 +319,7 @@ public async Task Headers_already_known()
         public async Task Peer_only_advertise_one_header()
         {
             Context ctx = new();
-            BlockDownloader downloader = CreateBlockDownloader(ctx);
+            BlockDownloader downloader = ctx.BlockDownloader;
 
             ISyncPeer syncPeer = Substitute.For<ISyncPeer>();
             syncPeer.GetBlockHeaders(Arg.Any<long>(), Arg.Any<int>(), Arg.Any<int>(), Arg.Any<CancellationToken>())
@@ -339,7 +339,7 @@ public async Task Peer_only_advertise_one_header()
         public async Task Peer_sends_just_one_item_when_advertising_more_blocks_but_no_bodies(long headNumber)
         {
             Context ctx = new();
-            BlockDownloader downloader = CreateBlockDownloader(ctx);
+            BlockDownloader downloader = ctx.BlockDownloader;
 
             ISyncPeer syncPeer = Substitute.For<ISyncPeer>();
             syncPeer.GetBlockHeaders(Arg.Any<long>(), Arg.Any<int>(), Arg.Any<int>(), Arg.Any<CancellationToken>())
@@ -362,7 +362,7 @@ public async Task Peer_sends_just_one_item_when_advertising_more_blocks_but_no_b
         public async Task Throws_on_null_best_peer()
         {
             Context ctx = new();
-            BlockDownloader downloader = CreateBlockDownloader(ctx);
+            BlockDownloader downloader = ctx.BlockDownloader;
             Task task1 = downloader.DownloadHeaders(null, new BlocksRequest(DownloaderOptions.WithBodies, 0), CancellationToken.None);
             await task1.ContinueWith(t => Assert.True(t.IsFaulted));
 
@@ -382,7 +382,7 @@ public async Task Throws_on_inconsistent_batch()
             syncPeer.TotalDifficulty.Returns(UInt256.MaxValue);
             syncPeer.HeadNumber.Returns(1024);
 
-            BlockDownloader downloader = CreateBlockDownloader(ctx);
+            BlockDownloader downloader = ctx.BlockDownloader;
             Task task = downloader.DownloadHeaders(peerInfo, new BlocksRequest(DownloaderOptions.WithBodies, 0), CancellationToken.None);
             await task.ContinueWith(t => Assert.True(t.IsFaulted));
         }
@@ -391,7 +391,8 @@ public async Task Throws_on_inconsistent_batch()
         public async Task Throws_on_invalid_seal()
         {
             Context ctx = new();
-            BlockDownloader downloader = new(ctx.Feed, ctx.PeerPool, ctx.BlockTree, Always.Valid, Always.Invalid, NullSyncReport.Instance, new InMemoryReceiptStorage(), RopstenSpecProvider.Instance, new BlocksSyncPeerAllocationStrategyFactory(), CreatePeerChoiceStrategy(), LimboLogs.Instance);
+            ctx.SealValidator = Always.Invalid;
+            BlockDownloader downloader = ctx.BlockDownloader;
 
             ISyncPeer syncPeer = Substitute.For<ISyncPeer>();
             syncPeer.TotalDifficulty.Returns(UInt256.MaxValue);
@@ -409,7 +410,8 @@ public async Task Throws_on_invalid_seal()
         public async Task Throws_on_invalid_header()
         {
             Context ctx = new();
-            BlockDownloader downloader = new(ctx.Feed, ctx.PeerPool, ctx.BlockTree, Always.Invalid, Always.Valid, NullSyncReport.Instance, new InMemoryReceiptStorage(), RopstenSpecProvider.Instance, new BlocksSyncPeerAllocationStrategyFactory(), CreatePeerChoiceStrategy(), LimboLogs.Instance);
+            ctx.BlockValidator = Always.Invalid;
+            BlockDownloader downloader = ctx.BlockDownloader;
 
             ISyncPeer syncPeer = Substitute.For<ISyncPeer>();
             syncPeer.TotalDifficulty.Returns(UInt256.MaxValue);
@@ -476,7 +478,8 @@ public bool ValidateProcessedBlock(Block processedBlock, TxReceipt[] receipts, B
         public async Task Can_cancel_seal_validation()
         {
             Context ctx = new();
-            BlockDownloader downloader = new(ctx.Feed, ctx.PeerPool, ctx.BlockTree, Always.Valid, new SlowSealValidator(), NullSyncReport.Instance, new InMemoryReceiptStorage(), RopstenSpecProvider.Instance, new BlocksSyncPeerAllocationStrategyFactory(), CreatePeerChoiceStrategy(), LimboLogs.Instance);
+            ctx.SealValidator = new SlowSealValidator();
+            BlockDownloader downloader = ctx.BlockDownloader;
 
             ISyncPeer syncPeer = Substitute.For<ISyncPeer>();
             syncPeer.GetBlockHeaders(Arg.Any<long>(), Arg.Any<int>(), Arg.Any<int>(), Arg.Any<CancellationToken>())
@@ -506,7 +509,8 @@ public async Task Can_cancel_seal_validation()
         public async Task Can_cancel_adding_headers()
         {
             Context ctx = new();
-            BlockDownloader downloader = new(ctx.Feed, ctx.PeerPool, ctx.BlockTree, new SlowHeaderValidator(), Always.Valid, NullSyncReport.Instance, new InMemoryReceiptStorage(), RopstenSpecProvider.Instance, new BlocksSyncPeerAllocationStrategyFactory(), CreatePeerChoiceStrategy(), LimboLogs.Instance);
+            ctx.BlockValidator = new SlowHeaderValidator();
+            BlockDownloader downloader = ctx.BlockDownloader;
 
             ISyncPeer syncPeer = Substitute.For<ISyncPeer>();
             syncPeer.GetBlockHeaders(Arg.Any<long>(), Arg.Any<int>(), Arg.Any<int>(), Arg.Any<CancellationToken>())
@@ -539,7 +543,8 @@ public async Task Validate_always_the_last_seal_and_random_seal_in_the_package()
             ISealValidator sealValidator = Substitute.For<ISealValidator>();
             sealValidator.ValidateSeal(Arg.Any<BlockHeader>(), Arg.Any<bool>()).Returns(true);
             Context ctx = new();
-            BlockDownloader downloader = new BlockDownloader(ctx.Feed, ctx.PeerPool, ctx.BlockTree, Always.Valid, sealValidator, NullSyncReport.Instance, new InMemoryReceiptStorage(), RopstenSpecProvider.Instance, new BlocksSyncPeerAllocationStrategyFactory(), CreatePeerChoiceStrategy(), LimboLogs.Instance); ;
+            ctx.SealValidator = sealValidator;
+            BlockDownloader downloader = ctx.BlockDownloader;
 
             BlockHeader[] blockHeaders = await ctx.ResponseBuilder.BuildHeaderResponse(0, 512, Response.AllCorrect);
             ISyncPeer syncPeer = Substitute.For<ISyncPeer>();
@@ -637,7 +642,7 @@ public bool TryGetSatelliteProtocol<T>(string protocol, out T protocolHandler) w
         public async Task Faults_on_get_headers_faulting()
         {
             Context ctx = new();
-            BlockDownloader downloader = CreateBlockDownloader(ctx);
+            BlockDownloader downloader = ctx.BlockDownloader;
 
             ISyncPeer syncPeer = new ThrowingPeer(1000, UInt256.MaxValue);
             PeerInfo peerInfo = new(syncPeer);
@@ -650,7 +655,7 @@ public async Task Faults_on_get_headers_faulting()
         public async Task Throws_on_block_task_exception()
         {
             Context ctx = new();
-            BlockDownloader downloader = CreateBlockDownloader(ctx);
+            BlockDownloader downloader = ctx.BlockDownloader;
 
             ISyncPeer syncPeer = Substitute.For<ISyncPeer>();
             syncPeer.TotalDifficulty.Returns(UInt256.MaxValue);
@@ -681,7 +686,7 @@ public async Task Throws_on_receipt_task_exception_when_downloading_receipts(int
         {
             Context ctx = new();
             DownloaderOptions downloaderOptions = (DownloaderOptions)options;
-            BlockDownloader downloader = CreateBlockDownloader(ctx);
+            BlockDownloader downloader = ctx.BlockDownloader;
 
             ISyncPeer syncPeer = Substitute.For<ISyncPeer>();
             syncPeer.TotalDifficulty.Returns(UInt256.MaxValue);
@@ -723,7 +728,7 @@ public async Task Throws_on_null_receipt_downloaded(int options, bool shouldThro
             Context ctx = new();
             DownloaderOptions downloaderOptions = (DownloaderOptions)options;
             bool withReceipts = downloaderOptions == DownloaderOptions.WithReceipts;
-            BlockDownloader downloader = CreateBlockDownloader(ctx);
+            BlockDownloader downloader = ctx.BlockDownloader;
 
             Response responseOptions = Response.AllCorrect;
             if (withReceipts)
@@ -781,7 +786,7 @@ public async Task Throws_on_null_receipt_downloaded(int options, bool shouldThro
         public async Task Throws_on_block_bodies_count_higher_than_receipts_list_count(int threshold)
         {
             Context ctx = new();
-            BlockDownloader downloader = CreateBlockDownloader(ctx);
+            BlockDownloader downloader = ctx.BlockDownloader;
 
             ISyncPeer syncPeer = Substitute.For<ISyncPeer>();
             syncPeer.TotalDifficulty.Returns(UInt256.MaxValue);
@@ -812,8 +817,7 @@ public async Task Throws_on_block_bodies_count_higher_than_receipts_list_count(i
         public async Task Does_throw_on_transaction_count_different_than_receipts_count_in_block(int threshold)
         {
             Context ctx = new();
-            InMemoryReceiptStorage inMemoryReceiptStorage = new();
-            BlockDownloader downloader = CreateBlockDownloader(ctx);
+            BlockDownloader downloader = ctx.BlockDownloader;
 
             ISyncPeer syncPeer = Substitute.For<ISyncPeer>();
             syncPeer.TotalDifficulty.Returns(UInt256.MaxValue);
@@ -844,7 +848,7 @@ public async Task Does_throw_on_transaction_count_different_than_receipts_count_
         public async Task Throws_on_incorrect_receipts_root(int threshold)
         {
             Context ctx = new();
-            BlockDownloader downloader = CreateBlockDownloader(ctx);
+            BlockDownloader downloader = ctx.BlockDownloader;
 
             ISyncPeer syncPeer = Substitute.For<ISyncPeer>();
             syncPeer.TotalDifficulty.Returns(UInt256.MaxValue);
@@ -870,31 +874,6 @@ public async Task Throws_on_incorrect_receipts_root(int threshold)
             await action.Should().ThrowAsync<EthSyncException>();
         }
 
-        private BlockDownloader CreateBlockDownloader(Context ctx)
-        {
-            InMemoryReceiptStorage receiptStorage = new();
-            return new BlockDownloader(
-                ctx.Feed,
-                ctx.PeerPool,
-                ctx.BlockTree,
-                Always.Valid,
-                Always.Valid,
-                NullSyncReport.Instance,
-                receiptStorage,
-                RopstenSpecProvider.Instance,
-                new BlocksSyncPeerAllocationStrategyFactory(),
-                CreatePeerChoiceStrategy(),
-                LimboLogs.Instance,
-                ctx.SyncBatchSize
-            );
-        }
-
-        private IBetterPeerStrategy CreatePeerChoiceStrategy()
-        {
-            ISyncProgressResolver syncProgressResolver = Substitute.For<ISyncProgressResolver>();
-            return new TotalDifficultyBetterPeerStrategy(LimboLogs.Instance);
-        }
-
         [Flags]
         private enum Response
         {
@@ -910,46 +889,119 @@ private enum Response
 
         private class Context
         {
-            public IBlockTree? BlockTree { get; set; }
-            public ISyncPeerPool PeerPool { get; }
-            public ISyncFeed<BlocksRequest> Feed { get; }
-            public ResponseBuilder ResponseBuilder { get; }
-            public Dictionary<long, Keccak> TestHeaderMapping { get; }
-            public ISyncModeSelector SyncModeSelector { get; }
+            private Block genesis = Build.A.Block.Genesis.TestObject;
+            private MemDb _stateDb = new();
+            private MemDb _blockInfoDb = new();
+            private SyncConfig syncConfig = new();
+            private IBlockTree? _blockTree { get; set; }
+            private Dictionary<long, Keccak> TestHeaderMapping { get; }
+            public InMemoryReceiptStorage ReceiptStorage = new();
 
-            public SyncBatchSize? SyncBatchSize { get; set; } = new SyncBatchSize(LimboLogs.Instance);
+            private SyncBatchSize? _syncBatchSize;
 
-            public Context(BlockTree? blockTree = null)
+            public SyncBatchSize? SyncBatchSize
             {
-                Block genesis = Build.A.Block.Genesis.TestObject;
-                MemDb blockInfoDb = new();
-                BlockTree = blockTree;
-                BlockTree ??= new BlockTree(new MemDb(), new MemDb(), blockInfoDb, new ChainLevelInfoRepository(blockInfoDb), MainnetSpecProvider.Instance, NullBloomStorage.Instance, LimboLogs.Instance);
-                BlockTree.SuggestBlock(genesis);
+                get => _syncBatchSize ??= new SyncBatchSize(LimboLogs.Instance);
+                set => _syncBatchSize = value;
+            }
 
-                TestHeaderMapping = new Dictionary<long, Keccak>();
-                TestHeaderMapping.Add(0, genesis.Hash!);
+            protected ISpecProvider? _specProvider;
+            protected virtual ISpecProvider SpecProvider => _specProvider ??= MainnetSpecProvider.Instance;
+
+            public virtual IBlockTree BlockTree
+            {
+                get
+                {
+                    if (_blockTree == null)
+                    {
+                        _blockTree = new BlockTree(new MemDb(), new MemDb(), _blockInfoDb, new ChainLevelInfoRepository(_blockInfoDb), SpecProvider, NullBloomStorage.Instance, LimboLogs.Instance);
+                        _blockTree.SuggestBlock(genesis);
+                    }
+
+                    return _blockTree;
+                }
+                set
+                {
+                    _blockTree = value;
+                }
+            }
 
-                PeerPool = Substitute.For<ISyncPeerPool>();
-                Feed = Substitute.For<ISyncFeed<BlocksRequest>>();
+            private ISyncPeerPool _peerPool;
+            public ISyncPeerPool PeerPool => _peerPool ??= Substitute.For<ISyncPeerPool>();
 
-                MemDb stateDb = new();
+            private ResponseBuilder? _responseBuilder = null;
+            public ResponseBuilder ResponseBuilder =>
+                _responseBuilder ??= new ResponseBuilder(BlockTree, TestHeaderMapping);
 
-                SyncConfig syncConfig = new();
-                ProgressTracker progressTracker = new(BlockTree, stateDb, LimboLogs.Instance);
-                SyncProgressResolver syncProgressResolver = new(
+            private ProgressTracker? _progressTracker;
+
+            private ProgressTracker ProgressTracker => _progressTracker ??=
+                new(BlockTree, _stateDb, LimboLogs.Instance);
+
+            private ISyncProgressResolver? _syncProgressResolver;
+
+            private ISyncProgressResolver? SyncProgressResolver => _syncProgressResolver ??=
+                new SyncProgressResolver(
                     BlockTree,
-                    NullReceiptStorage.Instance,
-                    stateDb,
-                    new TrieStore(stateDb, LimboLogs.Instance),
-                    progressTracker,
+                    ReceiptStorage,
+                    _stateDb,
+                    new TrieStore(_stateDb, LimboLogs.Instance),
+                    ProgressTracker,
                     syncConfig,
                     LimboLogs.Instance);
-                TotalDifficultyBetterPeerStrategy bestPeerStrategy = new(LimboLogs.Instance);
-                SyncModeSelector = new MultiSyncModeSelector(syncProgressResolver, PeerPool, syncConfig, No.BeaconSync, bestPeerStrategy, LimboLogs.Instance);
-                Feed = new FullSyncFeed(SyncModeSelector, LimboLogs.Instance);
 
-                ResponseBuilder = new ResponseBuilder(BlockTree, TestHeaderMapping);
+            private MultiSyncModeSelector _syncModeSelector;
+
+            protected IBetterPeerStrategy _betterPeerStrategy;
+
+            protected virtual IBetterPeerStrategy BetterPeerStrategy =>
+                _betterPeerStrategy ??= new TotalDifficultyBetterPeerStrategy(LimboLogs.Instance);
+
+            private ISyncModeSelector SyncModeSelector => _syncModeSelector ??=
+                new MultiSyncModeSelector(SyncProgressResolver, PeerPool, syncConfig, No.BeaconSync, BetterPeerStrategy, LimboLogs.Instance);
+
+            private FullSyncFeed _feed;
+            public ActivatedSyncFeed<BlocksRequest> Feed => _feed ??= new FullSyncFeed(SyncModeSelector, LimboLogs.Instance);
+
+            private ISealValidator? _sealValidator;
+            public ISealValidator SealValidator
+            {
+                get => _sealValidator ??= Always.Valid;
+                set => _sealValidator = value;
+            }
+
+            private IBlockValidator _blockValidator;
+            public IBlockValidator BlockValidator
+            {
+                get => _blockValidator ??= Always.Valid;
+                set => _blockValidator = value;
+            }
+
+            private BlockDownloader _blockDownloader;
+            public virtual BlockDownloader BlockDownloader => _blockDownloader ??= new BlockDownloader(
+                Feed,
+                PeerPool,
+                BlockTree,
+                BlockValidator,
+                SealValidator,
+                NullSyncReport.Instance,
+                ReceiptStorage,
+                SpecProvider,
+                new BlocksSyncPeerAllocationStrategyFactory(),
+                BetterPeerStrategy,
+                LimboLogs.Instance,
+                SyncBatchSize
+            );
+
+            public Context(BlockTree? blockTree = null)
+            {
+                if (blockTree != null)
+                {
+                    BlockTree = blockTree;
+                }
+
+                TestHeaderMapping = new Dictionary<long, Keccak>();
+                TestHeaderMapping.Add(0, genesis.Hash!);
             }
         }
 
```

### src/Nethermind/Nethermind.Synchronization/ParallelSync/SyncDispatcher.cs
```diff
@@ -35,7 +35,7 @@ protected SyncDispatcher(
             syncFeed.StateChanged += SyncFeedOnStateChanged;
         }
 
-        private TaskCompletionSource<object?>? _dormantStateTask = new();
+        private TaskCompletionSource<object?>? _dormantStateTask = new(TaskCreationOptions.RunContinuationsAsynchronously);
 
         protected abstract Task Dispatch(PeerInfo peerInfo, T request, CancellationToken cancellationToken);
 
@@ -86,7 +86,10 @@ public async Task Start(CancellationToken cancellationToken)
                         if (allocatedPeer is not null)
                         {
                             if (Logger.IsTrace) Logger.Trace($"SyncDispatcher request: {request}, AllocatedPeer {allocation.Current}");
-                            Task task = DoDispatch(cancellationToken, allocatedPeer, request, allocation);
+
+                            // Use Task.Run to make sure it queues it instead of running part of it synchronously.
+                            Task task = Task.Run(() => DoDispatch(cancellationToken, allocatedPeer, request,
+                                allocation), cancellationToken);
 
                             if (!Feed.IsMultiFeed)
                             {
@@ -217,7 +220,7 @@ private void UpdateState(SyncFeedState state)
                     TaskCompletionSource<object?>? newDormantStateTask = null;
                     if (state == SyncFeedState.Dormant)
                     {
-                        newDormantStateTask = new TaskCompletionSource<object?>();
+                        newDormantStateTask = new TaskCompletionSource<object?>(TaskCreationOptions.RunContinuationsAsynchronously);
                     }
 
                     var previous = Interlocked.Exchange(ref _dormantStateTask, newDormantStateTask);
```
