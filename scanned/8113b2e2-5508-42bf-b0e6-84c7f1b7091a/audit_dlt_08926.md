# [?] node/pkg/solana: fix solanaConnectionErrors panic

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2021-07-30
Source: https://github.com/wormhole-foundation/wormhole/commit/b2495ca43ee6e94872f7ba5a2296330d8ee3ecfb
Type: security-commit

## Details
node/pkg/solana: fix solanaConnectionErrors panic

Change-Id: I75889897e47902abe54cc45153934e73f1f3dcd4

## Patch
### bridge/pkg/solana/client.go
```diff
@@ -214,7 +214,7 @@ func (s *SolanaWatcher) fetchBlock(ctx context.Context, slot uint64) {
 
 	queryLatency.WithLabelValues("get_confirmed_block", string(s.commitment)).Observe(time.Since(start).Seconds())
 	if err != nil {
-		solanaConnectionErrors.WithLabelValues("get_confirmed_block_error").Inc()
+		solanaConnectionErrors.WithLabelValues(string(s.commitment), "get_confirmed_block_error").Inc()
 		s.logger.Error("failed to request block", zap.Error(err), zap.Uint64("slot", slot),
 			zap.String("commitment", string(s.commitment)))
 		return
@@ -277,7 +277,7 @@ OUTER:
 		})
 		queryLatency.WithLabelValues("get_confirmed_transaction", string(s.commitment)).Observe(time.Since(start).Seconds())
 		if err != nil {
-			solanaConnectionErrors.WithLabelValues("get_confirmed_transaction_error").Inc()
+			solanaConnectionErrors.WithLabelValues(string(s.commitment), "get_confirmed_transaction_error").Inc()
 			s.logger.Error("failed to request transaction",
 				zap.Error(err),
 				zap.Uint64("slot", slot),
@@ -356,7 +356,7 @@ func (s *SolanaWatcher) fetchMessageAccount(ctx context.Context, acc solana.Publ
 	})
 	queryLatency.WithLabelValues("get_account_info", string(s.commitment)).Observe(time.Since(start).Seconds())
 	if err != nil {
-		solanaConnectionErrors.WithLabelValues("get_account_info_error").Inc()
+		solanaConnectionErrors.WithLabelValues(string(s.commitment), "get_account_info_error").Inc()
 		s.logger.Error("failed to request account",
 			zap.Error(err),
 			zap.Uint64("slot", slot),
@@ -366,7 +366,7 @@ func (s *SolanaWatcher) fetchMessageAccount(ctx context.Context, acc solana.Publ
 	}
 
 	if !info.Value.Owner.Equals(s.bridge) {
-		solanaConnectionErrors.WithLabelValues("account_owner_mismatch").Inc()
+		solanaConnectionErrors.WithLabelValues(string(s.commitment), "account_owner_mismatch").Inc()
 		s.logger.Error("account has invalid owner",
 			zap.Uint64("slot", slot),
 			zap.String("commitment", string(s.commitment)),
@@ -377,7 +377,7 @@ func (s *SolanaWatcher) fetchMessageAccount(ctx context.Context, acc solana.Publ
 
 	data := info.Value.Data.GetBinary()
 	if string(data[:3]) != "msg" {
-		solanaConnectionErrors.WithLabelValues("bad_account_data").Inc()
+		solanaConnectionErrors.WithLabelValues(string(s.commitment), "bad_account_data").Inc()
 		s.logger.Error("account is not a message account",
 			zap.Uint64("slot", slot),
 			zap.String("commitment", string(s.commitment)),
```
