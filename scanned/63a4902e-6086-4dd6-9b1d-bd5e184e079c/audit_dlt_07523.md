# [?] Merge bitcoin/bitcoin#31374: wallet: fix crash during watch-only wallet migration

## Summary
Severity: Unknown
Chain: Liquid
Component: ElementsProject/elements
Published: 2024-12-09
Source: https://github.com/ElementsProject/elements/commit/9039d8f1a1dfe080321f119e1bda2255e1cfdeb9
Type: security-commit

## Details
Merge bitcoin/bitcoin#31374: wallet: fix crash during watch-only wallet migration

cdd207c0e48081ab13e2c8c9886f3e2d5da1857e test: add coverage for migrating standalone imported keys (furszy)
297a876c9809e267e37481fc776cbec90056b078 test: add coverage for migrating watch-only script (furszy)
932cd1e92b6d39c6879f546867698bc8441d09cd wallet: fix crash during watch-only wallet migration (furszy)

Pull request description:

  The crash occurs because we assume the cached scripts structure will not be empty,
  but it can be empty for watch-only wallets that start blank.

  This also adds test coverage for standalone imported keys, which were also crashing
  because pubkey imports are treated the same way as hex script imports through
  `importaddress()`.

  Testing Notes:
  This can be verified by cherry-picking and running any of the test commits on master.
  It will crash there but pass on this branch.

ACKs for top commit:
  theStack:
    re-ACK cdd207c0e48081ab13e2c8c9886f3e2d5da1857e
  brunoerg:
    reACK cdd207c0e48081ab13e2c8c9886f3e2d5da1857e
  achow101:
    ACK cdd207c0e48081ab13e2c8c9886f3e2d5da1857e

Tree-SHA512: e05c77cf3e9f35f10f122a73680b3f131f683c56685c1e26b5ffc857f95195b64c8c9d4535960ed3d6f931935aa79b0b1242537462006126bdb68251f0452954

## Patch
### src/wallet/wallet.cpp
```diff
@@ -4085,7 +4085,11 @@ util::Result<void> CWallet::ApplyMigrationData(WalletBatch& local_wallet_batch,
         if (ExtractDestination(script, dest)) not_migrated_dests.emplace(dest);
     }
 
-    Assume(!m_cached_spks.empty());
+    // When the legacy wallet has no spendable scripts, the main wallet will be empty, leaving its script cache empty as well.
+    // The watch-only and/or solvable wallet(s) will contain the scripts in their respective caches.
+    if (!data.desc_spkms.empty()) Assume(!m_cached_spks.empty());
+    if (!data.watch_descs.empty()) Assume(!data.watchonly_wallet->m_cached_spks.empty());
+    if (!data.solvable_descs.empty()) Assume(!data.solvable_wallet->m_cached_spks.empty());
 
     for (auto& desc_spkm : data.desc_spkms) {
         if (m_spk_managers.count(desc_spkm->GetID()) > 0) {
```

### test/functional/wallet_migration.py
```diff
@@ -19,14 +19,16 @@
 from test_framework.key import ECPubKey
 from test_framework.test_framework import BitcoinTestFramework
 from test_framework.messages import COIN, CTransaction, CTxOut
-from test_framework.script_util import key_to_p2pkh_script, script_to_p2sh_script, script_to_p2wsh_script
+from test_framework.script import hash160
+from test_framework.script_util import key_to_p2pkh_script, key_to_p2pk_script, script_to_p2sh_script, script_to_p2wsh_script
 from test_framework.util import (
     assert_equal,
     assert_raises_rpc_error,
     sha256sum_file,
 )
 from test_framework.wallet_util import (
     get_generate_key,
+    generate_keypair,
 )
 
 
@@ -1006,6 +1008,61 @@ def check_comments():
 
         wallet.unloadwallet()
 
+    def test_migrate_simple_watch_only(self):
+        self.log.info("Test migrating a watch-only p2pk script")
+        wallet = self.create_legacy_wallet("bare_p2pk", blank=True)
+        _, pubkey = generate_keypair()
+        p2pk_script = key_to_p2pk_script(pubkey)
+        wallet.importaddress(address=p2pk_script.hex())
+        # Migrate wallet in the latest node
+        res, _ = self.migrate_and_get_rpc("bare_p2pk")
+        wo_wallet = self.master_node.get_wallet_rpc(res['watchonly_name'])
+        assert_equal(wo_wallet.listdescriptors()['descriptors'][0]['desc'], descsum_create(f'pk({pubkey.hex()})'))
+        wo_wallet.unloadwallet()
+
+    def test_manual_keys_import(self):
+        self.log.info("Test migrating standalone private keys")
+        wallet = self.create_legacy_wallet("import_privkeys", blank=True)
+        privkey, pubkey = generate_keypair(wif=True)
+        wallet.importprivkey(privkey=privkey, label="hi", rescan=False)
+
+        # Migrate and verify
+        res, wallet = self.migrate_and_get_rpc("import_privkeys")
+
+        # There should be descriptors containing the imported key for: pk(), pkh(), sh(wpkh()), wpkh()
+        key_origin = hash160(pubkey)[:4].hex()
+        pubkey_hex = pubkey.hex()
+        pk_desc = descsum_create(f'pk([{key_origin}]{pubkey_hex})')
+        pkh_desc = descsum_create(f'pkh([{key_origin}]{pubkey_hex})')
+        sh_wpkh_desc = descsum_create(f'sh(wpkh([{key_origin}]{pubkey_hex}))')
+        wpkh_desc = descsum_create(f'wpkh([{key_origin}]{pubkey_hex})')
+        expected_descs = [pk_desc, pkh_desc, sh_wpkh_desc, wpkh_desc]
+
+        # Verify all expected descriptors were migrated
+        migrated_desc = [item['desc'] for item in wallet.listdescriptors()['descriptors'] if pubkey.hex() in item['desc']]
+        assert_equal(expected_descs, migrated_desc)
+        wallet.unloadwallet()
+
+        ######################################################
+        self.log.info("Test migrating standalone public keys")
+        wallet = self.create_legacy_wallet("import_pubkeys", blank=True)
+        wallet.importpubkey(pubkey=pubkey_hex, rescan=False)
+
+        res, _ = self.migrate_and_get_rpc("import_pubkeys")
+
+        # Same as before, there should be descriptors in the watch-only wallet for the imported pubkey
+        wo_wallet = self.nodes[0].get_wallet_rpc(res['watchonly_name'])
+        # As we imported the pubkey only, there will be no key origin in the following descriptors
+        pk_desc = descsum_create(f'pk({pubkey_hex})')
+        pkh_desc = descsum_create(f'pkh({pubkey_hex})')
+        sh_wpkh_desc = descsum_create(f'sh(wpkh({pubkey_hex}))')
+        wpkh_desc = descsum_create(f'wpkh({pubkey_hex})')
+        expected_descs = [pk_desc, pkh_desc, sh_wpkh_desc, wpkh_desc]
+
+        # Verify all expected descriptors were migrated
+        migrated_desc = [item['desc'] for item in wo_wallet.listdescriptors()['descriptors']]
+        assert_equal(expected_descs, migrated_desc)
+        wo_wallet.unloadwallet()
 
     def run_test(self):
         self.master_node = self.nodes[0]
@@ -1032,6 +1089,9 @@ def run_test(self):
         self.test_avoidreuse()
         self.test_preserve_tx_extra_info()
         self.test_blank()
+        self.test_migrate_simple_watch_only()
+        self.test_manual_keys_import()
+
 
 if __name__ == '__main__':
     WalletMigrationTest(__file__).main()
```
