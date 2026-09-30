# [?] Merge pull request from GHSA-qrhq-96mh-q8jv

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/ibc-go
Published: 2021-08-25
Source: https://github.com/cosmos/ibc-go/commit/ae36ab5ba5c66af253bcf8013a3c938d53db0d98
Type: security-commit

## Details
Merge pull request from GHSA-qrhq-96mh-q8jv

## Patch
### modules/apps/transfer/module.go
```diff
@@ -329,7 +329,7 @@ func (am AppModule) OnRecvPacket(
 
 	var data types.FungibleTokenPacketData
 	if err := types.ModuleCdc.UnmarshalJSON(packet.GetData(), &data); err != nil {
-		ack = channeltypes.NewErrorAcknowledgement(fmt.Sprintf("cannot unmarshal ICS-20 transfer packet data: %s", err.Error()))
+		ack = channeltypes.NewErrorAcknowledgement("cannot unmarshal ICS-20 transfer packet data")
 	}
 
 	// only attempt the application logic if the packet data
```
