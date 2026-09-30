# [?] Merge bitcoin/bitcoin#26462: wallet: fix crash on loading descriptor wallet containing legacy key type entries

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2022-12-05
Source: https://github.com/dashpay/dash/commit/0dcda483299b5686db92b71a19e2a9493f7777dc
Type: security-commit

## Details
Merge bitcoin/bitcoin#26462: wallet: fix crash on loading descriptor wallet containing legacy key type entries

3198e4239e848bbb119e3638677aa9bcf8353ca6 test: check that loading descriptor wallet with legacy entries throws error (Sebastian Falbesoner)
349ed2a0eed3aaaf199ead93057c97730869c3a3 wallet: throw error if legacy entries are present on loading descriptor wallets (Sebastian Falbesoner)

Pull request description:

  Loading a descriptor wallet currently leads to a segfault if a legacy key type entry is present that can be deserialized successfully and needs SPKman-interaction. To reproduce with a "cscript" entry (see second commit for details):

  ```
  $ ./src/bitcoin-cli createwallet crashme
  $ ./src/bitcoin-cli unloadwallet crashme
  $ sqlite3 ~/.bitcoin/wallets/crashme/wallet.dat
  SQLite version 3.38.2 2022-03-26 13:51:10
  Enter ".help" for usage hints.
  sqlite> INSERT INTO main VALUES(x'07637363726970740000000000000000000000000000000000000000', x'00');
  $ ./src/bitcoin-cli loadwallet crashme

  --- bitcoind output: ---
  2022-11-06T13:51:01Z Using SQLite Version 3.38.2
  2022-11-06T13:51:01Z Using wallet /home/honey/.bitcoin/wallets/crashme
  2022-11-06T13:51:01Z init message: Loading wallet…
  2022-11-06T13:51:01Z [crashme] Wallet file version = 10500, last client version = 249900

  Segmentation fault (core dumped)
  ```

  Background: In the wallet key-value-loading routine, most legacy type entries require a `LegacyScriptPubKeyMan` instance after successful deserialization. On a descriptor wallet, creating that (via method `GetOrCreateLegacyScriptPubKeyMan`) fails and then leads to a null-pointer dereference crash. E.g. for CSCRIPT: https://github.com/bitcoin/bitcoin/blob/50422b770a40f5fa964201d1e99fd6b5dc1653ca/src/wallet/walletdb.cpp#L589-L594

  ~~This PR fixes this by simply ignoring legacy entries if the wallet flags indicate that we have a descriptor wallet. The second commits adds a regression test to the descriptor wallet's functional test (fortunately Python includes sqlite3 support in the standard library).~~

  ~~Probably it would be even better to throw a warning to the user if unexpected legacy entries are found in descriptor wallets, but I think as a first mitigation everything is obvisouly better than crashing. As far as I'm aware, descriptor wallets created/migrated by Bitcoin Core should never end up in a state containing legacy type entries though.~~

  This PR fixes this by throwing an error if legacy entries are found in descriptor wallets on loading.

ACKs for top commit:
  achow101:
    ACK 3198e4239e848bbb119e3638677aa9bcf8353ca6
  aureleoules:
    ACK 3198e4239e848bbb119e3638677aa9bcf8353ca6

Tree-SHA512: ee43da3f61248e0fde55d9a705869202cb83df678ebf4816f0e77263f0beac0d7bae9490465d1753159efb093ee37182931d76b2e2b6e8c6f8761285700ace1c

Co-authored-by: Andrew Chow <github@achow101.com>

## Patch
### src/wallet/wallet.cpp
```diff
@@ -3213,6 +3213,10 @@ std::shared_ptr<CWallet> CWallet::Create(WalletContext& context, const std::stri
                                 "The wallet might had been created on a newer version.\n"
                                 "Please try running the latest software version.\n"), walletFile);
             return nullptr;
+        } else if (nLoadWalletRet == DBErrors::UNEXPECTED_LEGACY_ENTRY) {
+            error = strprintf(_("Unexpected legacy entry in descriptor wallet found. Loading wallet %s\n\n"
+                                "The wallet might have been tampered with or created with malicious intent.\n"), walletFile);
+            return nullptr;
         } else {
             error = strprintf(_("Error loading %s"), walletFile);
             return nullptr;
```

### src/wallet/walletdb.cpp
```diff
@@ -368,6 +368,8 @@ class CWalletScanState {
     std::map<std::pair<uint256, CKeyID>, std::pair<std::vector<unsigned char>, std::vector<unsigned char>>> crypted_mnemonics;
     bool tx_corrupt{false};
     bool descriptor_unknown{false};
+    bool unexpected_legacy_entry{false};
+
     CWalletScanState() = default;
 };
 
@@ -384,6 +386,11 @@ ReadKeyValue(CWallet* pwallet, CDataStream& ssKey, CDataStream& ssValue,
         if (filter_fn && !filter_fn(strType)) {
             return true;
         }
+        // Legacy entries in descriptor wallets are not allowed, abort immediately
+        if (pwallet->IsWalletFlagSet(WALLET_FLAG_DESCRIPTORS) && DBKeys::LEGACY_TYPES.count(strType) > 0) {
+            wss.unexpected_legacy_entry = true;
+            return false;
+        }
         if (strType == DBKeys::NAME) {
             std::string strAddress;
             ssKey >> strAddress;
@@ -918,6 +925,12 @@ DBErrors WalletBatch::LoadWallet(CWallet* pwallet)
             std::string strType, strErr;
             if (!ReadKeyValue(pwallet, ssKey, ssValue, wss, strType, strErr))
             {
+                if (wss.unexpected_legacy_entry) {
+                    strErr = strprintf("Error: Unexpected legacy entry found in descriptor wallet %s. ", pwallet->GetName());
+                    strErr += "The wallet might have been tampered with or created with malicious intent.";
+                    pwallet->WalletLogPrintf("%s\n", strErr);
+                    return DBErrors::UNEXPECTED_LEGACY_ENTRY;
+                }
                 // losing keys is considered a catastrophic error, anything else
                 // we assume the user can live with:
                 if (IsKeyType(strType) || strType == DBKeys::DEFAULTKEY) {
```

### src/wallet/walletdb.h
```diff
@@ -59,7 +59,8 @@ enum class DBErrors
     LOAD_FAIL,
     NEED_REWRITE,
     NEED_RESCAN,
-    UNKNOWN_DESCRIPTOR
+    UNKNOWN_DESCRIPTOR,
+    UNEXPECTED_LEGACY_ENTRY
 };
 
 namespace DBKeys {
```

### test/functional/wallet_descriptor.py
```diff
@@ -3,6 +3,8 @@
 # Distributed under the MIT software license, see the accompanying
 # file COPYING or http://www.opensource.org/licenses/mit-license.php.
 """Test descriptor wallet function."""
+import os
+import sqlite3
 
 from test_framework.test_framework import BitcoinTestFramework
 from test_framework.util import (
@@ -188,5 +190,15 @@ def run_test(self):
                     imp_addr = imp_rpc.getnewaddress()
                 assert_equal(exp_addr, imp_addr)
 
+        self.log.info("Test that loading descriptor wallet containing legacy key types throws error")
+        self.nodes[0].createwallet(wallet_name="crashme", descriptors=True)
+        self.nodes[0].unloadwallet("crashme")
+        wallet_db = os.path.join(self.nodes[0].datadir, self.chain, "wallets", "crashme", self.wallet_data_filename)
+        with sqlite3.connect(wallet_db) as conn:
+            # add "cscript" entry: key type is uint160 (20 bytes), value type is CScript (zero-length here)
+            conn.execute('INSERT INTO main VALUES(?, ?)', (b'\x07cscript' + b'\x00'*20, b'\x00'))
+        assert_raises_rpc_error(-4, "Unexpected legacy entry in descriptor wallet found.", self.nodes[0].loadwallet, "crashme")
+
+
 if __name__ == '__main__':
     WalletDescriptorTest().main ()
```
