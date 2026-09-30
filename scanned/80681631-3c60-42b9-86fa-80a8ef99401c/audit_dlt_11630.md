# [?] tolerate stale acks without panicking; fixes #1271 (#1272)

## Summary
Severity: Unknown
Chain: Quicksilver
Component: quicksilver-zone/quicksilver
Published: 2024-03-14
Source: https://github.com/quicksilver-zone/quicksilver/commit/a5c19da410a6b5d9426b9c84e4c7f6b7725321e8
Type: security-commit

## Details
tolerate stale acks without panicking; fixes #1271 (#1272)

## Patch
### x/interchainstaking/keeper/ibc_packet_handlers.go
```diff
@@ -938,7 +938,12 @@ func (k *Keeper) HandleRedeemTokens(ctx sdk.Context, msg sdk.Msg, amount sdk.Coi
 		}
 		k.Logger(ctx).Debug("outstanding delegations ack-received")
 		k.SetReceiptsCompleted(ctx, zone.ChainId, time.Unix(exclusionTimestampUnix, 0), ctx.BlockTime(), redeemMsg.Amount.Denom)
-		zone.DelegationAddress.Balance = zone.DelegationAddress.Balance.Sub(redeemMsg.Amount)
+		balance, negative := zone.DelegationAddress.Balance.SafeSub(redeemMsg.Amount)
+		if negative {
+			k.Logger(ctx).Error("unexpected negative balance; likely due to stale ack")
+			return nil
+		}
+		zone.DelegationAddress.Balance = balance
 		k.SetZone(ctx, zone)
 		if zone.GetWithdrawalWaitgroup() == 0 {
 			k.Logger(ctx).Info("Triggering redemption rate calc after delegation flush")
@@ -1025,7 +1030,12 @@ func (k *Keeper) HandleDelegate(ctx sdk.Context, msg sdk.Msg, memo string) error
 		}
 		k.Logger(ctx).Debug("outstanding delegations ack-received")
 		k.SetReceiptsCompleted(ctx, zone.ChainId, time.Unix(exclusionTimestampUnix, 0), ctx.BlockTime(), delegateMsg.Amount.Denom)
-		zone.DelegationAddress.Balance = zone.DelegationAddress.Balance.Sub(delegateMsg.Amount)
+		balance, negative := zone.DelegationAddress.Balance.SafeSub(delegateMsg.Amount)
+		if negative {
+			k.Logger(ctx).Error("unexpected negative balance; likely a stale ack")
+			return nil
+		}
+		zone.DelegationAddress.Balance = balance
 		if err := zone.DecrementWithdrawalWaitgroup(k.Logger(ctx), uint32(1), "batch/reward delegation success ack"); err != nil {
 			k.Logger(ctx).Error(err.Error())
 			return nil
```
