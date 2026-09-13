# [?] fix(txpool): fix data race that broadcasts a null transaction (#12162)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-06-29
Source: https://github.com/NethermindEth/nethermind/commit/618af12a9a1542f980c2c509d7700a589a95f1c9
Type: security-commit

## Details
fix(txpool): fix data race that broadcasts a null transaction (#12162)

* fix(txpool): fix data race that broadcasts a null transaction

TxBroadcaster.BroadcastOnce locked on the _accumulatedTemporaryTxs
instance while TimerOnElapsed swapped that field by reference via
Interlocked.Exchange without taking the same lock. A monitor only
serialises sections that lock the same stable object, so the swap let
two threads hold monitors on two different ResettableList instances
while both Add()-ing to the same underlying List<T>. A concurrent Add
during a resize leaves a null hole in the list, which is later read
lazily through txs.Where(_gossipFilter) and dereferenced by
SpecDrivenTxGossipPolicy, throwing NullReferenceException in
CompositeTxGossipPolicy.ShouldGossipTransaction while gossiping to peers.

Use a dedicated, never-reassigned lock for both the append and the swap.
After the swap, BroadcastOnce only touches the new (empty) accumulator
while the timer exclusively owns the buffer being sent, so the two lists
are never mutated concurrently. The ResettableList reuse/swap design is
kept to avoid per-broadcast allocations during sync.

The pre-existing race surfaces as a fatal crash now only because
SpecDrivenTxGossipPolicy is the first gossip policy to dereference the
transaction; it was observed on gnosis+Flat sync where finalization-driven
background work shifts scheduling enough to hit the window.

Adds a concurrency regression test that drives BroadcastOnce against
repeated timer swaps and asserts no null reaches the peer (and that every
transaction is sent exactly once). The test fails reliably on the old
code and passes on the fix.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* refactor(txpool): address review feedback

- Remove the two comments @asdacap flagged as unnecessary (the XML doc on
  _accumulatedTxsLock and the inline comment in NotifyPeers).
- Yield in the regression test's ticker loop so it no longer busy-spins a
  core; the swap window is still hit reliably (test still fails 5/5 on the
  pre-fix code, passes on the fix).

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

### src/Nethermind/Nethermind.TxPool.Test/TxBroadcasterTests.cs
```diff
@@ -2,6 +2,7 @@
 // SPDX-License-Identifier: LGPL-3.0-only
 
 using System;
+using System.Collections.Concurrent;
 using System.Collections.Generic;
 using System.Linq;
 using System.Runtime.CompilerServices;
@@ -723,6 +724,72 @@ public void can_correctly_broadcast_light_transactions_without_wrappers([Values]
         Assert.That(result, Is.EqualTo(versionMatches), "LightTransaction from blob transaction should be gossiped when proof version matches.");
     }
 
+    [Test]
+    public async Task Should_not_send_null_tx_when_adding_concurrently_with_timer_swap()
+    {
+        // Regression for the gossip NRE seen on gnosis+Flat: BroadcastOnce used to lock on the
+        // _accumulatedTemporaryTxs instance while the timer swapped that field by reference without taking the same
+        // lock. A concurrent Add could then mutate the swapped-out List<T> and leave a null hole, later dereferenced
+        // while gossiping (NullReferenceException in CompositeTxGossipPolicy.ShouldGossipTransaction).
+        ITimer timer = Substitute.For<ITimer>();
+        ITimerFactory timerFactory = Substitute.For<ITimerFactory>();
+        timerFactory.CreateTimer(Arg.Any<TimeSpan>()).Returns(timer);
+
+        _broadcaster = new TxBroadcaster(_comparer, timerFactory, _txPoolConfig, _headInfo, _logManager);
+
+        RecordingPeer peer = new(TestItem.PublicKeyA);
+        _broadcaster.AddPeer(peer);
+
+        const int txCount = 30_000;
+        Transaction[] transactions = new Transaction[txCount];
+        for (int i = 0; i < txCount; i++)
+        {
+            transactions[i] = Build.A.Transaction.WithNonce((ulong)i).TestObject;
+        }
+
+        using System.Threading.CancellationTokenSource cts = new();
+
+        // Keep firing the timer so NotifyPeers repeatedly swaps and flushes the accumulator while transactions are
+        // still being added from other threads - this is the window the old lock failed to guard.
+        Task ticker = Task.Run(() =>
+        {
+            while (!cts.IsCancellationRequested)
+            {
+                timer.Elapsed += Raise.Event<EventHandler>(timer, EventArgs.Empty);
+                System.Threading.Thread.Yield();
+            }
+        });
+
+        Parallel.For(0, txCount, i => _broadcaster.Broadcast(transactions[i], isPersistent: false));
+
+        cts.Cancel();
+        await ticker;
+        // Final flush of whatever was still accumulated after the adders finished.
+        timer.Elapsed += Raise.Event<EventHandler>(timer, EventArgs.Empty);
+
+        Assert.That(peer.SawNull, Is.False, "A null transaction reached the peer - the accumulated tx list was corrupted by a data race.");
+        Assert.That(peer.Sent.Count, Is.EqualTo(txCount), "Every broadcast transaction should be sent exactly once.");
+        Assert.That(peer.Sent.Distinct().Count(), Is.EqualTo(txCount), "No transaction should be sent more than once.");
+    }
+
+    private sealed class RecordingPeer(PublicKey id) : ITxPoolPeer
+    {
+        private readonly ConcurrentBag<Transaction> _sent = [];
+        public PublicKey Id => id;
+        public ulong HeadNumber { get; set; }
+        public bool SawNull { get; private set; }
+        public IReadOnlyCollection<Transaction> Sent => _sent;
+
+        public void SendNewTransactions(IEnumerable<Transaction> txs, bool sendFullTx)
+        {
+            foreach (Transaction tx in txs)
+            {
+                if (tx is null) SawNull = true;
+                else _sent.Add(tx);
+            }
+        }
+    }
+
     private (IList<Transaction> expectedTxs, IList<Hash256> expectedHashes) GetTxsAndHashesExpectedToBroadcast(Transaction[] transactions, int expectedCountTotal)
     {
         List<Transaction> expectedTxs = [];
```

### src/Nethermind/Nethermind.TxPool/TxBroadcaster.cs
```diff
@@ -53,6 +53,7 @@ internal class TxBroadcaster : IDisposable
         /// </summary>
         private ResettableList<Transaction> _txsToSend;
 
+        private readonly Lock _accumulatedTxsLock = new();
 
         /// <summary>
         /// Minimal value of MaxFeePerGas of local tx to be broadcasted immediately after receiving it
@@ -131,7 +132,7 @@ private bool StartBroadcast(Transaction tx)
 
         private void BroadcastOnce(Transaction tx)
         {
-            lock (_accumulatedTemporaryTxs)
+            lock (_accumulatedTxsLock)
             {
                 _accumulatedTemporaryTxs.Add(tx);
             }
@@ -296,7 +297,10 @@ private void TimerOnElapsed(object? sender, EventArgs args)
             [MethodImpl(MethodImplOptions.AggressiveInlining)]
             void NotifyPeers()
             {
-                _txsToSend = Interlocked.Exchange(ref _accumulatedTemporaryTxs, _txsToSend);
+                lock (_accumulatedTxsLock)
+                {
+                    (_accumulatedTemporaryTxs, _txsToSend) = (_txsToSend, _accumulatedTemporaryTxs);
+                }
 
                 if (_logger.IsTrace) _logger.Trace($"Broadcasting transactions to all peers");
 
```
