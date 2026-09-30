# [?] Merge pull request #192 from hyunsooda/valset-crash-prevented

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2024-12-31
Source: https://github.com/kaiachain/kaia/commit/767292802e1b8cbf5135bf2b64d1a02501c7c710
Type: security-commit

## Details
Merge pull request #192 from hyunsooda/valset-crash-prevented

consensus: Added error check to valset

## Patch
### consensus/istanbul/backend/engine.go
```diff
@@ -329,6 +329,9 @@ func (sb *backend) verifySigner(chain consensus.ChainReader, header *types.Heade
 
 	// Retrieve the snapshot needed to verify this header and cache it
 	valSet, err := sb.GetValidatorSet(number)
+	if err != nil {
+		return err
+	}
 
 	// resolve the authorization key and check against signers
 	signer, err := ecrecover(header)
```
