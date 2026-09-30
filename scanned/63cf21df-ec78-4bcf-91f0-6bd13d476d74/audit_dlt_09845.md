# [?] fix potential security issue in onCommit for leader

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2019-06-08
Source: https://github.com/harmony-one/harmony/commit/072e9261216c0b295c0f8b9ed024c80b9d952117
Type: security-commit

## Details
fix potential security issue in onCommit for leader

## Patch
### consensus/consensus_v2.go
```diff
@@ -292,16 +292,25 @@ func (consensus *Consensus) onPrepare(msg *msg_pb.Message) {
 
 	if len(prepareSigs) >= consensus.Quorum() {
 		consensus.switchPhase(Commit, false)
-
 		// Construct and broadcast prepared message
 		msgToSend, aggSig := consensus.constructPreparedMessage()
 		consensus.aggregatedPrepareSig = aggSig
 
+		// add prepared message to log
+		msgPayload, _ := proto.GetConsensusMessagePayload(msgToSend)
+		msg := &msg_pb.Message{}
+		_ = protobuf.Unmarshal(msgPayload, msg)
+		pbftMsg, err := ParsePbftMessage(msg)
+		if err != nil {
+			utils.GetLogger().Warn("onPrepare unable to parse pbft message", "error", err)
+			return
+		}
+		consensus.pbftLog.AddMessage(pbftMsg)
+
 		utils.GetLogger().Warn("sent prepared message", "viewID", consensus.viewID, "block", consensus.blockNum)
 		consensus.host.SendMessageToGroups([]p2p.GroupID{p2p.NewGroupIDByShardID(p2p.ShardID(consensus.ShardID))}, host.ConstructP2pMessage(byte(17), msgToSend))
 
 		// Leader add commit phase signature
-
 		blockNumHash := make([]byte, 8)
 		binary.LittleEndian.PutUint64(blockNumHash, consensus.blockNum)
 		commitPayload := append(blockNumHash, consensus.blockHash[:]...)
@@ -441,6 +450,11 @@ func (consensus *Consensus) onCommit(msg *msg_pb.Message) {
 		return
 	}
 
+	if !consensus.pbftLog.HasMatchingViewPrepared(consensus.blockNum, consensus.viewID, recvMsg.BlockHash) {
+		utils.GetLogger().Debug("cannot find matching prepared message")
+		return
+	}
+
 	validatorPubKey := recvMsg.SenderPubkey
 	addrBytes := validatorPubKey.GetAddress()
 	validatorAddress := common.BytesToAddress(addrBytes[:])
```

### consensus/pbft_log.go
```diff
@@ -152,7 +152,7 @@ func (log *PbftLog) GetMessagesByTypeSeqHash(typ msg_pb.MessageType, blockNum ui
 	return found
 }
 
-// HasMatchingAnnounce returns whether the log contains announce type message with given blockNum, viewID and blockHash
+// HasMatchingAnnounce returns whether the log contains announce type message with given blockNum, blockHash
 func (log *PbftLog) HasMatchingAnnounce(blockNum uint64, blockHash common.Hash) bool {
 	found := log.GetMessagesByTypeSeqHash(msg_pb.MessageType_ANNOUNCE, blockNum, blockHash)
 	return len(found) == 1
@@ -164,6 +164,12 @@ func (log *PbftLog) HasMatchingViewAnnounce(blockNum uint64, viewID uint32, bloc
 	return len(found) == 1
 }
 
+// HasMatchingViewPrepared returns whether the log contains prepared message with given blockNum, viewID and blockHash
+func (log *PbftLog) HasMatchingViewPrepared(blockNum uint64, viewID uint32, blockHash common.Hash) bool {
+	found := log.GetMessagesByTypeSeqViewHash(msg_pb.MessageType_PREPARED, blockNum, viewID, blockHash)
+	return len(found) == 1
+}
+
 // GetMessagesByTypeSeqView returns pbft messages with matching type, blockNum and viewID
 func (log *PbftLog) GetMessagesByTypeSeqView(typ msg_pb.MessageType, blockNum uint64, viewID uint32) []*PbftMessage {
 	found := []*PbftMessage{}
```
