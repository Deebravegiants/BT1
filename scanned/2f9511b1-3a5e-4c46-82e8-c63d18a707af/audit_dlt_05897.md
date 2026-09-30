# [?] Fix FAB-18528: remove panic in ifConfig func (#2828)

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2021-08-11
Source: https://github.com/hyperledger/fabric/commit/497a177ffb818ed8f75578cb55a65ba2224a85ea
Type: security-commit

## Details
Fix FAB-18528: remove panic in ifConfig func (#2828)

Fix issues: FAB-18528. When received the constructed message from the malicious node (through the interface "chain.rpc.SendSubmit(dest uint64, request *orderer.SubmitRequest, report func(err error))"), all orderers will breakdown immediately.

Signed-off-by: sardChen <sard.chen@gmail.com>

## Patch
### orderer/consensus/etcdraft/chain.go
```diff
@@ -891,7 +891,12 @@ func (c *Chain) writeBlock(block *common.Block, index uint64) {
 func (c *Chain) ordered(msg *orderer.SubmitRequest) (batches [][]*common.Envelope, pending bool, err error) {
 	seq := c.support.Sequence()
 
-	if c.isConfig(msg.Payload) {
+	isconfig, err := c.isConfig(msg.Payload)
+	if err != nil {
+		return nil, false, errors.Errorf("bad message: %s", err)
+	}
+
+	if isconfig {
 		// ConfigMsg
 		if msg.LastValidationSeq < seq {
 			c.logger.Warnf("Config message was validated against %d, although current config seq has advanced (%d)", msg.LastValidationSeq, seq)
@@ -1163,13 +1168,14 @@ func (c *Chain) gc() {
 	}
 }
 
-func (c *Chain) isConfig(env *common.Envelope) bool {
+func (c *Chain) isConfig(env *common.Envelope) (bool, error) {
 	h, err := protoutil.ChannelHeader(env)
 	if err != nil {
-		c.logger.Panicf("failed to extract channel header from envelope")
+		c.logger.Errorf("failed to extract channel header from envelope")
+		return false, err
 	}
 
-	return h.Type == int32(common.HeaderType_CONFIG) || h.Type == int32(common.HeaderType_ORDERER_TRANSACTION)
+	return h.Type == int32(common.HeaderType_CONFIG) || h.Type == int32(common.HeaderType_ORDERER_TRANSACTION), nil
 }
 
 func (c *Chain) configureComm() error {
```
