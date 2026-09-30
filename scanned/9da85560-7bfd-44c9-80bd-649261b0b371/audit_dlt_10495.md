# [?] Merge pull request from GHSA-qrhq-96mh-q8jv

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2021-08-25
Source: https://github.com/sei-protocol/sei-chain/commit/c49ba3925aaa5da52c6909b67ee360191d0107d2
Type: security-commit

## Details
Merge pull request from GHSA-qrhq-96mh-q8jv

## Patch
### sei-ibc-go/modules/apps/transfer/module.go
```diff
@@ -329,7 +329,7 @@ func (am AppModule) OnRecvPacket(
 
 	var data types.FungibleTokenPacketData
 	if err := types.ModuleCdc.UnmarshalJSON(packet.GetData(), &data); err != nil {
-		ack = channeltypes.NewErrorAcknowledgement(fmt.Sprintf("cannot unmarshal ICS-20 transfer packet data: %s", err.Error()))
+		ack = channeltypes.NewErrorAcknowledgement("cannot unmarshal ICS-20 transfer packet data")
 	}
 
 	// only attempt the application logic if the packet data
```
