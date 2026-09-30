# [?] Merge pull request from GHSA-j658-c98j-fww4

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/ibc-go
Published: 2022-03-15
Source: https://github.com/cosmos/ibc-go/commit/13bc4a06aff8f48e12dff2dba6f84206fa429c96
Type: security-commit

## Details
Merge pull request from GHSA-j658-c98j-fww4

Co-authored-by: Carlos Rodriguez <crodveg@gmail.com>

## Patch
### modules/apps/transfer/keeper/relay.go
```diff
@@ -239,6 +239,10 @@ func (k Keeper) OnRecvPacket(ctx sdk.Context, packet channeltypes.Packet, data t
 		}
 		token := sdk.NewCoin(denom, transferAmount)
 
+		if k.bankKeeper.BlockedAddr(receiver) {
+			return sdkerrors.Wrapf(sdkerrors.ErrUnauthorized, "%s is not allowed to receive funds", receiver)
+		}
+
 		// unescrow tokens
 		escrowAddress := types.GetEscrowAddress(packet.GetDestPort(), packet.GetDestChannel())
 		if err := k.bankKeeper.SendCoins(ctx, escrowAddress, receiver, sdk.NewCoins(token)); err != nil {
```

### modules/apps/transfer/keeper/relay_test.go
```diff
@@ -167,6 +167,16 @@ func (suite *KeeperTestSuite) TestOnRecvPacket() {
 		{"tries to unescrow more tokens than allowed", func() {
 			amount = sdk.NewInt(1000000)
 		}, true, false},
+
+		// - coin being sent to module address on chainA
+		{"failure: receive on module account", func() {
+			receiver = suite.chainA.GetSimApp().AccountKeeper.GetModuleAddress(types.ModuleName).String()
+		}, false, false},
+
+		// - coin being sent back to original chain (chainB) to module address
+		{"failure: receive on module account on source chain", func() {
+			receiver = suite.chainB.GetSimApp().AccountKeeper.GetModuleAddress(types.ModuleName).String()
+		}, true, false},
 	}
 
 	for _, tc := range testCases {
```

### modules/apps/transfer/types/expected_keepers.go
```diff
@@ -23,6 +23,7 @@ type BankKeeper interface {
 	BurnCoins(ctx sdk.Context, moduleName string, amt sdk.Coins) error
 	SendCoinsFromModuleToAccount(ctx sdk.Context, senderModule string, recipientAddr sdk.AccAddress, amt sdk.Coins) error
 	SendCoinsFromAccountToModule(ctx sdk.Context, senderAddr sdk.AccAddress, recipientModule string, amt sdk.Coins) error
+	BlockedAddr(addr sdk.AccAddress) bool
 }
 
 // ICS4Wrapper defines the expected ICS4Wrapper for middleware
```
