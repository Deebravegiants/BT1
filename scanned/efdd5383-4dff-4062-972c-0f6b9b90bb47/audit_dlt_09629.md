# [?] fix: use wider integer to avoid potential overflow scenarios

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2026-02-11
Source: https://github.com/dashpay/dash/commit/abb9aa1e1b5b526f08999d37620dafdc6102215d
Type: security-commit

## Details
fix: use wider integer to avoid potential overflow scenarios

Also fetch network params once, remove unusual clamping logic as
validators operate on 64-bit integers.

## Patch
### src/interfaces/node.h
```diff
@@ -146,6 +146,7 @@ class GOV
         int nextsuperblock{0};
         int fundingthreshold{0};
         CAmount governancebudget{0};
+        int64_t targetSpacing{0};
         int relayRequiredConfs{1};
         int requiredConfs{6};
     };
```

### src/node/interfaces.cpp
```diff
@@ -282,6 +282,7 @@ class GOVImpl : public GOV
         info.proposalfee = GOVERNANCE_PROPOSAL_FEE_TX;
         info.superblockcycle = consensusParams.nSuperblockCycle;
         info.superblockmaturitywindow = consensusParams.nSuperblockMaturityWindow;
+        info.targetSpacing = consensusParams.nPowTargetSpacing;
         info.relayRequiredConfs = GOVERNANCE_MIN_RELAY_FEE_CONFIRMATIONS;
         info.requiredConfs = GOVERNANCE_FEE_CONFIRMATIONS;
         if (ctx.dmnman) {
```

### src/qt/proposalwizard.cpp
```diff
@@ -67,6 +67,8 @@ ProposalWizard::ProposalWizard(WalletModel* walletModel, QWidget* parent) :
     {
         // Load governance parameters
         const auto info = m_walletModel->node().gov().getGovernanceInfo();
+        m_superblock_cycle = info.superblockcycle;
+        m_target_spacing = info.targetSpacing;
         m_relayRequiredConfs = info.relayRequiredConfs;
         m_requiredConfs = info.requiredConfs;
 
@@ -76,7 +78,7 @@ ProposalWizard::ProposalWizard(WalletModel* walletModel, QWidget* parent) :
         const int cycle = info.superblockcycle;
         for (int i = 0; i < 12; ++i) {
             const int sbHeight = nextSb + i * cycle;
-            const qint64 secs = static_cast<qint64>(i) * cycle * Params().GetConsensus().nPowTargetSpacing;
+            const qint64 secs = static_cast<qint64>(i) * cycle * m_target_spacing;
             const auto dt = QDateTime::currentDateTimeUtc().addSecs(secs).toLocalTime();
             m_ui->comboFirstPayment->addItem(QLocale().toString(dt, QLocale::ShortFormat), sbHeight);
         }
@@ -130,39 +132,29 @@ ProposalWizard::~ProposalWizard()
 
 void ProposalWizard::buildJsonAndHex()
 {
+    const int64_t multiplier = std::numeric_limits<int64_t>::max() / std::max<int64_t>(1, m_target_spacing);
+
     // Compute start/end epochs from selected superblocks
-    int start_epoch = 0;
-    int end_epoch = 0;
-    int firstSb = m_ui->comboFirstPayment->currentData().toInt();
-    int payments = m_ui->comboPayments->currentData().toInt();
-    if (firstSb > 0 && payments > 0) {
-        const int cycle = Params().GetConsensus().nSuperblockCycle;
-        if (cycle > 0) {
-            const int prevSb = firstSb - cycle;
-            const int lastSb = firstSb + (payments - 1) * cycle;
-            const int nextAfterLast = lastSb + cycle;
+    int64_t start_epoch = 0;
+    int64_t end_epoch = 0;
+    const int64_t first_sb = m_ui->comboFirstPayment->currentData().toInt();
+    const int64_t payments = m_ui->comboPayments->currentData().toInt();
+    if (first_sb > 0 && payments > 0) {
+        if (m_superblock_cycle > 0) {
+            const int64_t prev_sb{first_sb - m_superblock_cycle};
+            const int64_t last_sb{first_sb + (payments - 1) * m_superblock_cycle};
+            const int64_t next_sb{last_sb + m_superblock_cycle};
             // Midpoints in blocks; convert roughly to seconds relative to now
-            const int startMidBlocks = (firstSb + prevSb) / 2;
-            const int endMidBlocks = (lastSb + nextAfterLast) / 2;
+            const int64_t start_blocks{(first_sb + prev_sb) / 2};
+            const int64_t end_blocks{(last_sb + next_sb) / 2};
             // We don't know absolute time for those heights in GUI; approximate using consensus block time
             // Use now as baseline; this is only to pass validator and give a stable window
-            const qint64 now = QDateTime::currentSecsSinceEpoch();
-            const int64_t targetSpacing = Params().GetConsensus().nPowTargetSpacing; // seconds
-            const int64_t deltaStartBlocks = static_cast<int64_t>(startMidBlocks) - static_cast<int64_t>(firstSb);
-            const int64_t deltaEndBlocks = static_cast<int64_t>(endMidBlocks) - static_cast<int64_t>(firstSb);
-            // Guard against overflow when multiplying
-            const int64_t maxMultiplier = std::numeric_limits<int64_t>::max() / std::max<int64_t>(1, targetSpacing);
-            const int64_t clampedDeltaStart = std::clamp<int64_t>(deltaStartBlocks, -maxMultiplier, maxMultiplier);
-            const int64_t clampedDeltaEnd = std::clamp<int64_t>(deltaEndBlocks, -maxMultiplier, maxMultiplier);
-            const int64_t startOffsetSecs = clampedDeltaStart * targetSpacing;
-            const int64_t endOffsetSecs = clampedDeltaEnd * targetSpacing;
-            const int64_t startEpoch64 = now + startOffsetSecs;
-            const int64_t endEpoch64 = now + endOffsetSecs;
-            // Clamp to 32-bit int range used by validator
-            start_epoch = static_cast<int>(
-                std::clamp<int64_t>(startEpoch64, std::numeric_limits<int>::min(), std::numeric_limits<int>::max()));
-            end_epoch = static_cast<int>(
-                std::clamp<int64_t>(endEpoch64, std::numeric_limits<int>::min(), std::numeric_limits<int>::max()));
+            const qint64 now{QDateTime::currentSecsSinceEpoch()};
+            const int64_t delta_start{start_blocks - first_sb};
+            const int64_t delta_end{end_blocks - first_sb};
+            // Guard against overflow when multiplying by clamping deltas first
+            start_epoch = now + std::clamp<int64_t>(delta_start, -multiplier, multiplier) * m_target_spacing;
+            end_epoch = now + std::clamp<int64_t>(delta_end, -multiplier, multiplier) * m_target_spacing;
         }
     }
 
```

### src/qt/proposalwizard.h
```diff
@@ -51,6 +51,8 @@ private Q_SLOTS:
     QString m_txid;
     QString m_fee_formatted;
     qint64 m_prepareTime{0};
+    int64_t m_superblock_cycle{0};
+    int64_t m_target_spacing{0};
     int m_relayRequiredConfs{1};
     int m_requiredConfs{6};
     int m_lastConfs{-1};
```
