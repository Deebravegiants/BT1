# [?] Fix IndexOutOfBoundsException race condition in TransactionBroadcaster (#10482)

## Summary
Severity: Unknown
Chain: Ethereum
Component: hyperledger/besu
Published: 2026-05-26
Source: https://github.com/besu-eth/besu/commit/77b4a04b3ea521b754588a9ca9feb8bc20ddbf4c
Type: security-commit

## Details
Fix IndexOutOfBoundsException race condition in TransactionBroadcaster (#10482)

* Fix IndexOutOfBoundsException race condition in TransactionBroadcaster

Signed-off-by: rakshaak29 <rakshaak29@gmail.com>

* test: add regression test for IndexOutOfBoundsException race condition in TransactionBroadcaster

When peerCount() and streamAvailablePeers() are called sequentially, peers can
disconnect between the two calls. This causes numPeersToSendFullTransactions
(calculated from peerCount) to exceed the actual number of peers returned by
streamAvailablePeers(), causing subList() to throw IndexOutOfBoundsException.

The new test reproduces this scenario: peerCount() returns 9 (sqrt = 3 full-tx
peers) but only 2 peers are available when streamAvailablePeers() is called.

Signed-off-by: rakshaak29 <rakshaak29@gmail.com>

* Fix spotless formatting

Signed-off-by: rakshaak29 <rakshaak29@gmail.com>

---------

Signed-off-by: rakshaak29 <rakshaak29@gmail.com>
Co-authored-by: Fabio Di Fabio <fabio.difabio@consensys.net>

## Patch
### ethereum/eth/src/main/java/org/hyperledger/besu/ethereum/eth/transactions/TransactionBroadcaster.java
```diff
@@ -114,10 +114,13 @@ public void onTransactionsAdded(final Collection<Transaction> transactions) {
 
     Collections.shuffle(peers, random);
 
+    final int actualNumPeersToSendFullTransactions =
+        Math.min(numPeersToSendFullTransactions, peers.size());
+
     final List<EthPeer> sendFullTransactionsPeers =
-        peers.subList(0, numPeersToSendFullTransactions);
+        peers.subList(0, actualNumPeersToSendFullTransactions);
     final List<EthPeer> sendOnlyHashesPeers =
-        peers.subList(numPeersToSendFullTransactions, peers.size());
+        peers.subList(actualNumPeersToSendFullTransactions, peers.size());
 
     LOG.atTrace()
         .setMessage("Sending full transactions to {} peers, transaction hashes only to {} peers")
```

### ethereum/eth/src/test/java/org/hyperledger/besu/ethereum/eth/transactions/TransactionBroadcasterTest.java
```diff
@@ -126,6 +126,37 @@ public void onTransactionsAddedWithNoPeersDoesNothing() {
     verifyNothingSent();
   }
 
+  /**
+   * Regression test for the race condition that caused an IndexOutOfBoundsException in
+   * TransactionBroadcaster.onTransactionsAdded.
+   *
+   * <p>The race: {@code peerCount()} is called first to calculate {@code
+   * numPeersToSendFullTransactions = sqrt(peerCount)}. Then {@code streamAvailablePeers()} is
+   * called to get the actual peer list. Between these two calls, peers can disconnect, so {@code
+   * streamAvailablePeers()} may return fewer peers than {@code peerCount()} indicated.
+   *
+   * <p>Before the fix, {@code peers.subList(0, numPeersToSendFullTransactions)} would throw {@link
+   * IndexOutOfBoundsException} when {@code numPeersToSendFullTransactions > peers.size()}. The fix
+   * clamps the index with {@code Math.min(numPeersToSendFullTransactions, peers.size())}.
+   */
+  @Test
+  public void onTransactionsAddedDoesNotThrowWhenPeersDisconnectBetweenCountAndStream() {
+    // Simulate: peerCount() returns 9 (so numPeersToSendFullTransactions = sqrt(9) = 3),
+    // but by the time streamAvailablePeers() is called, only 2 peers remain.
+    // Before the fix this triggered: IndexOutOfBoundsException from subList(0, 3) on a list of 2.
+    when(ethPeers.peerCount()).thenReturn(9);
+    when(ethPeers.streamAvailablePeers())
+        .thenReturn(Stream.of(ethPeer, ethPeer2).map(EthPeerImmutableAttributes::from));
+
+    List<Transaction> txs = toTransactionList(setupTransactionPool(1, 1));
+
+    // Must not throw IndexOutOfBoundsException
+    txBroadcaster.onTransactionsAdded(txs);
+
+    // All available peers should receive the transactions (as full or hash-only)
+    sendTaskCapture.getAllValues().forEach(Runnable::run);
+  }
+
   @Test
   public void onTransactionsAddedWithOnly2PeersSendFullTransactions() {
     when(ethPeers.peerCount()).thenReturn(2);
```
