# [?] fix(coinjoin): make pending-observation locks crash-safe and cheap to poll

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2026-07-25
Source: https://github.com/dashpay/dash/commit/f9c4bebea16e4a91a45bbda63917c0da78e9ec77
Type: security-commit

## Details
fix(coinjoin): make pending-observation locks crash-safe and cheap to poll

Review follow-ups to the pending-observation mechanism:

- AddPendingObservation() persisted the wallet locks before the
  cj_pending_obs record which owns them. Those are two separate writes, so
  a crash in between left persistently locked coins behind with nothing
  tracking them and no timeout to release them. Write the record first and
  only persist the locks if that succeeded; the resulting order is
  self-healing, CheckPendingObservations() drops a pending entry as soon as
  it sees its coin is not locked.

- CheckPendingObservations() constructed a WalletBatch on every pass, and
  every WalletBatch checkpoints the wallet database when it goes out of
  scope. Open it lazily, on the first actual write, and read the record
  with fFlushOnClose=false.

- Do not persist the timer refresh applied to an input which is spent in
  chain/mempool but not according to the wallet. Such an entry can be
  terminal, and rewriting the record for it buys nothing: the worst a
  restart can do is re-run the check once. Log it so it is diagnosable.

- Schedule the check on its own rather than running it from DoMaintenance
  ahead of the mixing gates. It keeps the same property - pending inputs
  unlock even while mixing or CoinJoin itself is disabled - with one
  cadence for both relay and block-only mode instead of once per second in
  one and once per minute in the other. Releasing these locks is pure
  bookkeeping: the outpoints are the ones the finalized mixing transaction
  spends, so by the time the wallet observes the spend they could not be
  selected again anyway.

- Move the timeout next to the other CoinJoin timeouts in coinjoin.h and
  restore the alphabetical include order.

- Mark the wrapped log format strings with /* Continued */ so lint-logs.py
  is satisfied, matching init.cpp and net_processing.cpp. It only inspects
  the first line of a log call and requires it to end with "\n".

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### src/coinjoin/client.cpp
```diff
@@ -17,9 +17,9 @@
 #include <coins.h>
 #include <core_io.h>
 #include <net.h>
-#include <txmempool.h>
 #include <netmessagemaker.h>
 #include <shutdown.h>
+#include <txmempool.h>
 #include <util/check.h>
 #include <util/fs_helpers.h>
 #include <util/moneystr.h>
@@ -33,6 +33,7 @@
 #include <wallet/walletdb.h>
 
 #include <memory>
+#include <optional>
 #include <ranges>
 
 #include <univalue.h>
@@ -633,22 +634,32 @@ void CCoinJoinClientManager::AddPendingObservation(const std::vector<COutPoint>&
     LoadPendingObservations(batch);
 
     const int64_t nNow{GetTime()};
-    bool fPersisted{true};
     for (const auto& outpoint : outpoints) {
-        // Persist the lock so that a restart before the finalized transaction is
-        // observed cannot make the input available for selection again
-        fPersisted &= m_wallet->LockCoin(outpoint, &batch);
         m_pending_obs.emplace(outpoint, nNow);
+    }
+
+    // NOTE: the record which owns these locks has to be written BEFORE the locks
+    // themselves. These are two separate writes and a crash in between must not leave
+    // persistently locked coins behind with nothing tracking them: nothing would ever
+    // release them again. The opposite order is self-healing, CheckPendingObservations()
+    // drops a pending entry as soon as it sees its coin is not locked.
+    bool fPersisted{batch.WriteCoinJoinPendingObs(m_pending_obs)};
+    for (const auto& outpoint : outpoints) {
+        // The coins are locked in memory already (see PrepareDenominate), this only
+        // persists the lock so that a restart before the finalized transaction is
+        // observed cannot make the input available for selection again. Skip persisting
+        // it if the record above could not be written though, a persistent lock with
+        // nothing left to release it strands the input.
+        if (!m_wallet->LockCoin(outpoint, fPersisted ? &batch : nullptr)) fPersisted = false;
         WalletCJLogPrint(m_wallet, "CCoinJoinClientManager::%s -- %s is locked until the finalized mixing transaction is observed\n",
                          __func__, outpoint.ToStringShort());
     }
-    fPersisted &= batch.WriteCoinJoinPendingObs(m_pending_obs);
     if (!fPersisted) {
         // The in-memory lock still protects these inputs for as long as this process
         // runs, but a restart would make them selectable again while a valid mixing
         // transaction spending them may already be in flight. Nothing we can do about
         // it here beyond making the failure loud - the wallet database is broken.
-        LogPrintf("CCoinJoinClientManager::%s -- ERROR: failed to persist locks for %d successfully mixed input(s), "
+        LogPrintf("CCoinJoinClientManager::%s -- ERROR: failed to persist locks for %d successfully mixed input(s), " /* Continued */
                   "they will not survive a restart\n",
                   __func__, outpoints.size());
     }
@@ -676,8 +687,20 @@ void CCoinJoinClientManager::CheckPendingObservations(const CTxMemPool& mempool)
     LOCK(m_wallet->cs_wallet);
     LOCK(cs_pending_obs);
 
-    wallet::WalletBatch batch(m_wallet->GetDatabase());
-    LoadPendingObservations(batch);
+    if (!m_pending_obs_loaded) {
+        // Read-only, no need to checkpoint the database on the way out
+        wallet::WalletBatch batch_load(m_wallet->GetDatabase(), /*_fFlushOnClose=*/false);
+        LoadPendingObservations(batch_load);
+    }
+
+    // Constructed on the first write only: this keeps running for as long as anything is
+    // pending and every WalletBatch checkpoints the wallet database when it goes out of
+    // scope, which is far too expensive to pay for a pass which changes nothing.
+    std::optional<wallet::WalletBatch> batch;
+    const auto get_batch = [&]() -> wallet::WalletBatch& {
+        if (!batch.has_value()) batch.emplace(m_wallet->GetDatabase());
+        return batch.value();
+    };
 
     const int64_t nNow{GetTime()};
     const bool fSynced{m_mn_sync.IsBlockchainSynced()};
@@ -695,15 +718,15 @@ void CCoinJoinClientManager::CheckPendingObservations(const CTxMemPool& mempool)
             // selectable anyway, drop the protective lock
             WalletCJLogPrint(m_wallet, "CCoinJoinClientManager::%s -- observed spend of %s, releasing lock\n", __func__,
                              outpoint.ToStringShort());
-            m_wallet->UnlockCoin(outpoint, &batch);
+            m_wallet->UnlockCoin(outpoint, &get_batch());
             it = m_pending_obs.erase(it);
             fChanged = true;
             continue;
         }
         // Only ever consult chain/mempool spentness on a synced chain: while catching up
         // the spending transaction may sit in a block we have not downloaded yet, and
         // releasing the input on the strength of that would defeat the whole point
-        if (fSynced && nNow - it->second >= PENDING_OBSERVATION_TIMEOUT_SECONDS) {
+        if (fSynced && nNow - it->second >= COINJOIN_PENDING_OBSERVATION_TIMEOUT) {
             // NOTE: findCoins() reports outputs which exist in the chain UTXO set or are
             // created by a mempool transaction; it does NOT know whether a mempool
             // transaction spends them (CCoinsViewMemPool::GetCoin never looks at
@@ -716,22 +739,30 @@ void CCoinJoinClientManager::CheckPendingObservations(const CTxMemPool& mempool)
                 // Still unspent in chain and mempool long after the session completed -
                 // the finalized transaction most likely never propagated, release the
                 // input so the wallet does not lose it forever
-                LogPrintf("CCoinJoinClientManager::%s -- WARNING: never observed finalized mixing transaction for %s, "
+                LogPrintf("CCoinJoinClientManager::%s -- WARNING: never observed finalized mixing transaction for %s, " /* Continued */
                           "releasing lock after %d seconds\n",
-                          __func__, outpoint.ToStringShort(), PENDING_OBSERVATION_TIMEOUT_SECONDS);
-                m_wallet->UnlockCoin(outpoint, &batch);
+                          __func__, outpoint.ToStringShort(), COINJOIN_PENDING_OBSERVATION_TIMEOUT);
+                m_wallet->UnlockCoin(outpoint, &get_batch());
                 it = m_pending_obs.erase(it);
                 fChanged = true;
                 continue;
             }
             // Spent according to chain/mempool but the wallet has not recorded the
-            // spending transaction yet, keep waiting for it
+            // spending transaction yet, keep waiting for it. Note that this can be
+            // terminal: if the wallet never learns about the spend (restored from an old
+            // backup and never rescanned, say) the entry stays for good. Releasing it
+            // would be wrong - such a coin still looks unspent to the wallet and could be
+            // selected for another session - so only refresh the timer to keep the check
+            // above from running on every pass. The refresh is deliberately not persisted,
+            // the worst a restart can do is re-run the check once.
+            WalletCJLogPrint(m_wallet, "CCoinJoinClientManager::%s -- %s is spent in chain/mempool but not according to " /* Continued */
+                                       "the wallet, keeping it locked\n",
+                             __func__, outpoint.ToStringShort());
             it->second = nNow;
-            fChanged = true;
         }
         ++it;
     }
-    if (fChanged && !batch.WriteCoinJoinPendingObs(m_pending_obs)) {
+    if (fChanged && !get_batch().WriteCoinJoinPendingObs(m_pending_obs)) {
         LogPrintf("CCoinJoinClientManager::%s -- ERROR: failed to persist %d pending observation(s)\n", __func__,
                   m_pending_obs.size());
     }
@@ -1873,16 +1904,9 @@ void CCoinJoinClientManager::UpdatedBlockTip(const CBlockIndex* pindex)
 
 void CCoinJoinClientManager::DoMaintenance(ChainstateManager& chainman, CConnman& connman, const CTxMemPool& mempool)
 {
-    if (ShutdownRequested()) return;
-
-    // Run this before the mixing gates below: inputs of already completed sessions
-    // must be able to unlock even when mixing or CoinJoin itself is disabled,
-    // otherwise their persisted locks could linger forever
-    CheckPendingObservations(mempool);
-
     if (!CCoinJoinClientOptions::IsEnabled()) return;
 
-    if (!m_mn_sync.IsBlockchainSynced()) return;
+    if (!m_mn_sync.IsBlockchainSynced() || ShutdownRequested()) return;
 
     static int nTick = 0;
     static int nDoAutoNextRun = nTick + COINJOIN_AUTO_TIMEOUT_MIN;
```

### src/coinjoin/client.h
```diff
@@ -231,10 +231,6 @@ class CCoinJoinClientManager : public interfaces::CoinJoin::Client
 
     void UpdatedSuccessBlock();
 
-    //! How long to keep waiting for the finalized mixing transaction before
-    //! double-checking chain/mempool spentness and potentially releasing the inputs
-    static constexpr int64_t PENDING_OBSERVATION_TIMEOUT_SECONDS{60 * 60};
-
     /// Keep the given successfully mixed inputs locked (persistently) until the wallet
     /// observes a transaction spending them
     void AddPendingObservation(const std::vector<COutPoint>& outpoints) EXCLUSIVE_LOCKS_REQUIRED(!cs_pending_obs);
@@ -246,7 +242,7 @@ class CCoinJoinClientManager : public interfaces::CoinJoin::Client
     void UpdatedBlockTip(const CBlockIndex* pindex);
 
     void DoMaintenance(ChainstateManager& chainman, CConnman& connman, const CTxMemPool& mempool)
-        EXCLUSIVE_LOCKS_REQUIRED(!cs_deqsessions, !cs_pending_obs);
+        EXCLUSIVE_LOCKS_REQUIRED(!cs_deqsessions);
 
     // interfaces::CoinJoin::Client overrides
     void disableAutobackups() override { fCreateAutoBackups = false; }
```

### src/coinjoin/coinjoin.h
```diff
@@ -47,6 +47,10 @@ static constexpr int COINJOIN_AUTO_TIMEOUT_MIN = 5;
 static constexpr int COINJOIN_AUTO_TIMEOUT_MAX = 15;
 static constexpr int COINJOIN_QUEUE_TIMEOUT = 30;
 static constexpr int COINJOIN_SIGNING_TIMEOUT = 15;
+//! How long a successfully mixed input is kept locked while waiting for the finalized
+//! mixing transaction before chain/mempool spentness is double-checked and the input is
+//! potentially released, in seconds
+static constexpr int64_t COINJOIN_PENDING_OBSERVATION_TIMEOUT = 60 * 60;
 
 static constexpr size_t COINJOIN_ENTRY_MAX_SIZE = 9;
 
```

### src/coinjoin/walletman.cpp
```diff
@@ -120,16 +120,19 @@ CJWalletManagerImpl::~CJWalletManagerImpl()
 
 void CJWalletManagerImpl::Schedule(CConnman& connman, CScheduler& scheduler)
 {
-    if (!m_relay_txes) {
-        // Mixing needs transaction relay, so no CoinJoin activity is scheduled here.
-        // Inputs of a session which completed before an earlier shutdown are a different
-        // matter: their locks were persisted and are restored with the wallet, so the
-        // check which releases them once their spend is observed (or once they time out)
-        // has to keep running even in block-only mode - nothing else would ever unlock them.
-        scheduler.scheduleEvery(std::bind(&CJWalletManagerImpl::CheckPendingObservations, this),
-                                std::chrono::minutes{1});
-        return;
-    }
+    // Inputs of a successfully completed session stay locked until the finalized mixing
+    // transaction is observed and those locks are persisted, so they are restored with
+    // the wallet. Releasing them has to keep running independently of mixing itself:
+    // even with CoinJoin disabled, mixing stopped or transaction relay unavailable
+    // (block-only mode, where nothing below is scheduled at all) nothing else would ever
+    // unlock them. NOTE: no CJWalletManager exists on a masternode (see init.cpp), a
+    // wallet with pending observations opened there keeps its inputs locked until it is
+    // opened on a regular node again or the user unlocks them via `lockunspent`.
+    scheduler.scheduleEvery(std::bind(&CJWalletManagerImpl::CheckPendingObservations, this), std::chrono::minutes{1});
+
+    // Mixing needs transaction relay
+    if (!m_relay_txes) return;
+
     scheduler.scheduleEvery(std::bind(&CJWalletManagerImpl::DoMaintenance, this, std::ref(connman)),
                             std::chrono::seconds{1});
 }
```
