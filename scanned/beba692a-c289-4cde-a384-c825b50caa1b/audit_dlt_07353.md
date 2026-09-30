# [?] [FAB-14475] fix data race in gossip/channel

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2019-03-04
Source: https://github.com/hyperledger/fabric/commit/435d4c43d70f41b61c64ec3cc9f93f85dbbcf0e2
Type: security-commit

## Details
[FAB-14475] fix data race in gossip/channel

In gossip/channel.GenerateMAC()
create a new slice instead of maybe appending to existing slice

Change-Id: I2e88b87d88ddccf5e3c45471cc07656acd7e7af6
Signed-off-by: Hagar Meir <hagar.meir@ibm.com>

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
