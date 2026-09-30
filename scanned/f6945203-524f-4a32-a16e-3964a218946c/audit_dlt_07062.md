# [?] Fix Holesky crash on restart (#6193)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2023-10-26
Source: https://github.com/NethermindEth/nethermind/commit/218ed6252cc2b8b101e1459e43ccad6187997ae5
Type: security-commit

## Details
Fix Holesky crash on restart (#6193)

* Create Holesky test case (#6183)

* Ensure Genesis is loaded during validation

* Preserve `WasProcessed` on semantically equivalent `BlockInfo`

* Use direct constructor instead of builder

- Something wrong there

* Use `BlockTreeBuilder`

## Patch
### src/Nethermind/Nethermind.Blockchain.Test/BlockTreeTests.cs
```diff
@@ -3,11 +3,13 @@
 
 using System;
 using System.Collections.Generic;
+using System.Collections.Immutable;
 using System.Threading;
 using System.Threading.Tasks;
 using FluentAssertions;
 using Nethermind.Blockchain.Blocks;
 using Nethermind.Blockchain.Find;
+using Nethermind.Blockchain.Headers;
 using Nethermind.Blockchain.Synchronization;
 using Nethermind.Blockchain.Visitors;
 using Nethermind.Core;
@@ -1818,6 +1820,96 @@ public void Find_handles_invalid_blocks(Func<BlockTree, Keccak?, BlockTreeLookup
             findFunction(blockTree, invalidBlock.Hash, lookupOptions).Should().Be(foundInvalid ? invalidBlock.Header : null);
         }
 
+        [Test]
+        public void On_restart_loads_already_processed_genesis_block()
+        {
+            TestMemDb blocksDb = new();
+            TestMemDb headersDb = new();
+            TestMemDb blockNumberDb = new();
+            TestMemDb blocksInfosDb = new();
+            ChainLevelInfoRepository chainLevelInfoRepository = new(blocksInfosDb);
+
+            // First run
+            {
+                Keccak uncleHash = new("0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347");
+                BlockTree tree = Build.A.BlockTree(HoleskySpecProvider.Instance)
+                    .WithBlockStore(new BlockStore(blocksDb))
+                    .WithBlocksNumberDb(blockNumberDb)
+                    .WithHeadersDb(headersDb)
+                    .WithChainLevelInfoRepository(chainLevelInfoRepository)
+                    .WithoutSettingHead
+                    .TestObject;
+
+                // Holesky genesis
+                Block genesis = new(new(
+                    parentHash: Keccak.Zero,
+                    unclesHash: uncleHash,
+                    beneficiary: new Address(Keccak.Zero),
+                    difficulty: 1,
+                    number: 0,
+                    gasLimit: 25000000,
+                    timestamp: 1695902100,
+                    extraData: Array.Empty<byte>())
+                {
+                    Hash = new Keccak("0xb5f7f912443c940f21fd611f12828d75b534364ed9e95ca4e307729a4661bde4"),
+                    Bloom = Core.Bloom.Empty
+                });
+
+                // Second block
+                Block second = new(new(
+                    parentHash: genesis.Header.Hash!,
+                    unclesHash: uncleHash,
+                    beneficiary: new Address(Keccak.Zero),
+                    difficulty: 0,
+                    number: genesis.Header.Number + 1,
+                    gasLimit: 25000000,
+                    timestamp: genesis.Header.Timestamp + 100,
+                    extraData: Array.Empty<byte>())
+                {
+                    Hash = new Keccak("0x1111111111111111111111111111111111111111111111111111111111111111"),
+                    Bloom = Core.Bloom.Empty,
+                    StateRoot = genesis.Header.Hash,
+                });
+
+                // Third block
+                Block third = new(new(
+                    parentHash: second.Header.Hash!,
+                    unclesHash: uncleHash,
+                    beneficiary: new Address(Keccak.Zero),
+                    difficulty: 0,
+                    number: second.Header.Number + 1,
+                    gasLimit: 25000000,
+                    timestamp: second.Header.Timestamp + 100,
+                    extraData: Array.Empty<byte>())
+                {
+                    Hash = new Keccak("0x2222222222222222222222222222222222222222222222222222222222222222"),
+                    Bloom = Core.Bloom.Empty,
+                    StateRoot = genesis.Header.Hash,
+                });
+
+                tree.SuggestBlock(genesis);
+                tree.Genesis.Should().NotBeNull();
+
+                tree.UpdateMainChain(ImmutableList.Create(genesis), true);
+
+                tree.SuggestBlock(second);
+                tree.SuggestBlock(third);
+            }
+
+            // Assume Nethermind got restarted
+            {
+                BlockTree tree = Build.A.BlockTree(HoleskySpecProvider.Instance)
+                    .WithBlockStore(new BlockStore(blocksDb))
+                    .WithBlocksNumberDb(blockNumberDb)
+                    .WithHeadersDb(headersDb)
+                    .WithChainLevelInfoRepository(chainLevelInfoRepository)
+                    .WithoutSettingHead
+                    .TestObject;
+
+                tree.Genesis.Should().NotBeNull();
+            }
+        }
+
         private class TestBlockTreeVisitor : IBlockTreeVisitor
         {
             private readonly ManualResetEvent _manualResetEvent;
```

### src/Nethermind/Nethermind.Core.Test/Builders/BlockTreeBuilder.cs
```diff
@@ -396,6 +396,12 @@ public BlockTreeBuilder WithHeadersDb(IDb headersDb)
             return this;
         }
 
+        public BlockTreeBuilder WithBlocksNumberDb(IDb blocksNumberDb)
+        {
+            BlockNumbersDb = blocksNumberDb;
+            return this;
+        }
+
         public BlockTreeBuilder WithBlockInfoDb(IDb blocksInfosDb)
         {
             BlockInfoDb = blocksInfosDb;
```

### src/Nethermind/Nethermind.Core/BlockInfo.cs
```diff
@@ -78,5 +78,11 @@ public bool IsBeaconInfo
         public long BlockNumber { get; set; }
 
         public override string ToString() => BlockHash.ToString();
+
+        public bool EqualsIgnoringWasProcessed(BlockInfo other) =>
+            TotalDifficulty.Equals(other.TotalDifficulty)
+            && BlockHash.Equals(other.BlockHash)
+            && Metadata == other.Metadata
+            && BlockNumber == other.BlockNumber;
     }
 }
```

### src/Nethermind/Nethermind.Core/ChainLevelInfo.cs
```diff
@@ -83,14 +83,17 @@ public void InsertBlockInfo(Keccak hash, BlockInfo blockInfo, bool setAsMain)
             BlockInfo[] blockInfos = BlockInfos;
 
             int? foundIndex = FindIndex(hash);
-            if (!foundIndex.HasValue)
+            if (foundIndex is null)
             {
                 Array.Resize(ref blockInfos, blockInfos.Length + 1);
             }
             else
             {
                 if (blockInfo.IsBeaconInfo && blockInfos[foundIndex.Value].IsBeaconMainChain)
                     blockInfo.Metadata |= BlockMetadata.BeaconMainChain;
+
+                if (blockInfo.EqualsIgnoringWasProcessed(blockInfos[foundIndex.Value]))
+                    blockInfo.WasProcessed |= blockInfos[foundIndex.Value].WasProcessed;
             }
 
             int index = foundIndex ?? blockInfos.Length - 1;
```

### src/Nethermind/Nethermind.Init/Steps/LoadGenesisBlock.cs
```diff
@@ -97,7 +97,7 @@ private void ValidateGenesisHash(Keccak? expectedGenesisHash)
             if (_api.WorldState is null) throw new StepDependencyException(nameof(_api.WorldState));
             if (_api.BlockTree is null) throw new StepDependencyException(nameof(_api.BlockTree));
 
-            BlockHeader genesis = _api.BlockTree.Genesis!;
+            BlockHeader genesis = _api.BlockTree.Genesis ?? throw new NullReferenceException("Genesis block is null");
             if (expectedGenesisHash is not null && genesis.Hash != expectedGenesisHash)
             {
                 if (_logger.IsWarn) _logger.Warn(_api.WorldState.DumpState());
```
