# [?] Merge "[FAB-14475] fix data race in gossip/channel"

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2019-03-05
Source: https://github.com/hyperledger/fabric/commit/ccd89a0626bc9fe88cbba42e2499a3b87f62adeb
Type: security-commit

## Details
Merge "[FAB-14475] fix data race in gossip/channel"

## Patch
### gossip/gossip/channel/channel.go
```diff
@@ -990,7 +990,9 @@ func (cache *stateInfoCache) Stop() {
 // and a channel name
 func GenerateMAC(pkiID common.PKIidType, channelID common.ChainID) []byte {
 	// Hash is computed on (PKI-ID || channel ID)
-	preImage := append([]byte(pkiID), []byte(channelID)...)
+	var preImage []byte
+	preImage = append(preImage, []byte(pkiID)...)
+	preImage = append(preImage, []byte(channelID)...)
 	return common_utils.ComputeSHA256(preImage)
 }
 
```
