# [?] fix crash on parsed block (#2993)

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2020-05-12
Source: https://github.com/harmony-one/harmony/commit/1dad4352918f3c3070a9d6c0a9aaf1a7333cecb6
Type: security-commit

## Details
fix crash on parsed block (#2993)

## Patch
### consensus/view_change.go
```diff
@@ -228,6 +228,7 @@ func (consensus *Consensus) onViewChange(msg *msg_pb.Message) {
 	}
 
 	preparedBlock := &types.Block{}
+	hasBlock := false
 	if len(recvMsg.Payload) != 0 && len(recvMsg.Block) != 0 {
 		if err := rlp.DecodeBytes(recvMsg.Block, preparedBlock); err != nil {
 			consensus.getLogger().Warn().
@@ -236,10 +237,11 @@ func (consensus *Consensus) onViewChange(msg *msg_pb.Message) {
 				Msg("[onViewChange] Unparseable prepared block data")
 			return
 		}
+		hasBlock = true
 	}
 
 	// m2 type message
-	if preparedBlock == nil {
+	if !hasBlock {
 		_, ok := consensus.nilSigs[recvMsg.ViewID][senderKey.SerializeToHexStr()]
 		if ok {
 			consensus.getLogger().Debug().
@@ -507,6 +509,7 @@ func (consensus *Consensus) onNewView(msg *msg_pb.Message) {
 
 	// check when M3 sigs > M2 sigs, then M1 (recvMsg.Payload) should not be empty
 	preparedBlock := &types.Block{}
+	hasBlock := false
 	if len(recvMsg.Payload) != 0 && len(recvMsg.Block) != 0 {
 		if err := rlp.DecodeBytes(recvMsg.Block, preparedBlock); err != nil {
 			consensus.getLogger().Warn().
@@ -526,6 +529,7 @@ func (consensus *Consensus) onNewView(msg *msg_pb.Message) {
 				Msg("[onNewView] Prepared block hash doesn't match msg block hash.")
 			return
 		}
+		hasBlock = true
 	}
 
 	if m2Mask == nil || m2Mask.Bitmap == nil ||
@@ -565,7 +569,9 @@ func (consensus *Consensus) onNewView(msg *msg_pb.Message) {
 		preparedMsg.SenderPubkey = senderKey
 		consensus.FBFTLog.AddMessage(&preparedMsg)
 
-		consensus.FBFTLog.AddBlock(preparedBlock)
+		if hasBlock {
+			consensus.FBFTLog.AddBlock(preparedBlock)
+		}
 	}
 
 	// newView message verified success, override my state
@@ -584,7 +590,7 @@ func (consensus *Consensus) onNewView(msg *msg_pb.Message) {
 	}
 
 	// NewView message is verified, change state to normal consensus
-	if preparedBlock != nil {
+	if hasBlock {
 		// Construct and send the commit message
 		if consensus.BlockVerifier(preparedBlock); err != nil {
 			consensus.getLogger().Error().Err(err).Msg("[onNewView] Prepared block verification failed")
```

### core/types/block.go
```diff
@@ -384,6 +384,9 @@ func NewBlockWithHeader(header *block.Header) *Block {
 // CopyHeader creates a deep copy of a block header to prevent side effects from
 // modifying a header variable.
 func CopyHeader(h *block.Header) *block.Header {
+	if h == nil {
+		return nil
+	}
 	cpy := *h
 	cpy.Header = cpy.Header.Copy()
 	return &cpy
```
