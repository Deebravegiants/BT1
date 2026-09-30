# [?] Merge bitcoin/bitcoin#26132: wallet: Fix nNextResend data race in ResubmitWalletTransactions

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2022-09-20
Source: https://github.com/dashpay/dash/commit/deeb2356a0f03b2edcde2874ad4240adea478b25
Type: security-commit

## Details
Merge bitcoin/bitcoin#26132: wallet: Fix nNextResend data race in ResubmitWalletTransactions

BACKPORT NOTE:
include missing doxygen comment from bitcoin/bitcoin#21759

fad61573ed547615f73710cb59b2fb0ecafed127 Fix nNextResend data race in ResubmitWalletTransactions (MacroFake)

Pull request description:

  Now that `ResubmitWalletTransactions` is called from more than one thread, it is no longer thread-safe.

  Introduced in 5291933fedceb9df16eb9e4627b1d7386b53ba07.

ACKs for top commit:
  achow101:
    ACK fad61573ed547615f73710cb59b2fb0ecafed127
  jonatack:
    ACK fad61573ed547615f73710cb59b2fb0ecafed127
  stickies-v:
    However, I think the current data race UB fix in fad61573e is the most critical to get into v24, so: ACK fad61573e - but open to further improvements.

Tree-SHA512: 54da2ed1c5f44e33588ac1d21ce26908fcf0bfe785c28ba8f6a479389b5ab7a0b32b016d4c482a2ccb405e0686efb61ffe23e427f5e589dc7d2b3c7469978977

## Patch
### src/wallet/wallet.cpp
```diff
@@ -1948,10 +1948,10 @@ void CWallet::ResendWalletTransactions()
 
     // Do this infrequently and randomly to avoid giving away
     // that these are our transactions.
-    if (GetTime() < nNextResend || !fBroadcastTransactions) return;
-    bool fFirst = (nNextResend == 0);
+    if (GetTime() < m_next_resend || !fBroadcastTransactions) return;
+    bool fFirst = (m_next_resend == 0);
     // resend 1-3 hours from now, ~2 hours on average.
-    nNextResend = GetTime() + (1 * 60 * 60) + GetRand(2 * 60 * 60);
+    m_next_resend = GetTime() + (1 * 60 * 60) + GetRand(2 * 60 * 60);
     if (fFirst) return;
 
     int submitted_tx_count = 0;
```

### src/wallet/wallet.h
```diff
@@ -274,7 +274,8 @@ class CWallet final : public WalletStorage, public interfaces::Chain::Notificati
     //! the current wallet version: clients below this version are not able to load the wallet
     int nWalletVersion GUARDED_BY(cs_wallet){FEATURE_BASE};
 
-    int64_t nNextResend = 0;
+    /** The next scheduled rebroadcast of wallet transactions. */
+    std::atomic<int64_t> m_next_resend{};
     /** Whether this wallet will submit newly created transactions to the node's mempool and
      * prompt rebroadcasts (see ResendWalletTransactions()). */
     bool fBroadcastTransactions = false;
```
