# [?] fix: prevent negative RequestSize crash when beacon pivot destination advances mid-sync (#11478)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-05-06
Source: https://github.com/NethermindEth/nethermind/commit/61c20c5196800aef79a48b0f82ff276910482d55
Type: security-commit

## Details
fix: prevent negative RequestSize crash when beacon pivot destination advances mid-sync (#11478)

* fix: prevent negative RequestSize crash when beacon pivot destination advances mid-sync

`HeadersSyncFeed.ShouldBuildANewBatch` checked
`_lowestRequestedHeaderNumber == HeadersDestinationNumber`. For beacon
headers, `HeadersDestinationNumber` is `BeaconPivot.PivotDestinationNumber`,
which tracks `Head.Number - Reorganization.MaxDepth + 1` and so advances
upward as the chain head progresses. When it stepped above
`_lowestRequestedHeaderNumber` mid-sync, the `==` check missed it,
`BuildNewBatch` produced a negative `RequestSize`, and
`HeaderStore.FindReversedHeaders` crashed with
`ArgumentOutOfRangeException` on `new Dictionary<>(negativeCount)`.

Widen the guard to `<=` and add a regression test that reproduces the
scenario via mocked `IBeaconPivot`.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

* chore: shorten inline comments per review

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

## Patch
### src/Nethermind/Nethermind.Merge.Plugin.Test/Synchronization/BeaconHeadersSyncTests.cs
```diff
@@ -302,6 +302,47 @@ public void Feed_connect_invalid_chain()
         storedLastValidHash.Should().Be(lastValidHeader);
     }
 
+    [Test]
+    public async Task Does_not_request_headers_when_destination_advances_past_lowest_requested()
+    {
+        // PivotDestinationNumber rising above _lowestRequestedHeaderNumber mid-sync must not produce
+        // a batch with negative RequestSize.
+        IBlockTree blockTree = Substitute.For<IBlockTree>();
+        blockTree.SyncPivot.Returns((1000, Keccak.Zero));
+        blockTree.LowestInsertedBeaconHeader.Returns((BlockHeader?)null);
+
+        IBeaconPivot beaconPivot = Substitute.For<IBeaconPivot>();
+        beaconPivot.PivotNumber.Returns(2000);
+        beaconPivot.PivotHash.Returns(TestItem.KeccakA);
+        beaconPivot.PivotParentHash.Returns(TestItem.KeccakB);
+        beaconPivot.PivotDestinationNumber.Returns(1100);
+
+        Context ctx = new()
+        {
+            BlockTree = blockTree,
+            SyncConfig = new SyncConfig
+            {
+                FastSync = true,
+                PivotNumber = 1000,
+                PivotHash = Keccak.Zero.ToString(),
+                PivotTotalDifficulty = "1000"
+            },
+            BeaconPivot = beaconPivot,
+        };
+        BeaconHeadersSyncFeed feed = ctx.Feed;
+        feed.InitializeFeed();
+
+        using HeadersSyncBatch? first = await feed.PrepareRequest();
+        first.Should().NotBeNull();
+        first!.RequestSize.Should().BeGreaterThan(0);
+
+        // Simulate Head advancing so that PivotDestinationNumber moves above _lowestRequestedHeaderNumber.
+        beaconPivot.PivotDestinationNumber.Returns(first.StartNumber + 10);
+
+        using HeadersSyncBatch? second = await feed.PrepareRequest();
+        second.Should().BeNull();
+    }
+
     [Test]
     public async Task When_pivot_changed_during_header_sync_after_chain_merged__do_not_return_null_request()
     {
```

### src/Nethermind/Nethermind.Synchronization/FastBlocks/HeadersSyncFeed.cs
```diff
@@ -256,7 +256,9 @@ private UInt256 TryGetPivotTotalDifficulty(Hash256 headerHash)
 
         private bool ShouldBuildANewBatch()
         {
-            bool destinationHeaderRequested = _lowestRequestedHeaderNumber == HeadersDestinationNumber;
+            // `<=` because `HeadersDestinationNumber` (beacon: `PivotDestinationNumber`) can advance
+            // above `_lowestRequestedHeaderNumber` mid-sync; `==` would let `BuildNewBatch` produce a negative `RequestSize`.
+            bool destinationHeaderRequested = _lowestRequestedHeaderNumber <= HeadersDestinationNumber;
 
             bool isImmediateSync = !_syncConfig.DownloadHeadersInFastSync;
 
```
