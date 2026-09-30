# [?] fix(sender): nil pointer panic when resubmitting failure (#1133)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/scroll
Published: 2024-02-19
Source: https://github.com/scroll-tech/scroll/commit/e5e5cafc48813ca6f777fc58f3f7f376b7da833f
Type: security-commit

## Details
fix(sender): nil pointer panic when resubmitting failure (#1133)

Co-authored-by: colinlyguo <colinlyguo@users.noreply.github.com>

## Patch
### common/version/version.go
```diff
@@ -5,7 +5,7 @@ import (
 	"runtime/debug"
 )
 
-var tag = "v4.3.63"
+var tag = "v4.3.64"
 
 var commit = func() string {
 	if info, ok := debug.ReadBuildInfo(); ok {
```

### rollup/internal/controller/sender/sender.go
```diff
@@ -472,7 +472,7 @@ func (s *Sender) checkPendingTransaction() {
 
 			if newTx, err := s.resubmitTransaction(tx, baseFee); err != nil {
 				s.metrics.resubmitTransactionFailedTotal.WithLabelValues(s.service, s.name).Inc()
-				log.Error("failed to resubmit transaction", "context ID", txnToCheck.ContextID, "sender meta", s.getSenderMeta(), "from", s.auth.From.String(), "nonce", newTx.Nonce(), "err", err)
+				log.Error("failed to resubmit transaction", "context ID", txnToCheck.ContextID, "sender meta", s.getSenderMeta(), "from", s.auth.From.String(), "nonce", tx.Nonce(), "err", err)
 			} else {
 				err := s.db.Transaction(func(dbTX *gorm.DB) error {
 					// Update the status of the original transaction as replaced, while still checking its confirmation status.
```
