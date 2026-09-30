# [?] fix(axelarnet): potential underflow (#1155)

## Summary
Severity: Unknown
Chain: Axelar
Component: axelarnetwork/axelar-core
Published: 2021-12-29
Source: https://github.com/axelarnetwork/axelar-core/commit/fcf8150addf61cb34edac669f86b1cc31bc82a04
Type: security-commit

## Details
fix(axelarnet): potential underflow (#1155)

## Patch
### x/axelarnet/keeper/msg_server.go
```diff
@@ -338,8 +338,14 @@ func IBCTransfer(ctx sdk.Context, k types.BaseKeeper, t types.IBCTransferKeeper,
 	height := clienttypes.NewHeight(state.GetLatestHeight().GetRevisionNumber(), state.GetLatestHeight().GetRevisionHeight()+k.GetRouteTimeoutWindow(ctx))
 	err = t.SendTransfer(ctx, portID, channelID, token, sender, receiver, height, 0)
 	if err == nil {
-		// SendTransfer would return error if the next sequence not found
-		seq, _ := c.GetNextSequenceSend(ctx, portID, channelID)
+		seq, ok := c.GetNextSequenceSend(ctx, portID, channelID)
+		if !ok {
+			return fmt.Errorf("no next sequence number found for channel ID '%s' at port ID '%s'", channelID, portID)
+		}
+		if seq == 0 {
+			return fmt.Errorf("next sequence number for channel ID '%s' at port ID '%s' is zero", channelID, portID)
+		}
+
 		k.SetPendingIBCTransfer(ctx, types.IBCTransfer{
 			Sender:    sender,
 			Receiver:  receiver,
```
