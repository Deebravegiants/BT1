# [?] fix: potential oobs panics

## Summary
Severity: Unknown
Chain: Quicksilver
Component: quicksilver-zone/quicksilver
Published: 2026-01-07
Source: https://github.com/quicksilver-zone/quicksilver/commit/b414734897a1db010d450fa73c859b3627d22ed6
Type: security-commit

## Details
fix: potential oobs panics

## Patch
### x/interchainstaking/keeper/msg_server.go
```diff
@@ -10,6 +10,7 @@ import (
 	"strings"
 	"time"
 
+	"cosmossdk.io/math"
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	govtypes "github.com/cosmos/cosmos-sdk/x/gov/types"
 	stakingtypes "github.com/cosmos/cosmos-sdk/x/staking/types"
@@ -622,41 +623,43 @@ func (k msgServer) GovCancelAllPendingRedemptions(goCtx context.Context, msg *ty
 		return false
 	})
 
-	// check if the amounts to refund are greater than the escrow balance
-	escrowBalance := k.BankKeeper.GetBalance(ctx, k.AccountKeeper.GetModuleAddress(types.EscrowModuleAccount), amountsToRefund[0].Denom)
-	if escrowBalance.IsLT(amountsToRefund[0]) {
-		return nil, fmt.Errorf("insufficient escrow balance to refund. Escrow balance: %s, amounts to refund: %s", escrowBalance.String(), amountsToRefund[0].String())
-	}
-
-	// Process each record
-	for _, record := range recordsToDelete {
-		userAccAddress, err := addressutils.AddressFromBech32(record.Delegator, "")
-		if err != nil {
-			k.Logger(ctx).Error("failed to parse delegator address", "address", record.Delegator, "error", err)
-			return nil, err
+	if len(amountsToRefund) > 0 {
+		// check if the amounts to refund are greater than the escrow balance
+		escrowBalance := k.BankKeeper.GetBalance(ctx, k.AccountKeeper.GetModuleAddress(types.EscrowModuleAccount), amountsToRefund[0].Denom)
+		if escrowBalance.IsLT(amountsToRefund[0]) {
+			return nil, fmt.Errorf("insufficient escrow balance to refund. Escrow balance: %s, amounts to refund: %s", escrowBalance.String(), amountsToRefund[0].String())
 		}
 
-		// Refund the qAssets from escrow to user
-		if err := k.BankKeeper.SendCoinsFromModuleToAccount(ctx, types.EscrowModuleAccount, userAccAddress, sdk.NewCoins(record.BurnAmount)); err != nil {
-			k.Logger(ctx).Error("failed to refund qAssets", "user", record.Delegator, "amount", record.BurnAmount, "error", err)
-			return nil, err
+		// Process each record
+		for _, record := range recordsToDelete {
+			userAccAddress, err := addressutils.AddressFromBech32(record.Delegator, "")
+			if err != nil {
+				k.Logger(ctx).Error("failed to parse delegator address", "address", record.Delegator, "error", err)
+				return nil, err
+			}
+
+			// Refund the qAssets from escrow to user
+			if err := k.BankKeeper.SendCoinsFromModuleToAccount(ctx, types.EscrowModuleAccount, userAccAddress, sdk.NewCoins(record.BurnAmount)); err != nil {
+				k.Logger(ctx).Error("failed to refund qAssets", "user", record.Delegator, "amount", record.BurnAmount, "error", err)
+				return nil, err
+			}
+
+			// Delete the withdrawal record
+			k.DeleteWithdrawalRecord(ctx, record.ChainId, record.Txhash, record.Status)
+
+			cancelledCount++
+			refundedAmounts = refundedAmounts.Add(record.BurnAmount)
+
+			ctx.EventManager().EmitEvent(
+				sdk.NewEvent(
+					types.EventTypeRedemptionCancellation,
+					sdk.NewAttribute(types.AttributeKeyReturnedAmount, record.BurnAmount.String()),
+					sdk.NewAttribute(types.AttributeKeyUser, record.Delegator),
+					sdk.NewAttribute(types.AttributeKeyHash, record.Txhash),
+					sdk.NewAttribute(types.AttributeKeyChainID, record.ChainId),
+				),
+			)
 		}
-
-		// Delete the withdrawal record
-		k.DeleteWithdrawalRecord(ctx, record.ChainId, record.Txhash, record.Status)
-
-		cancelledCount++
-		refundedAmounts = refundedAmounts.Add(record.BurnAmount)
-
-		ctx.EventManager().EmitEvent(
-			sdk.NewEvent(
-				types.EventTypeRedemptionCancellation,
-				sdk.NewAttribute(types.AttributeKeyReturnedAmount, record.BurnAmount.String()),
-				sdk.NewAttribute(types.AttributeKeyUser, record.Delegator),
-				sdk.NewAttribute(types.AttributeKeyHash, record.Txhash),
-				sdk.NewAttribute(types.AttributeKeyChainID, record.ChainId),
-			),
-		)
 	}
 
 	ctx.EventManager().EmitEvents(sdk.Events{
@@ -714,7 +717,7 @@ func (k msgServer) GovForceUnbondAllDelegations(goCtx context.Context, msg *type
 	}
 
 	var msgs []sdk.Msg
-	totalUnbonded := sdk.NewCoin(zone.BaseDenom, sdk.ZeroInt())
+	totalUnbonded := sdk.NewCoin(zone.BaseDenom, math.ZeroInt())
 	var unbondingCount uint64
 
 	// Create MsgUndelegate for each delegation
```
