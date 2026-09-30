# [?] Fix participation panics (#107)

## Summary
Severity: Unknown
Chain: Quicksilver
Component: quicksilver-zone/quicksilver
Published: 2022-06-16
Source: https://github.com/quicksilver-zone/quicksilver/commit/f9c79083fd47b9b233552305c91177be31d5bb04
Type: security-commit

## Details
Fix participation panics (#107)

* remove height check; this causes code 11 (gas?) error and needs properly investigating

* clarify memo intent error messages

* remove superfluous logging

* fix: guard against nil rewards being returned

* fix: guard against nil allocations

* callback names should be globally unique

## Patch
### x/interchainquery/keeper/msg_server.go
```diff
@@ -29,7 +29,8 @@ var _ types.MsgServer = msgServer{}
 func (k msgServer) SubmitQueryResponse(goCtx context.Context, msg *types.MsgSubmitQueryResponse) (*types.MsgSubmitQueryResponseResponse, error) {
 	ctx := sdk.UnwrapSDKContext(goCtx)
 	q, found := k.GetQuery(ctx, msg.QueryId)
-	if found && q.LastHeight.Int64() != ctx.BlockHeader().Height {
+	//if found && q.LastHeight.Int64() != ctx.BlockHeader().Height {
+	if found {
 		pathParts := strings.Split(q.QueryType, "/")
 		if pathParts[len(pathParts)-1] == "key" {
 			if msg.ProofOps == nil {
```

### x/interchainstaking/types/zones.go
```diff
@@ -97,12 +97,12 @@ func (z *RegisteredZone) ConvertMemoToOrdinalIntents(coins sdk.Coins, memo strin
 
 	memoBytes, err := base64.StdEncoding.DecodeString(memo)
 	if err != nil {
-		fmt.Println("Error: Failed to decode base64 memo", err)
+		fmt.Println("unable to determine intent from memo: Failed to decode base64 message", err)
 		return out
 	}
 
 	if len(memoBytes)%21 != 0 { // memo must be one byte (1-200) weight then 20 byte valoperAddress
-		fmt.Println("Error: Message was incorrect length", len(memoBytes))
+		fmt.Println("unable to determine intent from memo: Message was incorrect length", len(memoBytes))
 		return out
 	}
 
```

### x/participationrewards/keeper/abci.go
```diff
@@ -2,18 +2,9 @@ package keeper
 
 import (
 	sdk "github.com/cosmos/cosmos-sdk/types"
-	"github.com/ingenuity-build/quicksilver/x/participationrewards/types"
 )
 
 // BeginBlocker of participationrewards module
 func (k Keeper) BeginBlocker(ctx sdk.Context) {
-	// hartbeat logger (for dev & debugging)
-	if ctx.BlockHeight()%int64(10) == 0 {
-		k.Logger(ctx).Info("up and running")
-		k.Logger(ctx).Info(
-			"module account",
-			"account", k.accountKeeper.GetModuleAccount(ctx, types.ModuleName),
-			"address", k.accountKeeper.GetModuleAddress(types.ModuleName),
-		)
-	}
+
 }
```

### x/participationrewards/keeper/callbacks.go
```diff
@@ -40,7 +40,7 @@ func (c Callbacks) AddCallback(id string, fn interface{}) types.QueryCallbacks {
 
 func (c Callbacks) RegisterCallbacks() types.QueryCallbacks {
 	a := c.
-		AddCallback("rewards", Callback(RewardsCallback))
+		AddCallback("perfrewards", Callback(RewardsCallback))
 
 	return a.(Callbacks)
 }
```

### x/participationrewards/keeper/distribution.go
```diff
@@ -41,6 +41,9 @@ func (k Keeper) getRewardsAllocations(ctx sdk.Context) rewardsAllocation {
 		// TODO: this needs to be verified as it currently does not trigger anymore
 		for _, zone := range k.icsKeeper.AllRegisteredZones(ctx) {
 			for _, di := range k.icsKeeper.AllOrdinalizedIntents(ctx, zone, false) {
+				// this already happens in zone. If we are certain about ordering,
+				// we should only iterate intents once per epoch boundary as it'll
+				// get unwieldy.
 				k.icsKeeper.SetIntent(ctx, zone, di, true)
 			}
 		}
@@ -206,6 +209,11 @@ func (k Keeper) getZoneAllocations(ctx sdk.Context, zoneProps map[string]sdk.Dec
 
 	zoneAllocations := make(map[string]sdk.Coins)
 
+	if len(allocation) == 0 {
+		// if there are no coins, we can never fetch the first one! short circuit.
+		return zoneAllocations
+	}
+
 	for zid, zp := range zoneProps {
 		zoneAllocations[zid] = sdk.NewCoins(
 			sdk.NewCoin(
```

### x/participationrewards/keeper/rewards_validatorSelection.go
```diff
@@ -66,7 +66,7 @@ func (k Keeper) allocateValidatorSelectionRewards(
 			bz,
 			sdk.NewInt(-1),
 			types.ModuleName,
-			"rewards",
+			"perfrewards",
 			0,
 		)
 
@@ -195,6 +195,11 @@ func (k Keeper) calcOverallScores(
 	k.Logger(ctx).Info("calculate performance & overall scores")
 
 	rewards := delegatorRewards.GetRewards()
+	if rewards == nil {
+		k.Logger(ctx).Error("No delegator rewards")
+		return nil
+	}
+
 	total := delegatorRewards.GetTotal().AmountOf(zone.BaseDenom)
 	expected := total.Quo(sdk.NewDec(int64(len(rewards))))
 
```
