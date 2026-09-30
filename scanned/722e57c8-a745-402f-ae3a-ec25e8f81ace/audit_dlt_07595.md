# [?] eth/catalyst: fix panic in TestWithdrawals (#26563)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2023-01-27
Source: https://github.com/ethereum/go-ethereum/commit/df52967ff6080a27243569020ff64cd956fb8362
Type: security-commit

## Details
eth/catalyst: fix panic in TestWithdrawals (#26563)

Fixes a regression introduced in #26549

## Patch
### eth/catalyst/api.go
```diff
@@ -175,19 +175,27 @@ func (api *ConsensusAPI) ForkchoiceUpdatedV1(update beacon.ForkchoiceStateV1, pa
 
 // ForkchoiceUpdatedV2 is equivalent to V1 with the addition of withdrawals in the payload attributes.
 func (api *ConsensusAPI) ForkchoiceUpdatedV2(update beacon.ForkchoiceStateV1, payloadAttributes *beacon.PayloadAttributes) (beacon.ForkChoiceResponse, error) {
-	if !api.eth.BlockChain().Config().IsShanghai(payloadAttributes.Timestamp) {
+	if payloadAttributes != nil {
+		if err := api.verifyPayloadAttributes(payloadAttributes); err != nil {
+			return beacon.STATUS_INVALID, beacon.InvalidPayloadAttributes.With(err)
+		}
+	}
+	return api.forkchoiceUpdated(update, payloadAttributes)
+}
+
+func (api *ConsensusAPI) verifyPayloadAttributes(attr *beacon.PayloadAttributes) error {
+	if !api.eth.BlockChain().Config().IsShanghai(attr.Timestamp) {
 		// Reject payload attributes with withdrawals before shanghai
-		if payloadAttributes != nil && payloadAttributes.Withdrawals != nil {
-			return beacon.STATUS_INVALID, beacon.InvalidPayloadAttributes.With(errors.New("withdrawals before shanghai"))
+		if attr.Withdrawals != nil {
+			return errors.New("withdrawals before shanghai")
 		}
 	} else {
 		// Reject payload attributes with nil withdrawals after shanghai
-		if payloadAttributes != nil && payloadAttributes.Withdrawals == nil {
-			return beacon.STATUS_INVALID, beacon.InvalidPayloadAttributes.With(errors.New("missing withdrawals list"))
+		if attr.Withdrawals == nil {
+			return errors.New("missing withdrawals list")
 		}
 	}
-
-	return api.forkchoiceUpdated(update, payloadAttributes)
+	return nil
 }
 
 func (api *ConsensusAPI) forkchoiceUpdated(update beacon.ForkchoiceStateV1, payloadAttributes *beacon.PayloadAttributes) (beacon.ForkChoiceResponse, error) {
```
