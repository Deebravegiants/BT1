# [?] Guard EraE/eth_subscribe overflow, drop pre-ulong leftovers, cover gas-limit reject arm (#12178)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-07-03
Source: https://github.com/NethermindEth/nethermind/commit/58d7d9214acd1d4ad8888cabd2ad89983737e03b
Type: security-commit

## Details
Guard EraE/eth_subscribe overflow, drop pre-ulong leftovers, cover gas-limit reject arm (#12178)

* Align EraE resume buffer size underflow check with Era1

* Harden eth_subscribe to gracefully handle overlow

* Remove letfovers of pre ulong times

* Improve tests

## Patch
### src/Nethermind/Nethermind.Blockchain.Test/Validators/HeaderValidatorTests.cs
```diff
@@ -10,6 +10,7 @@
 using Nethermind.Core;
 using Nethermind.Core.BlockAccessLists;
 using Nethermind.Core.Crypto;
+using Nethermind.Core.Messages;
 using Nethermind.Core.Specs;
 using Nethermind.Core.Test;
 using Nethermind.Core.Test.Builders;
@@ -228,8 +229,11 @@ public void When_gaslimit_is_on_london_fork(ulong parentGasLimit, ulong blockNum
         Assert.That(result, Is.EqualTo(expectedResult));
     }
 
-    [Test, MaxTime(Timeout.MaxTestTime)]
-    public void When_gas_limit_is_long_max_value()
+    [MaxTime(Timeout.MaxTestTime)]
+    [TestCase(0x7FFFFFFFFFFFFFFFUL, true, TestName = "When_gas_limit_at_protocol_cap")]
+    [TestCase(0x8000000000000000UL, false, TestName = "When_gas_limit_just_above_protocol_cap")]
+    [TestCase(ulong.MaxValue, false, TestName = "When_gas_limit_is_ulong_max")]
+    public void When_gas_limit_around_protocol_cap(ulong gasLimit, bool expectedResult)
     {
         _validator = new HeaderValidator(_blockTree, _ethash, _specProvider, new OneLoggerLogManager(new(_testLogger)));
         _parentBlock = Build.A.Block.WithDifficulty(1)
@@ -239,14 +243,18 @@ public void When_gas_limit_is_long_max_value()
         _block = Build.A.Block.WithParent(_parentBlock)
             .WithDifficulty(131072)
             .WithMixHash(new Hash256("0xd7db5fdd332d3a65d6ac9c4c530929369905734d3ef7a91e373e81d0f010b8e8"))
-            .WithGasLimit(long.MaxValue)
+            .WithGasLimit(gasLimit)
             .WithNumber(_parentBlock.Number + 1)
             .WithNonce(0).TestObject;
         _block.Header.Hash = _block.CalculateHash();
 
-        bool result = _validator.Validate(_block.Header, _parentBlock.Header);
+        bool result = _validator.Validate(_block.Header, _parentBlock.Header, false, out string? error);
 
-        Assert.That(result, Is.True);
+        using (Assert.EnterMultipleScope())
+        {
+            Assert.That(result, Is.EqualTo(expectedResult));
+            Assert.That(error, expectedResult ? Is.Null : Is.EqualTo(BlockErrorMessages.InvalidGasLimit));
+        }
     }
 
 
```

### src/Nethermind/Nethermind.EraE/Import/EraImporter.cs
```diff
@@ -92,7 +92,10 @@ private async Task ImportInternal(ulong from, ulong to, IEraStore eraStore, Canc
         using ProgressReporter progress = new("EraE import", logManager, to - from + 1);
         ulong blocksProcessed = 0;
 
-        using BlockTreeSuggestPacer pacer = new(blockTree, eraConfig.ImportBlocksBufferSize, eraConfig.ImportBlocksBufferSize - 1024UL);
+        ulong resumeBatchSize = eraConfig.ImportBlocksBufferSize > 1024UL
+            ? eraConfig.ImportBlocksBufferSize - 1024UL
+            : eraConfig.ImportBlocksBufferSize / 2;
+        using BlockTreeSuggestPacer pacer = new(blockTree, eraConfig.ImportBlocksBufferSize, resumeBatchSize);
         ulong blockNumber = from;
 
         ulong suggestFromBlock = (blockTree.Head?.Number ?? 0UL) + 1;
```

### src/Nethermind/Nethermind.EthStats.Test/EthStatsIntegrationTests.cs
```diff
@@ -23,16 +23,16 @@ namespace Nethermind.EthStats.Test;
 
 public class EthStatsIntegrationTests
 {
-    [TestCase(3UL, 1UL, 1UL, 3UL, TestName = "TryNormalizeHistoryRange_swaps_min_and_max")]
-    [TestCase(0UL, 100UL, 37UL, 100UL, TestName = "TryNormalizeHistoryRange_limits_oversized_range")]
-    [TestCase(ulong.MaxValue - 63, ulong.MaxValue, ulong.MaxValue - 63, ulong.MaxValue, TestName = "TryNormalizeHistoryRange_handles_max_ulong_without_overflow")]
-    public void TryNormalizeHistoryRange_handles_edges(
+    [TestCase(3UL, 1UL, 1UL, 3UL, TestName = "NormalizeHistoryRange_swaps_min_and_max")]
+    [TestCase(0UL, 100UL, 37UL, 100UL, TestName = "NormalizeHistoryRange_limits_oversized_range")]
+    [TestCase(ulong.MaxValue - 63, ulong.MaxValue, ulong.MaxValue - 63, ulong.MaxValue, TestName = "NormalizeHistoryRange_handles_max_ulong_without_overflow")]
+    public void NormalizeHistoryRange_handles_edges(
         ulong requestMin,
         ulong requestMax,
         ulong expectedMin,
         ulong expectedMax)
     {
-        EthStatsIntegration.TryNormalizeHistoryRange(
+        EthStatsIntegration.NormalizeHistoryRange(
             new EthStatsHistoryRequest(requestMin, requestMax),
             out ulong min,
             out ulong max);
```

### src/Nethermind/Nethermind.EthStats/Integrations/EthStatsIntegration.cs
```diff
@@ -195,11 +195,7 @@ private async Task ReconnectHelloAsync()
 
         private Task SendHistoryAsync(EthStatsHistoryRequest request)
         {
-            if (!TryNormalizeHistoryRange(request, out ulong min, out ulong max))
-            {
-                if (_logger.IsDebug) _logger.Debug($"Ignoring invalid ETH Stats history range {request.Min}-{request.Max}.");
-                return Task.CompletedTask;
-            }
+            NormalizeHistoryRange(request, out ulong min, out ulong max);
 
             List<EthStatsBlock> history = new((int)(max - min + 1));
             for (ulong blockNumber = min; blockNumber <= max; blockNumber++)
@@ -300,26 +296,15 @@ private Task HandleUnknownMessageAsync(string eventType)
             return Task.CompletedTask;
         }
 
-        internal static bool TryNormalizeHistoryRange(EthStatsHistoryRequest request, out ulong min, out ulong max)
+        internal static void NormalizeHistoryRange(EthStatsHistoryRequest request, out ulong min, out ulong max)
         {
             min = Math.Min(request.Min, request.Max);
             max = Math.Max(request.Min, request.Max);
 
-            if (max < 0)
-            {
-                min = 0;
-                max = 0;
-                return false;
-            }
-
-            min = Math.Max(0, min);
-
             if (max - min >= MaxHistoryBlocks)
             {
                 min = max - MaxHistoryBlocks + 1;
             }
-
-            return true;
         }
 
         private static EthStatsBlock CreateBlockModel(CoreBlock block)
```

### src/Nethermind/Nethermind.JsonRpc.Test/Modules/SubscribeModuleTests.cs
```diff
@@ -467,12 +467,17 @@ public async Task LogsSubscription_dispose_regression()
             Assert.That(expectedResult, Is.EqualTo(serialized));
         }
 
-        [Test]
-        public async Task LogsSubscription_with_invalid_arguments_creating_result()
+        [TestCase("invalid_param")]
+        [TestCase("{\"fromBlock\":\"-1\"}")]
+        [TestCase("{\"fromBlock\":\"0x10000000000000000\"}")]
+        [TestCase("{\"toBlock\":\"notanumber\"}")]
+        [TestCase("{\"address\":\"0xzz705ae4c6f81b66cdb323c65f4e8133690fc099\"}")]
+        [TestCase("{\"blockHash\":\"0xzz783fac2efed8fbc9ad443e592ee30e61d65f471140c10ca155e937b435b760\"}")]
+        public async Task LogsSubscription_with_malformed_args_returns_invalid_params(string args)
         {
-            string serialized = await RpcTest.TestSerializedRequest(_subscribeRpcModule, "eth_subscribe", "logs", "invalid_param");
+            string serialized = await RpcTest.TestSerializedRequest(_subscribeRpcModule, "eth_subscribe", "logs", args);
             string expectedResult = "{\"jsonrpc\":\"2.0\",\"error\":{\"code\":-32602,\"message\":\"Invalid params\"},\"id\":67}";
-            Assert.That(expectedResult, Is.EqualTo(serialized));
+            Assert.That(expectedResult, Is.EqualTo(serialized), "malformed eth_subscribe/logs args should map to InvalidParams, not InternalError");
         }
 
         [Test]
```

### src/Nethermind/Nethermind.JsonRpc/Modules/Subscribe/SubscribeRpcModule.cs
```diff
@@ -26,7 +26,7 @@ public ResultWrapper<string> eth_subscribe(string subscriptionName, string? args
             {
                 return ResultWrapper<string>.Fail($"Invalid params", ErrorCodes.InvalidParams, e.Message);
             }
-            catch (JsonException)
+            catch (Exception e) when (e is JsonException or FormatException or OverflowException)
             {
                 return ResultWrapper<string>.Fail($"Invalid params", ErrorCodes.InvalidParams);
             }
```

### src/Nethermind/Nethermind.Optimism/Rpc/OptimismPayloadAttributes.cs
```diff
@@ -74,7 +74,7 @@ protected override int ComputePayloadIdMembersSize() =>
         base.ComputePayloadIdMembersSize()
         + sizeof(bool) // noTxPool
         + (Keccak.Size * TransactionsLength) // Txs
-        + sizeof(long) // gasLimit
+        + sizeof(ulong) // gasLimit
         + ((EIP1559Params?.Length * sizeof(byte)) ?? 0); // eip1559Params
 
     protected override int WritePayloadIdMembers(BlockHeader parentHeader, Span<byte> inputSpan)
```
