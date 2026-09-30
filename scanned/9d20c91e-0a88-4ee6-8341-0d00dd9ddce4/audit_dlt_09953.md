# [?] fix: non-determinism in auction sims (#432)

## Summary
Severity: Unknown
Chain: Kava
Component: Kava-Labs/kava
Published: 2020-04-14
Source: https://github.com/Kava-Labs/kava/commit/acc96952a7df3d5f1004263d9dd9d548bc213e90
Type: security-commit

## Details
fix: non-determinism in auction sims (#432)

## Patch
### x/auction/simulation/operations/msg.go
```diff
@@ -39,7 +39,7 @@ func SimulateMsgPlaceBid(authKeeper auth.AccountKeeper, keeper auction.Keeper) s
 		})
 
 		// shuffle auctions slice so that bids are evenly distributed across auctions
-		rand.Shuffle(len(openAuctions), func(i, j int) {
+		r.Shuffle(len(openAuctions), func(i, j int) {
 			openAuctions[i], openAuctions[j] = openAuctions[j], openAuctions[i]
 		})
 		// TODO do the same for accounts?
```
