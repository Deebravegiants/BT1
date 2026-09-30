# [?] fix(x/protocolpool): fix potential panic and missing error handling (#18995)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2024-01-10
Source: https://github.com/cosmos/cosmos-sdk/commit/8d71191a4876c81c3d73750c2f5cd07e2190cdde
Type: security-commit

## Details
fix(x/protocolpool): fix potential panic and missing error handling (#18995)

## Patch
### x/protocolpool/keeper/genesis.go
```diff
@@ -28,11 +28,11 @@ func (k Keeper) InitGenesis(ctx context.Context, data *types.GenesisState) error
 	}
 	for _, budget := range data.Budget {
 		// Validate StartTime
-		if budget.StartTime.IsZero() || budget.StartTime == nil {
+		if budget.StartTime == nil || budget.StartTime.IsZero() {
 			budget.StartTime = &currentTime
 		}
 		// ignore budget with start time < currentTime
-		if budget.StartTime != nil && budget.StartTime.Before(currentTime) {
+		if budget.StartTime.Before(currentTime) {
 			continue
 		}
 
```

### x/protocolpool/keeper/keeper.go
```diff
@@ -111,6 +111,7 @@ func (k Keeper) withdrawContinuousFund(ctx context.Context, recipient sdk.AccAdd
 		if errors.Is(err, collections.ErrNotFound) {
 			return sdk.Coin{}, fmt.Errorf("no continuous fund found for recipient: %s", recipient.String())
 		}
+		return sdk.Coin{}, fmt.Errorf("get continuous fund failed for recipient: %s", recipient.String())
 	}
 	if cf.Expiry != nil && cf.Expiry.Before(sdkCtx.HeaderInfo().Time) {
 		return sdk.Coin{}, fmt.Errorf("cannot withdraw continuous funds: continuous fund expired for recipient: %s", recipient.String())
@@ -412,10 +413,8 @@ func (k Keeper) validateContinuousFund(ctx context.Context, msg types.MsgCreateC
 
 	// Validate expiry
 	currentTime := sdk.UnwrapSDKContext(ctx).BlockTime()
-	if msg.Expiry != nil {
-		if msg.Expiry.Compare(currentTime) == -1 {
-			return fmt.Errorf("expiry time cannot be less than the current block time")
-		}
+	if msg.Expiry != nil && msg.Expiry.Compare(currentTime) == -1 {
+		return fmt.Errorf("expiry time cannot be less than the current block time")
 	}
 
 	return nil
```

### x/protocolpool/keeper/msg_server.go
```diff
@@ -190,10 +190,8 @@ func (k MsgServer) CancelContinuousFund(ctx context.Context, msg *types.MsgCance
 
 	// withdraw funds if any are allocated
 	withdrawnFunds, err := k.withdrawRecipientFunds(ctx, recipient)
-	if err != nil {
-		if !errorspkg.Is(err, types.ErrNoRecipientFund) {
-			return nil, fmt.Errorf("error while withdrawing already allocated funds for recipient %s: %v", msg.RecipientAddress, err)
-		}
+	if err != nil && !errorspkg.Is(err, types.ErrNoRecipientFund) {
+		return nil, fmt.Errorf("error while withdrawing already allocated funds for recipient %s: %v", msg.RecipientAddress, err)
 	}
 
 	if err := k.ContinuousFund.Remove(ctx, recipient); err != nil {
```
