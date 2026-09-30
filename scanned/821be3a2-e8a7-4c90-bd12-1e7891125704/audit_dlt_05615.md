# [?] fix: resolve flaky TxPool tests and SpecGasCosts DEBUG crash (#10713)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-03-04
Source: https://github.com/NethermindEth/nethermind/commit/5f349c98fd52d5a15866582af64f623f5653e555
Type: security-commit

## Details
fix: resolve flaky TxPool tests and SpecGasCosts DEBUG crash (#10713)

* fix and improve flaky tx pool tests

* Fix TxPool test hanging indefinitely on missing TxPoolHeadChanged event (#10715)

* Initial plan

* Use CancellationTokenSource with 5s timeout instead of CancellationToken.None in TxPool test

Co-authored-by: LukaszRozmej <12445221+LukaszRozmej@users.noreply.github.com>

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>
Co-authored-by: LukaszRozmej <12445221+LukaszRozmej@users.noreply.github.com>

---------

Co-authored-by: Copilot <198982749+Copilot@users.noreply.github.com>
Co-authored-by: LukaszRozmej <12445221+LukaszRozmej@users.noreply.github.com>

## Patch
### src/Nethermind/Nethermind.Core/Specs/SpecGasCosts.cs
```diff
@@ -67,7 +67,7 @@ public SpecGasCosts(IReleaseSpec spec)
         bool netIstanbul = spec.UseIstanbulNetGasMetering;  // EIP-2200
         bool netConstantinople = spec.UseConstantinopleNetGasMetering;  // EIP-1283
 
-        ClearReversalRefund =
+        long clearReversalRefund = ClearReversalRefund =
             hotCold ? RefundOf.SResetReversedHotCold
             : netIstanbul ? RefundOf.SResetReversedEip2200
             : netConstantinople ? RefundOf.SResetReversedEip1283
@@ -137,7 +137,7 @@ public SpecGasCosts(IReleaseSpec spec)
             : RefundOf.DestroyBeforeEip3529;
 
         int hashCode1 = HashCode.Combine(SLoadCost, BalanceCost, ExtCodeCost, ExtCodeHashCost, CallCost, ExpByteCost, sStoreResetCost, netMeteredSStoreCost);
-        int hashCode2 = HashCode.Combine(TxDataNonZeroMultiplier, ClearReversalRefund, setReversalRefund, SClearRefund, MaxBlobGasPerBlock, MaxBlobGasPerTx, TargetBlobGasPerBlock, DestroyRefund);
+        int hashCode2 = HashCode.Combine(TxDataNonZeroMultiplier, clearReversalRefund, setReversalRefund, SClearRefund, MaxBlobGasPerBlock, MaxBlobGasPerTx, TargetBlobGasPerBlock, DestroyRefund);
         _hashCode = HashCode.Combine(hashCode1, hashCode2);
     }
 
```

### src/Nethermind/Nethermind.TxPool.Test/TxPoolTests.cs
```diff
@@ -206,7 +206,7 @@ public void should_accept_1559_transactions_only_when_eip1559_enabled([Values(fa
         }
 
         [Test]
-        public void should_not_ignore_insufficient_funds_for_eip1559_transactions()
+        public async Task should_not_ignore_insufficient_funds_for_eip1559_transactions()
         {
             ISpecProvider specProvider = GetLondonSpecProvider();
             var txPool = CreatePool(null, specProvider);
@@ -220,11 +220,16 @@ public void should_not_ignore_insufficient_funds_for_eip1559_transactions()
             result.Should().Be(AcceptTxResult.InsufficientFunds);
             EnsureSenderBalance(tx.SenderAddress, tx.Value);
 
-            var headProcessed = new ManualResetEventSlim(false);
-            txPool.TxPoolHeadChanged += (s, a) => headProcessed.Set();
-            _blockTree.RaiseBlockAddedToMain(new BlockReplacementEventArgs(Build.A.Block.WithGasLimit(10000000).TestObject));
+            Block block = Build.A.Block.WithGasLimit(10000000).TestObject;
+            using CancellationTokenSource cts = new(TimeSpan.FromSeconds(5));
+            Task waitTask = Wait.ForEventCondition<Block>(
+                cts.Token,
+                e => txPool.TxPoolHeadChanged += e,
+                e => txPool.TxPoolHeadChanged -= e,
+                _ => true);
+            _blockTree.RaiseBlockAddedToMain(new BlockReplacementEventArgs(block));
+            await waitTask;
 
-            headProcessed.Wait();
             result = txPool.SubmitTx(tx, TxHandlingOptions.PersistentBroadcast);
             result.Should().Be(AcceptTxResult.InsufficientFunds);
             txPool.GetPendingTransactionsCount().Should().Be(0);
@@ -762,7 +767,7 @@ public async Task should_not_fail_if_there_is_no_current_nonce_in_bucket()
         }
 
         [Test]
-        public void should_remove_txHash_from_hashCache_when_tx_removed_because_of_txPool_size_exceeded()
+        public async Task should_remove_txHash_from_hashCache_when_tx_removed_because_of_txPool_size_exceeded()
         {
             _txPool = CreatePool(new TxPoolConfig() { Size = 1 });
             Transaction transaction = Build.A.Transaction
@@ -781,12 +786,8 @@ public void should_remove_txHash_from_hashCache_when_tx_removed_because_of_txPoo
             EnsureSenderBalance(higherPriorityTx);
             _txPool.SubmitTx(higherPriorityTx, TxHandlingOptions.PersistentBroadcast);
 
-            var headProcessed = new ManualResetEventSlim(false);
-            _txPool.TxPoolHeadChanged += (s, a) => headProcessed.Set();
+            await RaiseBlockAddedToMainAndWaitForNewHead(Build.A.Block.TestObject);
 
-            _blockTree.RaiseBlockAddedToMain(new BlockReplacementEventArgs(Build.A.Block.TestObject));
-
-            headProcessed.Wait();
             _txPool.IsKnown(higherPriorityTx.Hash).Should().BeTrue();
             _txPool.IsKnown(transaction.Hash).Should().BeFalse();
         }
@@ -872,7 +873,7 @@ public void should_not_broadcast_own_transactions_that_faded_out_and_came_back()
         [TestCase(10, 5)]
         [TestCase(10, 8)]
         [TestCase(10, 9)]
-        public void should_remove_stale_txs_from_persistent_transactions(int numberOfTxs, int nonceIncludedInBlock)
+        public async Task should_remove_stale_txs_from_persistent_transactions(int numberOfTxs, int nonceIncludedInBlock)
         {
             _txPool = CreatePool();
 
@@ -892,20 +893,14 @@ public void should_remove_stale_txs_from_persistent_transactions(int numberOfTxs
             _txPool.GetOwnPendingTransactions().Length.Should().Be(numberOfTxs);
 
             Block block = Build.A.Block.WithTransactions(transactions[nonceIncludedInBlock]).TestObject;
-            BlockReplacementEventArgs blockReplacementEventArgs = new(block, null);
-
-            ManualResetEvent manualResetEvent = new(false);
-            _txPool.TxPoolHeadChanged += (o, e) => manualResetEvent.Set();
-            _blockTree.RaiseBlockAddedToMain(blockReplacementEventArgs);
-            bool signaled = manualResetEvent.WaitOne(TimeSpan.FromMilliseconds(Timeout));
+            await RaiseBlockAddedToMainAndWaitForNewHead(block);
 
-            signaled.Should().BeTrue("TxPoolHeadChanged event should have been raised");
             // transactions[nonceIncludedInBlock] was included in the block and should be removed, as well as all lower nonces.
             _txPool.GetOwnPendingTransactions().Length.Should().Be(numberOfTxs - nonceIncludedInBlock - 1);
         }
 
         [Test]
-        public void broadcaster_should_work_well_when_there_are_no_txs_in_persistent_txs_from_sender_of_tx_included_in_block()
+        public async Task broadcaster_should_work_well_when_there_are_no_txs_in_persistent_txs_from_sender_of_tx_included_in_block()
         {
             _txPool = CreatePool();
 
@@ -931,14 +926,8 @@ public void broadcaster_should_work_well_when_there_are_no_txs_in_persistent_txs
             _txPool.GetOwnPendingTransactions().Length.Should().Be(1);
 
             Block block = Build.A.Block.WithTransactions(transactionA).TestObject;
-            BlockReplacementEventArgs blockReplacementEventArgs = new(block, null);
+            await RaiseBlockAddedToMainAndWaitForNewHead(block);
 
-            ManualResetEvent manualResetEvent = new(false);
-            _txPool.TxPoolHeadChanged += (o, e) => manualResetEvent.Set();
-            _blockTree.RaiseBlockAddedToMain(blockReplacementEventArgs);
-            bool signaled = manualResetEvent.WaitOne(TimeSpan.FromMilliseconds(Timeout));
-
-            signaled.Should().BeTrue("TxPoolHeadChanged event should have been raised");
             _txPool.GetPendingTransactionsCount().Should().Be(1);
             _txPool.GetOwnPendingTransactions().Length.Should().Be(1);
         }
@@ -1004,7 +993,7 @@ public void should_add_pending_transactions(bool sameTransactionSenderPerPeer, b
         [TestCase(false, true, 100)]
         [TestCase(true, false, 100)]
         [TestCase(false, false, 100)]
-        public void should_remove_tx_from_txPool_when_included_in_block(bool sameTransactionSenderPerPeer, bool sameNoncePerPeer, int expectedTransactions)
+        public async Task should_remove_tx_from_txPool_when_included_in_block(bool sameTransactionSenderPerPeer, bool sameNoncePerPeer, int expectedTransactions)
         {
             _txPool = CreatePool();
 
@@ -1013,22 +1002,16 @@ public void should_remove_tx_from_txPool_when_included_in_block(bool sameTransac
 
             Transaction[] transactions = _txPool.GetPendingTransactions();
             Block block = Build.A.Block.WithTransactions(transactions).TestObject;
-            BlockReplacementEventArgs blockReplacementEventArgs = new(block, null);
-
-            ManualResetEvent manualResetEvent = new(false);
-            _txPool.TxPoolHeadChanged += (o, e) => manualResetEvent.Set();
-            _blockTree.RaiseBlockAddedToMain(blockReplacementEventArgs);
-            bool signaled = manualResetEvent.WaitOne(TimeSpan.FromMilliseconds(Timeout));
+            await RaiseBlockAddedToMainAndWaitForNewHead(block);
 
-            signaled.Should().BeTrue("TxPoolHeadChanged event should have been raised");
             _txPool.GetPendingTransactionsCount().Should().Be(0);
         }
 
         [TestCase(true, true, 10)]
         [TestCase(false, true, 100)]
         [TestCase(true, false, 100)]
         [TestCase(false, false, 100)]
-        public void should_not_remove_txHash_from_hashCache_when_tx_removed_because_of_including_in_block(bool sameTransactionSenderPerPeer, bool sameNoncePerPeer, int expectedTransactions)
+        public async Task should_not_remove_txHash_from_hashCache_when_tx_removed_because_of_including_in_block(bool sameTransactionSenderPerPeer, bool sameNoncePerPeer, int expectedTransactions)
         {
             _txPool = CreatePool();
 
@@ -1037,14 +1020,8 @@ public void should_not_remove_txHash_from_hashCache_when_tx_removed_because_of_i
 
             Transaction[] transactions = _txPool.GetPendingTransactions();
             Block block = Build.A.Block.WithTransactions(transactions).TestObject;
-            BlockReplacementEventArgs blockReplacementEventArgs = new(block, null);
-
-            ManualResetEvent manualResetEvent = new(false);
-            _txPool.TxPoolHeadChanged += (o, e) => manualResetEvent.Set();
-            _blockTree.RaiseBlockAddedToMain(blockReplacementEventArgs);
-            bool signaled = manualResetEvent.WaitOne(TimeSpan.FromMilliseconds(Timeout));
+            await RaiseBlockAddedToMainAndWaitForNewHead(block);
 
-            signaled.Should().BeTrue("TxPoolHeadChanged event should have been raised");
             foreach (Transaction transaction in transactions)
             {
                 _txPool.IsKnown(transaction.Hash).Should().BeTrue();
@@ -2402,7 +2379,7 @@ private async Task RaiseBlockAddedToMainAndWaitForNewHead(Block block, Block pre
                 : new BlockReplacementEventArgs(block ?? Build.A.Block.TestObject, previousBlock);
 
             Task waitTask = Wait.ForEventCondition<Block>(
-                default,
+                CancellationToken.None,
                 e => _txPool.TxPoolHeadChanged += e,
                 e => _txPool.TxPoolHeadChanged -= e,
                 e => e.Number == block.Number
```
