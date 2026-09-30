# [?] Add debug info for overrun issue & fix OOB bugs from the audit (#2076)

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2020-01-14
Source: https://github.com/harmony-one/harmony/commit/7c9142d35e86d608c909d7cdf06912115e2a1e92
Type: security-commit

## Details
Add debug info for overrun issue & fix OOB bugs from the audit (#2076)

* Add debug info for consensus main loop

* Fix potential OOB issue on p2p message parsing

* Add msg size check to prevent OOB in msg handler

* Add constant for p2p msg prefix

## Patch
### consensus/consensus_v2.go
```diff
@@ -1110,6 +1110,7 @@ func (consensus *Consensus) Start(blockChannel chan *types.Block, stopChan chan
 		for {
 			select {
 			case <-ticker.C:
+				consensus.getLogger().Debug().Msg("[ConsensusMainLoop] Ticker")
 				if toStart == false && isInitialLeader {
 					continue
 				}
@@ -1133,13 +1134,15 @@ func (consensus *Consensus) Start(blockChannel chan *types.Block, stopChan chan
 					}
 				}
 			case <-consensus.syncReadyChan:
+				consensus.getLogger().Debug().Msg("[ConsensusMainLoop] syncReadyChan")
 				consensus.SetBlockNum(consensus.ChainReader.CurrentHeader().Number().Uint64() + 1)
 				consensus.SetViewID(consensus.ChainReader.CurrentHeader().ViewID().Uint64() + 1)
 				mode := consensus.UpdateConsensusInformation()
 				consensus.current.SetMode(mode)
 				consensus.getLogger().Info().Str("Mode", mode.String()).Msg("Node is in sync")
 
 			case <-consensus.syncNotReadyChan:
+				consensus.getLogger().Debug().Msg("[ConsensusMainLoop] syncNotReadyChan")
 				consensus.SetBlockNum(consensus.ChainReader.CurrentHeader().Number().Uint64() + 1)
 				consensus.current.SetMode(Syncing)
 				consensus.getLogger().Info().Msg("Node is out of sync")
@@ -1241,9 +1244,11 @@ func (consensus *Consensus) Start(blockChannel chan *types.Block, stopChan chan
 				consensus.announce(newBlock)
 
 			case msg := <-consensus.MsgChan:
+				consensus.getLogger().Debug().Msg("[ConsensusMainLoop] MsgChan")
 				consensus.handleMessageUpdate(msg)
 
 			case viewID := <-consensus.commitFinishChan:
+				consensus.getLogger().Debug().Msg("[ConsensusMainLoop] commitFinishChan")
 				// Only Leader execute this condition
 				func() {
 					consensus.mutex.Lock()
@@ -1254,9 +1259,11 @@ func (consensus *Consensus) Start(blockChannel chan *types.Block, stopChan chan
 				}()
 
 			case <-stopChan:
+				consensus.getLogger().Debug().Msg("[ConsensusMainLoop] stopChan")
 				return
 			}
 		}
+		consensus.getLogger().Debug().Msg("[ConsensusMainLoop] Ended.")
 	}()
 }
 
```

### node/node_handler.go
```diff
@@ -25,6 +25,8 @@ import (
 	libp2p_peer "github.com/libp2p/go-libp2p-core/peer"
 )
 
+const p2pMsgPrefixSize = 5
+
 // receiveGroupMessage use libp2p pubsub mechanism to receive broadcast messages
 func (node *Node) receiveGroupMessage(
 	receiver p2p.GroupReceiver, rxQueue msgq.MessageAdder,
@@ -43,7 +45,12 @@ func (node *Node) receiveGroupMessage(
 		}
 		//utils.Logger().Info("[PUBSUB]", "received group msg", len(msg), "sender", sender)
 		// skip the first 5 bytes, 1 byte is p2p type, 4 bytes are message size
-		if err := rxQueue.AddMessage(msg[5:], sender); err != nil {
+		if len(msg) < p2pMsgPrefixSize {
+			utils.Logger().Warn().Err(err).Int("msg size", len(msg)).
+				Msg("invalid p2p message size")
+			continue
+		}
+		if err := rxQueue.AddMessage(msg[p2pMsgPrefixSize:], sender); err != nil {
 			utils.Logger().Warn().Err(err).
 				Str("sender", sender.Pretty()).
 				Msg("cannot enqueue incoming message for processing")
@@ -105,6 +112,10 @@ func (node *Node) HandleMessage(content []byte, sender libp2p_peer.ID) {
 			node.stakingMessageHandler(msgPayload)
 		case proto_node.Block:
 			utils.Logger().Debug().Msg("NET: received message: Node/Block")
+			if len(msgPayload) < 1 {
+				utils.Logger().Debug().Msgf("Invalid block message size")
+				return
+			}
 			blockMsgType := proto_node.BlockMessageType(msgPayload[0])
 			switch blockMsgType {
 			case proto_node.Sync:
@@ -156,6 +167,10 @@ func (node *Node) HandleMessage(content []byte, sender libp2p_peer.ID) {
 }
 
 func (node *Node) transactionMessageHandler(msgPayload []byte) {
+	if len(msgPayload) < 1 {
+		utils.Logger().Debug().Msgf("Invalid transaction message size")
+		return
+	}
 	txMessageType := proto_node.TransactionMessageType(msgPayload[0])
 
 	switch txMessageType {
@@ -173,6 +188,10 @@ func (node *Node) transactionMessageHandler(msgPayload []byte) {
 }
 
 func (node *Node) stakingMessageHandler(msgPayload []byte) {
+	if len(msgPayload) < 1 {
+		utils.Logger().Debug().Msgf("Invalid staking transaction message size")
+		return
+	}
 	txMessageType := proto_node.TransactionMessageType(msgPayload[0])
 
 	switch txMessageType {
```
