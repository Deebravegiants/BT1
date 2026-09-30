# [?] eth: added a check to prevent panic in bor handler (#1608)

## Summary
Severity: Unknown
Chain: Polygon
Component: 0xPolygon/bor
Published: 2025-07-02
Source: https://github.com/0xPolygon/bor/commit/8c42d84e416d5e368a6eaa5a9088a35737c8c23b
Type: security-commit

## Details
eth: added a check to prevent panic in bor handler (#1608)

## Patch
### eth/handler_bor.go
```diff
@@ -161,8 +161,10 @@ func (h *ethHandler) handleMilestone(ctx context.Context, eth *Ethereum, milesto
 
 	for lastSeenMilestoneBlockNumber < num {
 		lastSeenMilestoneBlockNumber += 1
-		blockTime := eth.blockchain.GetBlockByNumber(lastSeenMilestoneBlockNumber).Time()
-		MilestoneWhitelistedDelayTimer.UpdateSince(time.Unix(int64(blockTime), 0))
+		block := eth.blockchain.GetBlockByNumber(lastSeenMilestoneBlockNumber)
+		if block != nil && block.Header() != nil {
+			MilestoneWhitelistedDelayTimer.UpdateSince(time.Unix(int64(block.Time()), 0))
+		}
 	}
 
 	h.downloader.ProcessMilestone(num, hash)
```
