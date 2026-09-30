# [?] fix possible nil performance address panic in participation rewards (#509)

## Summary
Severity: Unknown
Chain: Quicksilver
Component: quicksilver-zone/quicksilver
Published: 2023-07-19
Source: https://github.com/quicksilver-zone/quicksilver/commit/c27bff6f1d3a38d17819ab0780b26d3b792f2111
Type: security-commit

## Details
fix possible nil performance address panic in participation rewards (#509)

## Patch
### x/participationrewards/keeper/rewards_validatorSelection.go
```diff
@@ -17,23 +17,25 @@ import (
 // individually in a callback.
 func (k Keeper) AllocateValidatorSelectionRewards(ctx sdk.Context) {
 	k.icsKeeper.IterateZones(ctx, func(_ int64, zone *icstypes.Zone) (stop bool) {
-		k.Logger(ctx).Info("zones", "chain_id", zone.ChainId, "performance address", zone.PerformanceAddress.Address)
-
-		// obtain zone performance account rewards
-		rewardsQuery := distrtypes.QueryDelegationTotalRewardsRequest{DelegatorAddress: zone.PerformanceAddress.Address}
-		bz := k.cdc.MustMarshal(&rewardsQuery)
-
-		k.IcqKeeper.MakeRequest(
-			ctx,
-			zone.ConnectionId,
-			zone.ChainId,
-			"cosmos.distribution.v1beta1.Query/DelegationTotalRewards",
-			bz,
-			sdk.NewInt(-1),
-			types.ModuleName,
-			ValidatorSelectionRewardsCallbackID,
-			0,
-		)
+		if zone.PerformanceAddress != nil {
+			k.Logger(ctx).Info("zones", "chain_id", zone.ChainId, "performance address", zone.PerformanceAddress.Address)
+
+			// obtain zone performance account rewards
+			rewardsQuery := distrtypes.QueryDelegationTotalRewardsRequest{DelegatorAddress: zone.PerformanceAddress.Address}
+			bz := k.cdc.MustMarshal(&rewardsQuery)
+
+			k.IcqKeeper.MakeRequest(
+				ctx,
+				zone.ConnectionId,
+				zone.ChainId,
+				"cosmos.distribution.v1beta1.Query/DelegationTotalRewards",
+				bz,
+				sdk.NewInt(-1),
+				types.ModuleName,
+				ValidatorSelectionRewardsCallbackID,
+				0,
+			)
+		}
 		return false
 	})
 }
```
