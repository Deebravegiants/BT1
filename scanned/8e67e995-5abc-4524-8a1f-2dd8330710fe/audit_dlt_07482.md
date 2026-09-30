# [?] Merge #8312: Fix mempool DoS vulnerability from malleated transactions

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2016-07-14
Source: https://github.com/dogecoin/dogecoin/commit/ca40ef6029c1b4f2984e767b6c335dca6d637388
Type: security-commit

## Details
Merge #8312: Fix mempool DoS vulnerability from malleated transactions

46c9620 Test that unnecessary witnesses can't be used for mempool DoS (Suhas Daftuar)
bb66a11 Fix DoS vulnerability in mempool acceptance (Suhas Daftuar)

## Patch
### qa/rpc-tests/p2p-segwit.py
```diff
@@ -43,6 +43,7 @@ def __init__(self):
         self.last_pong = msg_pong(0)
         self.sleep_time = 0.05
         self.getdataset = set()
+        self.last_reject = None
 
     def add_connection(self, conn):
         self.connection = conn
@@ -68,7 +69,7 @@ def on_pong(self, conn, message):
 
     def on_reject(self, conn, message):
         self.last_reject = message
-        #print message
+        #print (message)
 
     # Syncing helpers
     def sync(self, test_function, timeout=60):
@@ -136,13 +137,17 @@ def request_block(self, blockhash, inv_type, timeout=60):
         self.wait_for_block(blockhash, timeout)
         return self.last_block
 
-    def test_transaction_acceptance(self, tx, with_witness, accepted):
+    def test_transaction_acceptance(self, tx, with_witness, accepted, reason=None):
         tx_message = msg_tx(tx)
         if with_witness:
             tx_message = msg_witness_tx(tx)
         self.send_message(tx_message)
         self.sync_with_ping()
         assert_equal(tx.hash in self.connection.rpc.getrawmempool(), accepted)
+        if (reason != None and not accepted):
+            # Check the rejection reason as well.
+            with mininode_lock:
+                assert_equal(self.last_reject.reason, reason)
 
     # Test whether a witness block had the correct effect on the tip
     def test_witness_block(self, block, accepted, with_witness=True):
@@ -277,9 +282,52 @@ def test_unnecessary_witness_before_segwit_activation(self):
         self.test_node.sync_with_ping()
         assert_equal(self.nodes[0].getbestblockhash(), block.hash)
 
+        sync_blocks(self.nodes)
+
+        # Create a p2sh output -- this is so we can pass the standardness
+        # rules (an anyone-can-spend OP_TRUE would be rejected, if not wrapped
+        # in P2SH).
+        p2sh_program = CScript([OP_TRUE])
+        p2sh_pubkey = hash160(p2sh_program)
+        scriptPubKey = CScript([OP_HASH160, p2sh_pubkey, OP_EQUAL])
+
+        # Now check that unnecessary witnesses can't be used to blind a node
+        # to a transaction, eg by violating standardness checks.
+        tx2 = CTransaction()
+        tx2.vin.append(CTxIn(COutPoint(tx.sha256, 0), b""))
+        tx2.vout.append(CTxOut(tx.vout[0].nValue-1000, scriptPubKey))
+        tx2.rehash()
+        self.test_node.test_transaction_acceptance(tx2, False, True)
+        self.nodes[0].generate(1)
+        sync_blocks(self.nodes)
+
+        # We'll add an unnecessary witness to this transaction that would cause
+        # it to be too large according to IsStandard.
+        tx3 = CTransaction()
+        tx3.vin.append(CTxIn(COutPoint(tx2.sha256, 0), CScript([p2sh_program])))
+        tx3.vout.append(CTxOut(tx2.vout[0].nValue-1000, scriptPubKey))
+        tx3.wit.vtxinwit.append(CTxinWitness())
+        tx3.wit.vtxinwit[0].scriptWitness.stack = [b'a'*400000]
+        tx3.rehash()
+        self.std_node.test_transaction_acceptance(tx3, True, False, b'no-witness-yet')
+
+        # If we send without witness, it should be accepted.
+        self.std_node.test_transaction_acceptance(tx3, False, True)
+
+        # Now create a new anyone-can-spend utxo for the next test.
+        tx4 = CTransaction()
+        tx4.vin.append(CTxIn(COutPoint(tx3.sha256, 0), CScript([p2sh_program])))
+        tx4.vout.append(CTxOut(tx3.vout[0].nValue-1000, CScript([OP_TRUE])))
+        tx4.rehash()
+        self.test_node.test_transaction_acceptance(tx3, False, True)
+        self.test_node.test_transaction_acceptance(tx4, False, True)
+
+        self.nodes[0].generate(1)
+        sync_blocks(self.nodes)
+
         # Update our utxo list; we spent the first entry.
         self.utxo.pop(0)
-        self.utxo.append(UTXO(tx.sha256, 0, tx.vout[0].nValue))
+        self.utxo.append(UTXO(tx4.sha256, 0, tx4.vout[0].nValue))
 
 
     # Mine enough blocks for segwit's vb state to be 'started'.
```

### src/main.cpp
```diff
@@ -1132,11 +1132,6 @@ bool AcceptToMemoryPoolWorker(CTxMemPool& pool, CValidationState& state, const C
     if (tx.IsCoinBase())
         return state.DoS(100, false, REJECT_INVALID, "coinbase");
 
-    // Rather not work on nonstandard transactions (unless -testnet/-regtest)
-    string reason;
-    if (fRequireStandard && !IsStandardTx(tx, reason))
-        return state.DoS(0, false, REJECT_NONSTANDARD, reason);
-
     // Don't relay version 2 transactions until CSV is active, and we can be
     // sure that such transactions will be mined (unless we're on
     // -testnet/-regtest).
@@ -1150,6 +1145,11 @@ bool AcceptToMemoryPoolWorker(CTxMemPool& pool, CValidationState& state, const C
         return state.DoS(0, false, REJECT_NONSTANDARD, "no-witness-yet", true);
     }
 
+    // Rather not work on nonstandard transactions (unless -testnet/-regtest)
+    string reason;
+    if (fRequireStandard && !IsStandardTx(tx, reason))
+        return state.DoS(0, false, REJECT_NONSTANDARD, reason);
+
     // Only accept nLockTime-using transactions that can be mined in the next
     // block; we don't want our mempool filled up with transactions that can't
     // be mined yet.
```
