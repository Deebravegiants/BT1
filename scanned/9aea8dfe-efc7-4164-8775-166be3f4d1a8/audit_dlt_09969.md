# [?] wallet: fix crash during watch-only wallet migration

## Summary
Severity: Unknown
Chain: Liquid
Component: ElementsProject/elements
Published: 2024-11-26
Source: https://github.com/ElementsProject/elements/commit/932cd1e92b6d39c6879f546867698bc8441d09cd
Type: security-commit

## Details
wallet: fix crash during watch-only wallet migration

The crash occurs because we assume the cached scripts
structure will not be empty, but it can be empty when
the legacy wallet contained only watch-only and
solvable but not spendable scripts

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
