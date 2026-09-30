# [?] Fix #8648 - eth_getTransactionByBlockNumberAndIndex out of bounds (#8654)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2025-05-19
Source: https://github.com/NethermindEth/nethermind/commit/5522f4cbd4a5a5349258d8d2e1568c62ca5119e1
Type: security-commit

## Details
Fix #8648 - eth_getTransactionByBlockNumberAndIndex out of bounds (#8654)

* Fix #8648 - eth_getTransactionByBlockNumberAndIndex  out of bounds

* one more fix

## Patch
### src/Nethermind/Nethermind.JsonRpc.Test/Modules/Eth/EthRpcModuleTests.cs
```diff
@@ -178,6 +178,14 @@ public async Task Eth_get_transaction_by_block_number_and_index()
         JToken.Parse(serialized).Should().BeEquivalentTo("""{"jsonrpc":"2.0","result":{"hash":"0x7126cf20a0ad8bd51634837d9049615c34c1bff5e1a54e5663f7e23109bff48b","nonce":"0x2","blockHash":"0x29f141925d2d8e357ae5b6040c97aa12d7ac6dfcbe2b20e7b616d8907ac8e1f3","blockNumber":"0x3","transactionIndex":"0x1","from":"0xb7705ae4c6f81b66cdb323c65f4e8133690fc099","to":"0x942921b14f1b1c385cd7e0cc2ef7abe5598c8358","value":"0x1","gasPrice":"0x1","gas":"0x5208","input":"0x","type":"0x0","v":"0x25","s":"0x575361bb330bf38b9a89dd8279d42a20d34edeaeede9739a7c2bdcbe3242d7bb","r":"0xe7c5ff3cba254c4fe8f9f12c3f202150bb9a0aebeee349ff2f4acb23585f56bd"},"id":67}""");
     }
 
+    [Test]
+    public async Task Eth_get_transaction_by_block_number_and_index_out_of_bounds()
+    {
+        using Context ctx = await Context.Create();
+        string serialized = await ctx.Test.TestEthRpc("eth_getTransactionByBlockNumberAndIndex", ctx.Test.BlockTree.FindHeadBlock()!.Number.ToString(), "100");
+        Assert.That(serialized, Is.EqualTo("{\"jsonrpc\":\"2.0\",\"result\":null,\"id\":67}"));
+    }
+
     [TestCase(false, "{\"jsonrpc\":\"2.0\",\"result\":{\"difficulty\":\"0xf4240\",\"extraData\":\"0x010203\",\"gasLimit\":\"0x3d0900\",\"gasUsed\":\"0x0\",\"hash\":\"0xa2a9f03b9493046696099d27b2612b99497aa1f392ec966716ab393c715a5bb6\",\"logsBloom\":\"0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000\",\"miner\":\"0x0000000000000000000000000000000000000000\",\"mixHash\":\"0x2ba5557a4c62a513c7e56d1bf13373e0da6bec016755483e91589fe1c6d212e2\",\"nonce\":\"0x00000000000003e8\",\"number\":\"0x0\",\"parentHash\":\"0xff483e972a04a9a62bb4b7d04ae403c615604e4090521ecc5bb7af67f71be09c\",\"receiptsRoot\":\"0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421\",\"sha3Uncles\":\"0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347\",\"size\":\"0x201\",\"stateRoot\":\"0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421\",\"totalDifficulty\":\"0x0\",\"timestamp\":\"0xf4240\",\"transactions\":[],\"transactionsRoot\":\"0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421\",\"uncles\":[]},\"id\":67}")]
     [TestCase(true, "{\"jsonrpc\":\"2.0\",\"result\":{\"difficulty\":\"0xf4240\",\"extraData\":\"0x010203\",\"gasLimit\":\"0x3d0900\",\"gasUsed\":\"0x0\",\"hash\":\"0xa2a9f03b9493046696099d27b2612b99497aa1f392ec966716ab393c715a5bb6\",\"logsBloom\":\"0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000\",\"miner\":\"0x0000000000000000000000000000000000000000\",\"mixHash\":\"0x2ba5557a4c62a513c7e56d1bf13373e0da6bec016755483e91589fe1c6d212e2\",\"nonce\":\"0x00000000000003e8\",\"number\":\"0x0\",\"parentHash\":\"0xff483e972a04a9a62bb4b7d04ae403c615604e4090521ecc5bb7af67f71be09c\",\"receiptsRoot\":\"0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421\",\"sha3Uncles\":\"0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347\",\"size\":\"0x201\",\"stateRoot\":\"0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421\",\"totalDifficulty\":\"0x0\",\"timestamp\":\"0xf4240\",\"baseFeePerGas\":\"0x0\",\"transactions\":[],\"transactionsRoot\":\"0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421\",\"uncles\":[]},\"id\":67}")]
     public async Task Eth_get_uncle_by_block_number_and_index(bool eip1559, string expectedJson)
```

### src/Nethermind/Nethermind.JsonRpc/Modules/Eth/EthRpcModule.cs
```diff
@@ -433,46 +433,36 @@ public ResultWrapper<TransactionForRpc[]> eth_pendingTransactions()
     public ResultWrapper<TransactionForRpc> eth_getTransactionByBlockHashAndIndex(Hash256 blockHash, UInt256 positionIndex)
     {
         ResultWrapper<TransactionForRpc> result = GetTransactionByBlockAndIndex(new BlockParameter(blockHash), positionIndex);
-        if (result.Result.ResultType == ResultType.Success)
-        {
-            if (_logger.IsTrace)
-                _logger.Trace(
-                    $"eth_getTransactionByBlockHashAndIndex request {blockHash}, index: {positionIndex}, result: {result.Data.Hash}");
-        }
+        if (_logger.IsTrace && result.Result.ResultType == ResultType.Success) _logger.Trace($"eth_getTransactionByBlockHashAndIndex request {blockHash}, index: {positionIndex}, result: {result.Data?.Hash}");
         return result;
     }
 
     public ResultWrapper<TransactionForRpc> eth_getTransactionByBlockNumberAndIndex(BlockParameter blockParameter, UInt256 positionIndex)
     {
         ResultWrapper<TransactionForRpc> result = GetTransactionByBlockAndIndex(blockParameter, positionIndex);
-        if (result.Result.ResultType == ResultType.Success)
-        {
-            if (_logger.IsTrace)
-                _logger.Trace(
-                    $"eth_getTransactionByBlockNumberAndIndex request {blockParameter}, index: {positionIndex}, result: {result.Data.Hash}");
-        }
+        if (_logger.IsTrace && result.Result.ResultType == ResultType.Success) _logger.Trace($"eth_getTransactionByBlockNumberAndIndex request {blockParameter}, index: {positionIndex}, result: {result.Data?.Hash}");
         return result;
     }
 
-    protected virtual ResultWrapper<TransactionForRpc> GetTransactionByBlockAndIndex(BlockParameter blockParameter, UInt256 positionIndex)
+    protected virtual ResultWrapper<TransactionForRpc?> GetTransactionByBlockAndIndex(BlockParameter blockParameter, UInt256 positionIndex)
     {
         SearchResult<Block> searchResult = _blockFinder.SearchForBlock(blockParameter);
         if (searchResult.IsError)
         {
-            return GetFailureResult<TransactionForRpc, Block>(searchResult, _ethSyncingInfo.SyncMode.HaveNotSyncedBodiesYet());
+            return GetFailureResult<TransactionForRpc?, Block>(searchResult, _ethSyncingInfo.SyncMode.HaveNotSyncedBodiesYet());
         }
 
         Block? block = searchResult.Object;
         if (positionIndex < 0 || positionIndex > block!.Transactions.Length - 1)
         {
-            return ResultWrapper<TransactionForRpc>.Fail("Position Index is incorrect", ErrorCodes.InvalidParams);
+            return ResultWrapper<TransactionForRpc?>.Success(null);
         }
 
         Transaction transaction = block.Transactions[(int)positionIndex];
         RecoverTxSenderIfNeeded(transaction);
 
         TransactionForRpc transactionModel = TransactionForRpc.FromTransaction(transaction, block.Hash, block.Number, (int)positionIndex, block.BaseFeePerGas, _specProvider.ChainId);
-        return ResultWrapper<TransactionForRpc>.Success(transactionModel);
+        return ResultWrapper<TransactionForRpc?>.Success(transactionModel);
     }
 
     public ResultWrapper<BlockForRpc> eth_getUncleByBlockHashAndIndex(Hash256 blockHash, UInt256 positionIndex)
@@ -497,7 +487,7 @@ private ResultWrapper<BlockForRpc> GetUncle(BlockParameter blockParameter, UInt2
         Block block = searchResult.Object;
         if (positionIndex < 0 || positionIndex > block!.Uncles.Length - 1)
         {
-            return ResultWrapper<BlockForRpc>.Fail("Position Index is incorrect", ErrorCodes.InvalidParams);
+            return ResultWrapper<BlockForRpc>.Success(null);
         }
 
         BlockHeader uncleHeader = block.Uncles[(int)positionIndex];
```

### src/Nethermind/Nethermind.Optimism/Rpc/OptimismEthRpcModule.cs
```diff
@@ -191,18 +191,18 @@ receipt is OptimismTxReceipt optimismTxReceipt
         return ResultWrapper<TransactionForRpc?>.Success(transactionModel);
     }
 
-    protected override ResultWrapper<TransactionForRpc> GetTransactionByBlockAndIndex(BlockParameter blockParameter, UInt256 positionIndex)
+    protected override ResultWrapper<TransactionForRpc?> GetTransactionByBlockAndIndex(BlockParameter blockParameter, UInt256 positionIndex)
     {
         SearchResult<Block> searchResult = _blockFinder.SearchForBlock(blockParameter);
         if (searchResult.IsError || searchResult.Object is null)
         {
-            return GetFailureResult<TransactionForRpc, Block>(searchResult, _ethSyncingInfo.SyncMode.HaveNotSyncedBodiesYet());
+            return GetFailureResult<TransactionForRpc?, Block>(searchResult, _ethSyncingInfo.SyncMode.HaveNotSyncedBodiesYet());
         }
 
         Block block = searchResult.Object;
         if (positionIndex < 0 || positionIndex > block!.Transactions.Length - 1)
         {
-            return ResultWrapper<TransactionForRpc>.Fail("Position Index is incorrect", ErrorCodes.InvalidParams);
+            return ResultWrapper<TransactionForRpc?>.Success(null);
         }
 
         Transaction transaction = block.Transactions[(int)positionIndex];
@@ -218,7 +218,7 @@ protected override ResultWrapper<TransactionForRpc> GetTransactionByBlockAndInde
             depositTx.DepositReceiptVersion = (receipt as OptimismTxReceipt)?.DepositReceiptVersion;
         }
 
-        return ResultWrapper<TransactionForRpc>.Success(transactionModel);
+        return ResultWrapper<TransactionForRpc?>.Success(transactionModel);
     }
 
     protected override ResultWrapper<BlockForRpc?> GetBlock(BlockParameter blockParameter, bool returnFullTransactionObjects)
```
