# [?] functional_tests: add double spend detection tests

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2019-03-25
Source: https://github.com/monero-project/monero/commit/798e3cad2ba923d61cbce95784ee7990bf20b3a0
Type: security-commit

## Details
functional_tests: add double spend detection tests

## Patch
### tests/functional_tests/transfer.py
```diff
@@ -42,6 +42,7 @@ def run_test(self):
         self.mine()
         self.transfer()
         self.check_get_bulk_payments()
+        self.check_double_spend_detection()
 
     def create(self):
         print 'Creating wallets'
@@ -509,5 +510,65 @@ def check_get_bulk_payments(self):
         res = self.wallet[2].get_bulk_payments(payment_ids = ['1'*64, '1234500000012345abcde00000abcdeff1234500000012345abcde00000abcde', '2'*64])
         assert len(res.payments) >= 1 # one tx was sent
 
+    def check_double_spend_detection(self):
+        print('Checking double spend detection')
+        txes = [[None, None], [None, None]]
+        for i in range(2):
+            self.wallet[0].restore_deterministic_wallet(seed = 'velvet lymph giddy number token physics poetry unquoted nibs useful sabotage limits benches lifestyle eden nitrogen anvil fewest avoid batch vials washing fences goat unquoted')
+            self.wallet[0].refresh()
+            res = self.wallet[0].get_balance()
+            unlocked_balance = res.unlocked_balance
+            res = self.wallet[0].sweep_all(address = '44Kbx4sJ7JDRDV5aAhLJzQCjDz2ViLRduE3ijDZu3osWKBjMGkV1XPk4pfDUMqt1Aiezvephdqm6YD19GKFD9ZcXVUTp6BW', do_not_relay = True, get_tx_hex = True)
+            assert len(res.tx_hash_list) == 1
+            assert len(res.tx_hash_list[0]) == 32*2
+            txes[i][0] = res.tx_hash_list[0]
+            assert len(res.fee_list) == 1
+            assert res.fee_list[0] > 0
+            assert len(res.amount_list) == 1
+            assert res.amount_list[0] == unlocked_balance - res.fee_list[0]
+            assert len(res.tx_blob_list) > 0
+            assert len(res.tx_blob_list[0]) > 0
+            assert not 'tx_metadata_list' in res or len(res.tx_metadata_list) == 0
+            assert not 'multisig_txset' in res or len(res.multisig_txset) == 0
+            assert not 'unsigned_txset' in res or len(res.unsigned_txset) == 0
+            assert len(res.tx_blob_list) == 1
+            txes[i][1] = res.tx_blob_list[0]
+
+        daemon = Daemon()
+        res = daemon.send_raw_transaction(txes[0][1])
+        assert res.not_relayed == False
+        assert res.low_mixin == False
+        assert res.double_spend == False
+        assert res.invalid_input == False
+        assert res.invalid_output == False
+        assert res.too_big == False
+        assert res.overspend == False
+        assert res.fee_too_low == False
+        assert res.not_rct == False
+
+        res = daemon.get_transactions([txes[0][0]])
+        assert len(res.txs) >= 1
+        tx = [tx for tx in res.txs if tx.tx_hash == txes[0][0]][0]
+        assert tx.in_pool
+        assert not tx.double_spend_seen
+
+        res = daemon.send_raw_transaction(txes[1][1])
+        assert res.not_relayed == False
+        assert res.low_mixin == False
+        assert res.double_spend == True
+        assert res.invalid_input == False
+        assert res.invalid_output == False
+        assert res.too_big == False
+        assert res.overspend == False
+        assert res.fee_too_low == False
+        assert res.not_rct == False
+
+        res = daemon.get_transactions([txes[0][0]])
+        assert len(res.txs) >= 1
+        tx = [tx for tx in res.txs if tx.tx_hash == txes[0][0]][0]
+        assert tx.in_pool
+        assert tx.double_spend_seen
+
+
 if __name__ == '__main__':
     TransferTest().run_test()
```

### utils/python-rpc/framework/wallet.py
```diff
@@ -159,11 +159,23 @@ def sweep_dust(self):
         }
         return self.rpc.send_json_rpc_request(sweep_dust)
 
-    def sweep_all(self, address):
+    def sweep_all(self, address = '', account_index = 0, subaddr_indices = [], priority = 0, ring_size = 0, outputs = 1, unlock_time = 0, payment_id = '', get_tx_keys = False, below_amount = 0, do_not_relay = False, get_tx_hex = False, get_tx_metadata = False):
         sweep_all = {
             'method': 'sweep_all',
             'params' : {
-                'address' : ''
+                'address' : address,
+                'account_index' : account_index,
+                'subaddr_indices' : subaddr_indices,
+                'priority' : priority,
+                'ring_size' : ring_size,
+                'outputs' : outputs,
+                'unlock_time' : unlock_time,
+                'payment_id' : payment_id,
+                'get_tx_keys' : get_tx_keys,
+                'below_amount' : below_amount,
+                'do_not_relay' : do_not_relay,
+                'get_tx_hex' : get_tx_hex,
+                'get_tx_metadata' : get_tx_metadata,
             },
             'jsonrpc': '2.0', 
             'id': '0'
```
