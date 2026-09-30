# [?] Merge "FAB-15160 fix data race in Raft chain"

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2019-04-12
Source: https://github.com/hyperledger/fabric/commit/734e35582b68b796cf55c91da13d16f3acae62d4
Type: security-commit

## Details
Merge "FAB-15160 fix data race in Raft chain"

## Patch
### orderer/consensus/etcdraft/chain.go
```diff
@@ -1191,8 +1191,8 @@ func (c *Chain) writeConfigBlock(block *common.Block, index uint64) {
 	case common.HeaderType_CONFIG:
 		configMembership := c.detectConfChange(block)
 
-		c.opts.BlockMetadata.RaftIndex = index
 		c.raftMetadataLock.Lock()
+		c.opts.BlockMetadata.RaftIndex = index
 		if configMembership != nil {
 			c.opts.BlockMetadata = configMembership.NewBlockMetadata
 			c.opts.Consenters = configMembership.NewConsenters
```
