# [?] qml: fix crashes on tx finalizing

## Summary
Severity: Unknown
Chain: Bitcoin
Component: spesmilo/electrum
Published: 2022-10-04
Source: https://github.com/spesmilo/electrum/commit/090706bfd6861a8dd95e18f3ba48aa012adb9a19
Type: security-commit

## Details
qml: fix crashes on tx finalizing

## Patch
### electrum/gui/qml/qechannelopener.py
```diff
@@ -35,7 +35,7 @@ def __init__(self, parent=None):
     conflictingBackup = pyqtSignal([str], arguments=['message'])
     channelOpening = pyqtSignal([str], arguments=['peer'])
     channelOpenError = pyqtSignal([str], arguments=['message'])
-    channelOpenSuccess = pyqtSignal([str,bool,int], arguments=['cid','has_onchain_backup','min_depth','tx_complete'])
+    channelOpenSuccess = pyqtSignal([str,bool,int,bool], arguments=['cid','has_onchain_backup','min_depth','tx_complete'])
 
     dataChanged = pyqtSignal() # generic notify signal
 
@@ -163,7 +163,7 @@ def open_channel(self, confirm_backup_conflict=False):
             node_id=self._peer.pubkey,
             fee_est=None)
 
-        acpt = lambda tx: self.do_open_channel(tx, str(self._peer), None)
+        acpt = lambda tx: self.do_open_channel(tx, str(self._peer), self._wallet.password)
 
         self._finalizer = QETxFinalizer(self, make_tx=mktx, accept=acpt)
         self._finalizer.canRbf = False
```

### electrum/gui/qml/qetxfinalizer.py
```diff
@@ -280,7 +280,7 @@ def update(self):
         fee = tx.get_fee()
         feerate = Decimal(fee) / tx_size  # sat/byte
 
-        self.fee.satsInt = fee
+        self._fee.satsInt = int(fee)
         self.feeRate = f'{feerate:.1f}'
 
         #TODO
```

### electrum/gui/qml/qewallet.py
```diff
@@ -407,7 +407,7 @@ def send_onchain(self, address, amount, fee=None, rbf=False):
 
     @auth_protect
     def sign(self, tx, *, broadcast: bool = False):
-        tx = self.wallet.sign_transaction(tx, None)
+        tx = self.wallet.sign_transaction(tx, self.password)
 
         if tx is None:
             self._logger.info('did not sign')
```
