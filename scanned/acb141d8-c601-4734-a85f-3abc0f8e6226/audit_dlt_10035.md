# [?] remove old todo + fix possible nil panic edge case

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2026-07-16
Source: https://github.com/multiversx/mx-chain-go/commit/11685187d6216f729d780315862bf28ecbc53afb
Type: security-commit

## Details
remove old todo + fix possible nil panic edge case

## Patch
### consensus/spos/consensusMessageValidator.go
```diff
@@ -449,7 +449,6 @@ func (cmv *consensusMessageValidator) checkMessageWithFinalInfoValidity(cnsMsg *
 			len(cnsMsg.AggregateSignature))
 	}
 
-	// TODO[cleanup cns finality]: remove this
 	if cmv.shouldNotVerifyLeaderSignature() {
 		return nil
 	}
@@ -464,12 +463,12 @@ func (cmv *consensusMessageValidator) checkMessageWithFinalInfoValidity(cnsMsg *
 }
 
 func (cmv *consensusMessageValidator) shouldNotVerifyLeaderSignature() bool {
-	// TODO: this check needs to be removed when equivalent messages are sent separately from the final info
-	if check.IfNil(cmv.consensusState.GetHeader()) {
+	header := cmv.consensusState.GetHeader()
+	if check.IfNil(header) {
 		return true
 	}
 
-	return cmv.enableEpochsHandler.IsFlagEnabledInEpoch(common.AndromedaFlag, cmv.consensusState.GetHeader().GetEpoch())
+	return cmv.enableEpochsHandler.IsFlagEnabledInEpoch(common.AndromedaFlag, header.GetEpoch())
 
 }
 
```
