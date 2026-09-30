# [?] Fix race condition by capturing version in goroutine (#855)

## Summary
Severity: Unknown
Chain: MEV
Component: flashbots/mev-boost
Published: 2025-11-09
Source: https://github.com/flashbots/mev-boost/commit/93d68d4169af6c741171cccd7d7544a41c8093ad
Type: security-commit

## Details
Fix race condition by capturing version in goroutine (#855)

* Fix race condition by capturing version in goroutine

When multiple relays are configured and some don't support getPayloadV2, a race condition occurs where one goroutine modifies the shared versionToUse variable, affecting response parsing in other concurrent goroutines.

This causes valid V2 responses to be incorrectly parsed as V1, leading to decoding errors and potential missed slots.

Fixed by capturing versionToUse in each goroutine's scope, ensuring each relay request maintains its own independent version state throughout the request-response lifecycle.

* Fix goroutine closure to avoid race condition

* Rename global parameter versionToUse to version

## Patch
### server/get_payload.go
```diff
@@ -71,7 +71,7 @@ func (m *BoostService) getPayloadV2(log *logrus.Entry, signedBlindedBeaconBlockB
 	return result, bid
 }
 
-func (m *BoostService) innerGetPayload(log *logrus.Entry, signedBlindedBeaconBlockBytes []byte, userAgent, proposerContentType, proposerAcceptContentTypes, proposerEthConsensusVersion string, versionToUse GetPayloadVersion) (payloadResult, bidResp) {
+func (m *BoostService) innerGetPayload(log *logrus.Entry, signedBlindedBeaconBlockBytes []byte, userAgent, proposerContentType, proposerAcceptContentTypes, proposerEthConsensusVersion string, version GetPayloadVersion) (payloadResult, bidResp) {
 	// Get the request's content type
 	parsedProposerContentType, _, err := mime.ParseMediaType(proposerContentType)
 	if err != nil {
@@ -156,7 +156,7 @@ func (m *BoostService) innerGetPayload(log *logrus.Entry, signedBlindedBeaconBlo
 	defer requestCtxCancel()
 
 	for _, relay := range m.relays {
-		go func(relay types.RelayEntry) {
+		go func(relay types.RelayEntry, versionToUse GetPayloadVersion) {
 			var url string
 			if versionToUse == GetPayloadV1 {
 				url = relay.GetURI(params.PathGetPayload)
@@ -311,7 +311,7 @@ func (m *BoostService) innerGetPayload(log *logrus.Entry, signedBlindedBeaconBlo
 			} else {
 				log.Trace("discarding response, already received a correct response")
 			}
-		}(relay)
+		}(relay, version)
 	}
 
 	// Wait for the first request to complete
```
