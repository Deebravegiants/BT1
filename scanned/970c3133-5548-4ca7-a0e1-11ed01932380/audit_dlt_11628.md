# [?] fix nil reference panic in abci.go; fixes #1744

## Summary
Severity: Unknown
Chain: Quicksilver
Component: quicksilver-zone/quicksilver
Published: 2024-11-17
Source: https://github.com/quicksilver-zone/quicksilver/commit/cea5738570390cae5edb73edaeae724cf8ef4a97
Type: security-commit

## Details
fix nil reference panic in abci.go; fixes #1744

## Patch
### x/interchainstaking/keeper/abci.go
```diff
@@ -52,22 +52,24 @@ func (k *Keeper) BeginBlocker(ctx sdk.Context) {
 				k.Logger(ctx).Error("error in GCCompletedUnbondings", "error", err.Error())
 			}
 
-			addressBytes, err := addressutils.AccAddressFromBech32(zone.DelegationAddress.Address, zone.AccountPrefix)
-			if err != nil {
-				k.Logger(ctx).Error("cannot decode bech32 delegation addr", "error", err.Error())
+			if zone.DelegationAddress != nil {
+				addressBytes, err := addressutils.AccAddressFromBech32(zone.DelegationAddress.Address, zone.AccountPrefix)
+				if err != nil {
+					k.Logger(ctx).Error("cannot decode bech32 delegation addr", "error", err.Error())
+				}
+				zone.DelegationAddress.IncrementBalanceWaitgroup()
+				k.ICQKeeper.MakeRequest(
+					ctx,
+					zone.ConnectionId,
+					zone.ChainId,
+					types.BankStoreKey,
+					append(banktypes.CreateAccountBalancesPrefix(addressBytes), []byte(zone.BaseDenom)...),
+					sdk.NewInt(-1),
+					types.ModuleName,
+					"accountbalance",
+					0,
+				)
 			}
-			zone.DelegationAddress.IncrementBalanceWaitgroup()
-			k.ICQKeeper.MakeRequest(
-				ctx,
-				zone.ConnectionId,
-				zone.ChainId,
-				types.BankStoreKey,
-				append(banktypes.CreateAccountBalancesPrefix(addressBytes), []byte(zone.BaseDenom)...),
-				sdk.NewInt(-1),
-				types.ModuleName,
-				"accountbalance",
-				0,
-			)
 		}
 
 		connection, found := k.IBCKeeper.ConnectionKeeper.GetConnection(ctx, zone.ConnectionId)
```
