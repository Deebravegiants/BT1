# [?] fix for goal node status crash - no longer getting block (#5100)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2023-02-02
Source: https://github.com/algorand/go-algorand/commit/3355ce6728876225521517f0fc10e86105eeb1b2
Type: security-commit

## Details
fix for goal node status crash - no longer getting block (#5100)

## Patch
### daemon/algod/api/server/v2/handlers.go
```diff
@@ -772,12 +772,6 @@ func (v2 *Handlers) GetStatus(ctx echo.Context) error {
 		return internalError(ctx, err, errFailedRetrievingNodeStatus, v2.Log)
 	}
 
-	ledger := v2.Node.LedgerForAPI()
-	latestBlkHdr, err := ledger.BlockHdr(ledger.Latest())
-	if err != nil {
-		return internalError(ctx, err, errFailedRetrievingLatestBlockHeaderStatus, v2.Log)
-	}
-
 	response := model.NodeStatusResponse{
 		LastRound:                   uint64(stat.LastRound),
 		LastVersion:                 string(stat.LastVersion),
@@ -813,7 +807,7 @@ func (v2 *Handlers) GetStatus(ctx echo.Context) error {
 		votesNo := votes - votesYes
 		upgradeDelay := uint64(stat.UpgradeDelay)
 		response.UpgradeVotesRequired = &upgradeThreshold
-		response.UpgradeNodeVote = &latestBlkHdr.UpgradeApprove
+		response.UpgradeNodeVote = &stat.UpgradeApprove
 		response.UpgradeDelay = &upgradeDelay
 		response.UpgradeVotes = &votes
 		response.UpgradeYesVotes = &votesYes
```
