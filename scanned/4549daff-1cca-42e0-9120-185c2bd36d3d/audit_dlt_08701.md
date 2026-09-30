# [?] fix: guard zero batch count in inbox search and avoid validator underflow (#4028)

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-12-02
Source: https://github.com/OffchainLabs/nitro/commit/8a65e48cb9e152757abc055377454f8f0507042f
Type: security-commit

## Details
fix: guard zero batch count in inbox search and avoid validator underflow (#4028)

Co-authored-by: Gabriel de Quadros Ligneul <8294320+gligneul@users.noreply.github.com>

## Patch
### arbnode/inbox_tracker.go
```diff
@@ -233,6 +233,9 @@ func (t *InboxTracker) FindInboxBatchContainingMessage(pos arbutil.MessageIndex)
 	if err != nil {
 		return 0, false, err
 	}
+	if batchCount == 0 {
+		return 0, false, nil
+	}
 	low := uint64(0)
 	high := batchCount - 1
 	lastBatchMessageCount, err := t.GetBatchMessageCount(high)
```

### staker/block_validator.go
```diff
@@ -1418,10 +1418,15 @@ func (v *BlockValidator) checkValidatedGSCaughtUp() (bool, error) {
 			log.Error("failed reading batch count", "err", err)
 			batchCount = 0
 		}
-		batchMsgCount, err := v.inboxTracker.GetBatchMessageCount(batchCount - 1)
-		if err != nil {
-			log.Error("failed reading batchMsgCount", "err", err)
+		var batchMsgCount arbutil.MessageIndex
+		if batchCount == 0 {
 			batchMsgCount = 0
+		} else {
+			batchMsgCount, err = v.inboxTracker.GetBatchMessageCount(batchCount - 1)
+			if err != nil {
+				log.Error("failed reading batchMsgCount", "err", err)
+				batchMsgCount = 0
+			}
 		}
 		processedMsgCount, err := v.streamer.GetProcessedMessageCount()
 		if err != nil {
```
