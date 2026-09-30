# [?] go/runtime/txpool: Fix crash on early access

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2022-04-04
Source: https://github.com/oasisprotocol/oasis-core/commit/dad525625003a5e4347dead2b5970c13f017f69a
Type: security-commit

## Details
go/runtime/txpool: Fix crash on early access

## Patch
### .changelog/4638.bugfix.md
```diff
@@ -0,0 +1 @@
+go/runtime/txpool: Fix crash on early access
```

### go/runtime/txpool/txpool.go
```diff
@@ -273,6 +273,9 @@ func (t *txPool) RemoveTxBatch(txs []hash.Hash) {
 	t.schedulerLock.Lock()
 	defer t.schedulerLock.Unlock()
 
+	if t.schedulerQueue == nil {
+		return
+	}
 	t.schedulerQueue.RemoveTxBatch(txs)
 
 	pendingScheduleSize.With(t.getMetricLabels()).Set(float64(t.schedulerQueue.Size()))
@@ -282,20 +285,35 @@ func (t *txPool) GetScheduledBatch(force bool) []*transaction.CheckedTransaction
 	t.schedulerLock.Lock()
 	defer t.schedulerLock.Unlock()
 
+	if t.schedulerQueue == nil {
+		return nil
+	}
 	return t.schedulerQueue.GetBatch(force)
 }
 
 func (t *txPool) GetPrioritizedBatch(offset *hash.Hash, limit uint32) []*transaction.CheckedTransaction {
 	t.schedulerLock.Lock()
 	defer t.schedulerLock.Unlock()
 
+	if t.schedulerQueue == nil {
+		return nil
+	}
 	return t.schedulerQueue.GetPrioritizedBatch(offset, limit)
 }
 
 func (t *txPool) GetKnownBatch(batch []hash.Hash) ([]*transaction.CheckedTransaction, map[hash.Hash]int) {
 	t.schedulerLock.Lock()
 	defer t.schedulerLock.Unlock()
 
+	if t.schedulerQueue == nil {
+		result := make([]*transaction.CheckedTransaction, 0, len(batch))
+		missing := make(map[hash.Hash]int)
+		for index, txHash := range batch {
+			result = append(result, nil)
+			missing[txHash] = index
+		}
+		return result, missing
+	}
 	return t.schedulerQueue.GetKnownBatch(batch)
 }
 
```
