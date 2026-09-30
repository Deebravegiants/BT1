# [?] FAB-15160 fix data race in Raft chain

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2019-04-12
Source: https://github.com/hyperledger/fabric/commit/fe7bd481e55bde110e5eda8c2e3c77d65e222fef
Type: security-commit

## Details
FAB-15160 fix data race in Raft chain

Update of RaftIndex in BlockMetadata should be guarded by write
lock as well, to avoid race with clone.

Change-Id: I7656e2129eee058179f694c055f98981e91b14c5
Signed-off-by: Jay Guo <guojiannan1101@gmail.com>

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
