# [?] Fix marker withdraw endpoint to not panic on empty to address. (#2849)

## Summary
Severity: Unknown
Chain: Provenance
Component: provenance-io/provenance
Published: 2026-09-22
Source: https://github.com/provenance-io/provenance/commit/f1250c5cd9b5ab8a11e3b91732ea5c9e3499c94d
Type: security-commit

## Details
Fix marker withdraw endpoint to not panic on empty to address. (#2849)

* Fix withdraw to not panic if there's no to address.

* Add changelog entry.

* Add unit test about not having a to-address.

## Patch
### .changelog/unreleased/bug-fixes/2849-fix-withdraw-panic.md
```diff
@@ -0,0 +1 @@
+* Fix marker withdraw to not panic if there's no to address [PR 2849](https://github.com/provenance-io/provenance/pull/2849).
```

### x/marker/keeper/marker.go
```diff
@@ -172,7 +172,7 @@ func (k Keeper) RemoveAccess(ctx sdk.Context, caller sdk.AccAddress, denom strin
 }
 
 // WithdrawCoins removes the specified coins from the MarkerAccount (both marker denominated coins and coins as assets
-// are supported here)
+// are supported here). If recipient is empty, the coins are moved to the caller's account.
 func (k Keeper) WithdrawCoins(
 	ctx sdk.Context, caller sdk.AccAddress, recipient sdk.AccAddress, denom string, coins sdk.Coins,
 ) error {
```

### x/marker/keeper/msg_server.go
```diff
@@ -353,7 +353,10 @@ func (k msgServer) Withdraw(goCtx context.Context, msg *types.MsgWithdrawRequest
 	}
 
 	admin := sdk.MustAccAddressFromBech32(msg.Administrator)
-	to := sdk.MustAccAddressFromBech32(msg.ToAddress)
+	to := admin
+	if len(msg.ToAddress) > 0 {
+		to = sdk.MustAccAddressFromBech32(msg.ToAddress)
+	}
 
 	if err := k.WithdrawCoins(ctx, admin, to, msg.Denom, msg.Amount); err != nil {
 		ctx.Logger().Error("unable to withdraw coins from marker", "err", err)
```

### x/marker/keeper/msg_server_test.go
```diff
@@ -1206,8 +1206,6 @@ func (s *MsgServerTestSuite) TestMsgWithdrawMarkerRequest() {
 		name          string
 		msg           *types.MsgWithdrawRequest
 		expectedEvent proto.Message
-		expErr        bool
-		expErrMsg     string
 	}{
 		{
 			name:          "should successfully withdraw marker",
@@ -1231,12 +1229,26 @@ func (s *MsgServerTestSuite) TestMsgWithdrawMarkerRequest() {
 			}(),
 			expectedEvent: types.NewEventMarkerWithdraw("100hotdog", hotdogDenom, s.owner1, s.owner1),
 		},
+		{
+			name: "no to-address in msg",
+			msg: &types.MsgWithdrawRequest{
+				Denom:         hotdogDenom,
+				Administrator: s.owner1Addr.String(),
+				ToAddress:     "",
+				Amount:        sdk.NewCoins(sdk.NewInt64Coin(hotdogDenom, 103)),
+			},
+			expectedEvent: types.NewEventMarkerWithdraw("103hotdog", hotdogDenom, s.owner1, s.owner1),
+		},
 	}
 
 	for _, tc := range testcases {
 		s.Run(tc.name, func() {
 			s.ctx = s.ctx.WithEventManager(sdk.NewEventManager())
-			response, err := s.msgServer.Withdraw(s.ctx, tc.msg)
+			var response *types.MsgWithdrawResponse
+			testFunc := func() {
+				response, err = s.msgServer.Withdraw(s.ctx, tc.msg)
+			}
+			s.Require().NotPanics(testFunc, "msgServer.Withdraw")
 			s.Require().NoError(err, "handler(%T) error", tc.msg)
 			if tc.expectedEvent != nil {
 				result := s.containsMessage(s.ctx.EventManager().ABCIEvents(), tc.expectedEvent)
```
