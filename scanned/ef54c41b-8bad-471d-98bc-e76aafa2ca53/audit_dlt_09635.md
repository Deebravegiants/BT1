# [?] merge bitcoin#26747: fix confusing error / GUI crash on cross-chain legacy wallet restore

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2022-12-23
Source: https://github.com/dashpay/dash/commit/c0f9225dad2ea75edb2ac61fa4cca8f6ee2b184e
Type: security-commit

## Details
merge bitcoin#26747: fix confusing error / GUI crash on cross-chain legacy wallet restore

## Patch
### src/wallet/wallet.cpp
```diff
@@ -428,8 +428,7 @@ std::shared_ptr<CWallet> RestoreWallet(WalletContext& context, const fs::path& b
         error += strprintf(Untranslated("Unexpected exception: %s"), e.what());
     }
     if (!wallet) {
-        fs::remove(wallet_file);
-        fs::remove(wallet_path);
+        fs::remove_all(wallet_path);
     }
 
     return wallet;
```

### test/functional/wallet_crosschain.py
```diff
@@ -33,20 +33,28 @@ def run_test(self):
         self.log.info("Creating wallets")
 
         node0_wallet = os.path.join(self.nodes[0].datadir, 'node0_wallet')
+        node0_wallet_backup = os.path.join(self.nodes[0].datadir, 'node0_wallet.bak')
         self.nodes[0].createwallet(node0_wallet)
+        self.nodes[0].backupwallet(node0_wallet_backup)
         self.nodes[0].unloadwallet(node0_wallet)
         node1_wallet = os.path.join(self.nodes[1].datadir, 'node1_wallet')
+        node1_wallet_backup = os.path.join(self.nodes[0].datadir, 'node1_wallet.bak')
         self.nodes[1].createwallet(node1_wallet)
+        self.nodes[1].backupwallet(node1_wallet_backup)
         self.nodes[1].unloadwallet(node1_wallet)
 
-        self.log.info("Loading wallets into nodes with a different genesis blocks")
+        self.log.info("Loading/restoring wallets into nodes with a different genesis block")
 
         if self.options.descriptors:
             assert_raises_rpc_error(-18, 'Wallet file verification failed.', self.nodes[0].loadwallet, node1_wallet)
             assert_raises_rpc_error(-18, 'Wallet file verification failed.', self.nodes[1].loadwallet, node0_wallet)
+            assert_raises_rpc_error(-18, 'Wallet file verification failed.', self.nodes[0].restorewallet, 'w', node1_wallet_backup)
+            assert_raises_rpc_error(-18, 'Wallet file verification failed.', self.nodes[1].restorewallet, 'w', node0_wallet_backup)
         else:
             assert_raises_rpc_error(-4, 'Wallet files should not be reused across chains.', self.nodes[0].loadwallet, node1_wallet)
             assert_raises_rpc_error(-4, 'Wallet files should not be reused across chains.', self.nodes[1].loadwallet, node0_wallet)
+            assert_raises_rpc_error(-4, 'Wallet files should not be reused across chains.', self.nodes[0].restorewallet, 'w', node1_wallet_backup)
+            assert_raises_rpc_error(-4, 'Wallet files should not be reused across chains.', self.nodes[1].restorewallet, 'w', node0_wallet_backup)
 
         if not self.options.descriptors:
             self.log.info("Override cross-chain wallet load protection")
```
