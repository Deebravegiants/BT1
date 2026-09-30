# [?] Fix data race in TestHaltChainProcessing

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2020-03-12
Source: https://github.com/hyperledger/fabric/commit/81b61607d4b22c037686a638e187c1d8a4acd739
Type: security-commit

## Details
Fix data race in TestHaltChainProcessing

Change-Id: I838ca892c0c29d17d4bf6b886ab9a86e73b6bf1e
Signed-off-by: yacovm <yacovm@il.ibm.com>

## Patch
### gossip/service/gossip_service.go
```diff
@@ -11,6 +11,7 @@ import (
 
 	gproto "github.com/hyperledger/fabric-protos-go/gossip"
 	tspb "github.com/hyperledger/fabric-protos-go/transientstore"
+	"github.com/hyperledger/fabric/common/flogging"
 	corecomm "github.com/hyperledger/fabric/core/comm"
 	"github.com/hyperledger/fabric/core/committer"
 	"github.com/hyperledger/fabric/core/committer/txvalidator"
@@ -344,6 +345,7 @@ func (g *GossipService) InitializeChannel(channelID string, ordererSource *order
 	blockingMode := !g.serviceConfig.NonBlockingCommitMode
 	stateConfig := state.GlobalConfig()
 	g.chains[channelID] = state.NewGossipStateProvider(
+		flogging.MustGetLogger(util.StateLogger),
 		channelID,
 		servicesAdapter,
 		coordinator,
```

### gossip/state/payloads_buffer.go
```diff
@@ -81,7 +81,7 @@ func (b *PayloadsBufferImpl) Push(payload *proto.Payload) {
 	seqNum := payload.SeqNum
 
 	if seqNum < b.next || b.buf[seqNum] != nil {
-		logger.Debugf("Payload with sequence number = %d has been already processed", payload.SeqNum)
+		b.logger.Debugf("Payload with sequence number = %d has been already processed", payload.SeqNum)
 		return
 	}
 
```

### gossip/state/state.go
```diff
@@ -136,6 +136,8 @@ type ServicesMediator struct {
 // the struct to handle in memory sliding window of
 // new ledger block to be acquired by hyper ledger
 type GossipStateProviderImpl struct {
+	logger util.Logger
+
 	// Chain id
 	chainID string
 
@@ -165,8 +167,6 @@ type GossipStateProviderImpl struct {
 	config *StateConfig
 }
 
-var logger = util.GetLogger(util.StateLogger, "")
-
 // stateRequestValidator facilitates validation of the state request messages
 type stateRequestValidator struct {
 }
@@ -187,14 +187,14 @@ func (v *stateRequestValidator) validate(request *proto.RemoteStateRequest, batc
 // NewGossipStateProvider creates state provider with coordinator instance
 // to orchestrate arrival of private rwsets and blocks before committing them into the ledger.
 func NewGossipStateProvider(
+	logger util.Logger,
 	chainID string,
 	services *ServicesMediator,
 	ledger ledgerResources,
 	stateMetrics *metrics.StateMetrics,
 	blockingMode bool,
 	config *StateConfig,
 ) GossipStateProvider {
-
 	gossipChan, _ := services.Accept(func(message interface{}) bool {
 		// Get only data messages
 		return protoext.IsDataMsg(message.(*proto.GossipMessage)) &&
@@ -238,6 +238,7 @@ func NewGossipStateProvider(
 	}
 
 	s := &GossipStateProviderImpl{
+		logger: logger,
 		// MessageCryptoService
 		mediator: services,
 		// Chain ID
@@ -282,40 +283,40 @@ func NewGossipStateProvider(
 
 func (s *GossipStateProviderImpl) receiveAndQueueGossipMessages(ch <-chan *proto.GossipMessage) {
 	for msg := range ch {
-		logger.Debug("Received new message via gossip channel")
+		s.logger.Debug("Received new message via gossip channel")
 		go func(msg *proto.GossipMessage) {
 			if !bytes.Equal(msg.Channel, []byte(s.chainID)) {
-				logger.Warning("Received enqueue for channel",
+				s.logger.Warning("Received enqueue for channel",
 					string(msg.Channel), "while expecting channel", s.chainID, "ignoring enqueue")
 				return
 			}
 
 			dataMsg := msg.GetDataMsg()
 			if dataMsg != nil {
 				if err := s.addPayload(dataMsg.GetPayload(), nonBlocking); err != nil {
-					logger.Warningf("Block [%d] received from gossip wasn't added to payload buffer: %v", dataMsg.Payload.SeqNum, err)
+					s.logger.Warningf("Block [%d] received from gossip wasn't added to payload buffer: %v", dataMsg.Payload.SeqNum, err)
 					return
 				}
 
 			} else {
-				logger.Debug("Gossip message received is not of data message type, usually this should not happen.")
+				s.logger.Debug("Gossip message received is not of data message type, usually this should not happen.")
 			}
 		}(msg)
 	}
 }
 
 func (s *GossipStateProviderImpl) receiveAndDispatchDirectMessages(ch <-chan protoext.ReceivedMessage) {
 	for msg := range ch {
-		logger.Debug("Dispatching a message", msg)
+		s.logger.Debug("Dispatching a message", msg)
 		go func(msg protoext.ReceivedMessage) {
 			gm := msg.GetGossipMessage()
 			// Check type of the message
 			if protoext.IsRemoteStateMessage(gm.GossipMessage) {
-				logger.Debug("Handling direct state transfer message")
+				s.logger.Debug("Handling direct state transfer message")
 				// Got state transfer request response
 				s.directMessage(msg)
 			} else if gm.GetPrivateData() != nil {
-				logger.Debug("Handling private data collection message")
+				s.logger.Debug("Handling private data collection message")
 				// Handling private data replication message
 				s.privateDataMessage(msg)
 			}
@@ -325,7 +326,7 @@ func (s *GossipStateProviderImpl) receiveAndDispatchDirectMessages(ch <-chan pro
 
 func (s *GossipStateProviderImpl) privateDataMessage(msg protoext.ReceivedMessage) {
 	if !bytes.Equal(msg.GetGossipMessage().Channel, []byte(s.chainID)) {
-		logger.Warning("Received state transfer request for channel",
+		s.logger.Warning("Received state transfer request for channel",
 			string(msg.GetGossipMessage().Channel), "while expecting channel", s.chainID, "skipping request...")
 		return
 	}
@@ -334,7 +335,7 @@ func (s *GossipStateProviderImpl) privateDataMessage(msg protoext.ReceivedMessag
 	pvtDataMsg := gossipMsg.GetPrivateData()
 
 	if pvtDataMsg.Payload == nil {
-		logger.Warning("Malformed private data message, no payload provided")
+		s.logger.Warning("Malformed private data message, no payload provided")
 		return
 	}
 
@@ -343,7 +344,7 @@ func (s *GossipStateProviderImpl) privateDataMessage(msg protoext.ReceivedMessag
 	pvtRwSet := pvtDataMsg.Payload.PrivateRwset
 
 	if len(pvtRwSet) == 0 {
-		logger.Warning("Malformed private data message, no rwset provided, collection name = ", collectionName)
+		s.logger.Warning("Malformed private data message, no rwset provided, collection name = ", collectionName)
 		return
 	}
 
@@ -366,25 +367,25 @@ func (s *GossipStateProviderImpl) privateDataMessage(msg protoext.ReceivedMessag
 	}
 
 	if err := s.ledger.StorePvtData(txID, txPvtRwSetWithConfig, pvtDataMsg.Payload.PrivateSimHeight); err != nil {
-		logger.Errorf("Wasn't able to persist private data for collection %s, due to %s", collectionName, err)
+		s.logger.Errorf("Wasn't able to persist private data for collection %s, due to %s", collectionName, err)
 		msg.Ack(err) // Sending NACK to indicate failure of storing collection
 	}
 
 	msg.Ack(nil)
-	logger.Debug("Private data for collection", collectionName, "has been stored")
+	s.logger.Debug("Private data for collection", collectionName, "has been stored")
 }
 
 func (s *GossipStateProviderImpl) directMessage(msg protoext.ReceivedMessage) {
-	logger.Debug("[ENTER] -> directMessage")
-	defer logger.Debug("[EXIT] ->  directMessage")
+	s.logger.Debug("[ENTER] -> directMessage")
+	defer s.logger.Debug("[EXIT] ->  directMessage")
 
 	if msg == nil {
-		logger.Error("Got nil message via end-to-end channel, should not happen!")
+		s.logger.Error("Got nil message via end-to-end channel, should not happen!")
 		return
 	}
 
 	if !bytes.Equal(msg.GetGossipMessage().Channel, []byte(s.chainID)) {
-		logger.Warning("Received state transfer request for channel",
+		s.logger.Warning("Received state transfer request for channel",
 			string(msg.GetGossipMessage().Channel), "while expecting channel", s.chainID, "skipping request...")
 		return
 	}
@@ -426,25 +427,25 @@ func (s *GossipStateProviderImpl) handleStateRequest(msg protoext.ReceivedMessag
 	request := msg.GetGossipMessage().GetStateRequest()
 
 	if err := s.requestValidator.validate(request, s.config.StateBatchSize); err != nil {
-		logger.Errorf("State request validation failed, %s. Ignoring request...", err)
+		s.logger.Errorf("State request validation failed, %s. Ignoring request...", err)
 		return
 	}
 
 	currentHeight, err := s.ledger.LedgerHeight()
 	if err != nil {
-		logger.Errorf("Cannot access to current ledger height, due to %+v", err)
+		s.logger.Errorf("Cannot access to current ledger height, due to %+v", err)
 		return
 	}
 	if currentHeight < request.EndSeqNum {
-		logger.Warningf("Received state request to transfer blocks with sequence numbers higher  [%d...%d] "+
+		s.logger.Warningf("Received state request to transfer blocks with sequence numbers higher  [%d...%d] "+
 			"than available in ledger (%d)", request.StartSeqNum, request.StartSeqNum, currentHeight)
 	}
 
 	endSeqNum := min(currentHeight, request.EndSeqNum)
 
 	response := &proto.RemoteStateResponse{Payloads: make([]*proto.Payload, 0)}
 	for seqNum := request.StartSeqNum; seqNum <= endSeqNum; seqNum++ {
-		logger.Debug("Reading block ", seqNum, " with private data from the coordinator service")
+		s.logger.Debug("Reading block ", seqNum, " with private data from the coordinator service")
 		connInfo := msg.GetConnectionInfo()
 		peerAuthInfo := protoutil.SignedData{
 			Data:      connInfo.Auth.SignedData,
@@ -454,19 +455,19 @@ func (s *GossipStateProviderImpl) handleStateRequest(msg protoext.ReceivedMessag
 		block, pvtData, err := s.ledger.GetPvtDataAndBlockByNum(seqNum, peerAuthInfo)
 
 		if err != nil {
-			logger.Errorf("cannot read block number %d from ledger, because %+v, skipping...", seqNum, err)
+			s.logger.Errorf("cannot read block number %d from ledger, because %+v, skipping...", seqNum, err)
 			continue
 		}
 
 		if block == nil {
-			logger.Errorf("Wasn't able to read block with sequence number %d from ledger, skipping....", seqNum)
+			s.logger.Errorf("Wasn't able to read block with sequence number %d from ledger, skipping....", seqNum)
 			continue
 		}
 
 		blockBytes, err := pb.Marshal(block)
 
 		if err != nil {
-			logger.Errorf("Could not marshal block: %+v", errors.WithStack(err))
+			s.logger.Errorf("Could not marshal block: %+v", errors.WithStack(err))
 			continue
 		}
 
@@ -475,7 +476,7 @@ func (s *GossipStateProviderImpl) handleStateRequest(msg protoext.ReceivedMessag
 			// Marshal private data
 			pvtBytes, err = pvtData.Marshal()
 			if err != nil {
-				logger.Errorf("Failed to marshal private rwset for block %d due to %+v", seqNum, errors.WithStack(err))
+				s.logger.Errorf("Failed to marshal private rwset for block %d due to %+v", seqNum, errors.WithStack(err))
 				continue
 			}
 		}
@@ -506,16 +507,16 @@ func (s *GossipStateProviderImpl) handleStateResponse(msg protoext.ReceivedMessa
 		return uint64(0), errors.New("Received state transfer response without payload")
 	}
 	for _, payload := range response.GetPayloads() {
-		logger.Debugf("Received payload with sequence number %d.", payload.SeqNum)
+		s.logger.Debugf("Received payload with sequence number %d.", payload.SeqNum)
 		block, err := protoutil.UnmarshalBlock(payload.Data)
 		if err != nil {
-			logger.Warningf("Error unmarshaling payload to block for sequence number %d, due to %+v", payload.SeqNum, err)
+			s.logger.Warningf("Error unmarshaling payload to block for sequence number %d, due to %+v", payload.SeqNum, err)
 			return uint64(0), err
 		}
 
 		if err := s.mediator.VerifyBlock(common2.ChannelID(s.chainID), payload.SeqNum, block); err != nil {
 			err = errors.WithStack(err)
-			logger.Warningf("Error verifying block with sequence number %d, due to %+v", payload.SeqNum, err)
+			s.logger.Warningf("Error verifying block with sequence number %d, due to %+v", payload.SeqNum, err)
 			return uint64(0), err
 		}
 		if max < payload.SeqNum {
@@ -524,7 +525,7 @@ func (s *GossipStateProviderImpl) handleStateResponse(msg protoext.ReceivedMessa
 
 		err = s.addPayload(payload, blocking)
 		if err != nil {
-			logger.Warningf("Block [%d] received from block transfer wasn't added to payload buffer: %v", payload.SeqNum, err)
+			s.logger.Warningf("Block [%d] received from block transfer wasn't added to payload buffer: %v", payload.SeqNum, err)
 		}
 	}
 	return max, nil
@@ -548,47 +549,47 @@ func (s *GossipStateProviderImpl) deliverPayloads() {
 		select {
 		// Wait for notification that next seq has arrived
 		case <-s.payloads.Ready():
-			logger.Debugf("[%s] Ready to transfer payloads (blocks) to the ledger, next block number is = [%d]", s.chainID, s.payloads.Next())
+			s.logger.Debugf("[%s] Ready to transfer payloads (blocks) to the ledger, next block number is = [%d]", s.chainID, s.payloads.Next())
 			// Collect all subsequent payloads
 			for payload := s.payloads.Pop(); payload != nil; payload = s.payloads.Pop() {
 				rawBlock := &common.Block{}
 				if err := pb.Unmarshal(payload.Data, rawBlock); err != nil {
-					logger.Errorf("Error getting block with seqNum = %d due to (%+v)...dropping block", payload.SeqNum, errors.WithStack(err))
+					s.logger.Errorf("Error getting block with seqNum = %d due to (%+v)...dropping block", payload.SeqNum, errors.WithStack(err))
 					continue
 				}
 				if rawBlock.Data == nil || rawBlock.Header == nil {
-					logger.Errorf("Block with claimed sequence %d has no header (%v) or data (%v)",
+					s.logger.Errorf("Block with claimed sequence %d has no header (%v) or data (%v)",
 						payload.SeqNum, rawBlock.Header, rawBlock.Data)
 					continue
 				}
-				logger.Debugf("[%s] Transferring block [%d] with %d transaction(s) to the ledger", s.chainID, payload.SeqNum, len(rawBlock.Data.Data))
+				s.logger.Debugf("[%s] Transferring block [%d] with %d transaction(s) to the ledger", s.chainID, payload.SeqNum, len(rawBlock.Data.Data))
 
 				// Read all private data into slice
 				var p util.PvtDataCollections
 				if payload.PrivateData != nil {
 					err := p.Unmarshal(payload.PrivateData)
 					if err != nil {
-						logger.Errorf("Wasn't able to unmarshal private data for block seqNum = %d due to (%+v)...dropping block", payload.SeqNum, errors.WithStack(err))
+						s.logger.Errorf("Wasn't able to unmarshal private data for block seqNum = %d due to (%+v)...dropping block", payload.SeqNum, errors.WithStack(err))
 						continue
 					}
 				}
 				if err := s.commitBlock(rawBlock, p); err != nil {
 					if executionErr, isExecutionErr := err.(*vsccErrors.VSCCExecutionFailureError); isExecutionErr {
-						logger.Errorf("Failed executing VSCC due to %v. Aborting chain processing", executionErr)
+						s.logger.Errorf("Failed executing VSCC due to %v. Aborting chain processing", executionErr)
 						return
 					}
-					logger.Panicf("Cannot commit block to the ledger due to %+v", errors.WithStack(err))
+					s.logger.Panicf("Cannot commit block to the ledger due to %+v", errors.WithStack(err))
 				}
 			}
 		case <-s.stopCh:
-			logger.Debug("State provider has been stopped, finishing to push new blocks.")
+			s.logger.Debug("State provider has been stopped, finishing to push new blocks.")
 			return
 		}
 	}
 }
 
 func (s *GossipStateProviderImpl) antiEntropy() {
-	defer logger.Debug("State Provider stopped, stopping anti entropy procedure.")
+	defer s.logger.Debug("State Provider stopped, stopping anti entropy procedure.")
 
 	for {
 		select {
@@ -598,11 +599,11 @@ func (s *GossipStateProviderImpl) antiEntropy() {
 			ourHeight, err := s.ledger.LedgerHeight()
 			if err != nil {
 				// Unable to read from ledger continue to the next round
-				logger.Errorf("Cannot obtain ledger height, due to %+v", errors.WithStack(err))
+				s.logger.Errorf("Cannot obtain ledger height, due to %+v", errors.WithStack(err))
 				continue
 			}
 			if ourHeight == 0 {
-				logger.Error("Ledger reported block height of 0 but this should be impossible")
+				s.logger.Error("Ledger reported block height of 0 but this should be impossible")
 				continue
 			}
 			maxHeight := s.maxAvailableLedgerHeight()
@@ -621,7 +622,7 @@ func (s *GossipStateProviderImpl) maxAvailableLedgerHeight() uint64 {
 	max := uint64(0)
 	for _, p := range s.mediator.PeersOfChannel(common2.ChannelID(s.chainID)) {
 		if p.Properties == nil {
-			logger.Debug("Peer", p.PreferredEndpoint(), "doesn't have properties, skipping it")
+			s.logger.Debug("Peer", p.PreferredEndpoint(), "doesn't have properties, skipping it")
 			continue
 		}
 		peerHeight := p.Properties.LedgerHeight
@@ -648,19 +649,19 @@ func (s *GossipStateProviderImpl) requestBlocksInRange(start uint64, end uint64)
 
 		for !responseReceived {
 			if tryCounts > s.config.StateMaxRetries {
-				logger.Warningf("Wasn't  able to get blocks in range [%d...%d), after %d retries",
+				s.logger.Warningf("Wasn't  able to get blocks in range [%d...%d), after %d retries",
 					prev, next, tryCounts)
 				return
 			}
 			// Select peers to ask for blocks
 			peer, err := s.selectPeerToRequestFrom(next)
 			if err != nil {
-				logger.Warningf("Cannot send state request for blocks in range [%d...%d), due to %+v",
+				s.logger.Warningf("Cannot send state request for blocks in range [%d...%d), due to %+v",
 					prev, next, errors.WithStack(err))
 				return
 			}
 
-			logger.Debugf("State transfer, with peer %s, requesting blocks in range [%d...%d), "+
+			s.logger.Debugf("State transfer, with peer %s, requesting blocks in range [%d...%d), "+
 				"for chainID %s", peer.Endpoint, prev, next, s.chainID)
 
 			s.mediator.Send(gossipMsg, peer)
@@ -679,7 +680,7 @@ func (s *GossipStateProviderImpl) requestBlocksInRange(start uint64, end uint64)
 				// Got corresponding response for state request, can continue
 				index, err := s.handleStateResponse(msg)
 				if err != nil {
-					logger.Warningf("Wasn't able to process state response for "+
+					s.logger.Warningf("Wasn't able to process state response for "+
 						"blocks [%d...%d], due to %+v", prev, next, errors.WithStack(err))
 					continue
 				}
@@ -740,7 +741,7 @@ func (s *GossipStateProviderImpl) hasRequiredHeight(height uint64) func(peer dis
 		if peer.Properties != nil {
 			return peer.Properties.LedgerHeight >= height
 		}
-		logger.Debug(peer.PreferredEndpoint(), "doesn't have properties")
+		s.logger.Debug(peer.PreferredEndpoint(), "doesn't have properties")
 		return false
 	}
 }
@@ -758,7 +759,7 @@ func (s *GossipStateProviderImpl) addPayload(payload *proto.Payload, blockingMod
 	if payload == nil {
 		return errors.New("Given payload is nil")
 	}
-	logger.Debugf("[%s] Adding payload to local buffer, blockNum = [%d]", s.chainID, payload.SeqNum)
+	s.logger.Debugf("[%s] Adding payload to local buffer, blockNum = [%d]", s.chainID, payload.SeqNum)
 	height, err := s.ledger.LedgerHeight()
 	if err != nil {
 		return errors.Wrap(err, "Failed obtaining ledger height")
@@ -773,7 +774,7 @@ func (s *GossipStateProviderImpl) addPayload(payload *proto.Payload, blockingMod
 	}
 
 	s.payloads.Push(payload)
-	logger.Debugf("Blocks payloads buffer size for channel [%s] is %d blocks", s.chainID, s.payloads.Size())
+	s.logger.Debugf("Blocks payloads buffer size for channel [%s] is %d blocks", s.chainID, s.payloads.Size())
 	return nil
 }
 
@@ -783,7 +784,7 @@ func (s *GossipStateProviderImpl) commitBlock(block *common.Block, pvtData util.
 
 	// Commit block with available private transactions
 	if err := s.ledger.StoreBlock(block, pvtData); err != nil {
-		logger.Errorf("Got error while committing(%+v)", errors.WithStack(err))
+		s.logger.Errorf("Got error while committing(%+v)", errors.WithStack(err))
 		return err
 	}
 
@@ -792,7 +793,7 @@ func (s *GossipStateProviderImpl) commitBlock(block *common.Block, pvtData util.
 
 	// Update ledger height
 	s.mediator.UpdateLedgerHeight(block.Header.Number+1, common2.ChannelID(s.chainID))
-	logger.Debugf("[%s] Committed block [%d] with %d transaction(s)",
+	s.logger.Debugf("[%s] Committed block [%d] with %d transaction(s)",
 		s.chainID, block.Header.Number, len(block.Data.Data))
 
 	s.stateMetrics.Height.With("channel", s.chainID).Set(float64(block.Header.Number + 1))
```

### gossip/state/state_test.go
```diff
@@ -12,7 +12,6 @@ import (
 	"fmt"
 	"math/rand"
 	"net"
-	"strings"
 	"sync"
 	"sync/atomic"
 	"testing"
@@ -49,9 +48,12 @@ import (
 	gossiputil "github.com/hyperledger/fabric/gossip/util"
 	gutil "github.com/hyperledger/fabric/gossip/util"
 	"github.com/hyperledger/fabric/protoutil"
+	"github.com/onsi/gomega"
 	"github.com/onsi/gomega/gbytes"
 	"github.com/stretchr/testify/assert"
 	"github.com/stretchr/testify/mock"
+	"go.uber.org/zap"
+	"go.uber.org/zap/zapcore"
 )
 
 var (
@@ -344,11 +346,12 @@ func newCommitter() committer.Committer {
 
 func newPeerNodeWithGossip(id int, committer committer.Committer,
 	acceptor peerIdentityAcceptor, g peerNodeGossipSupport, bootPorts ...int) *peerNode {
-	return newPeerNodeWithGossipWithValidator(id, committer, acceptor, g, &validator.MockValidator{}, bootPorts...)
+	logger := flogging.MustGetLogger(gutil.StateLogger)
+	return newPeerNodeWithGossipWithValidator(logger, id, committer, acceptor, g, &validator.MockValidator{}, bootPorts...)
 }
 
 // Constructing pseudo peer node, simulating only gossip and state transfer part
-func newPeerNodeWithGossipWithValidatorWithMetrics(id int, committer committer.Committer,
+func newPeerNodeWithGossipWithValidatorWithMetrics(logger gutil.Logger, id int, committer committer.Committer,
 	acceptor peerIdentityAcceptor, g peerNodeGossipSupport, v txvalidator.Validator,
 	gossipMetrics *metrics.GossipMetrics, bootPorts ...int) (node *peerNode, port int) {
 	cs := &cryptoServiceMock{acceptor: acceptor}
@@ -426,7 +429,7 @@ func newPeerNodeWithGossipWithValidatorWithMetrics(id int, committer committer.C
 		StateChannelSize:     DefStateChannelSize,
 		StateEnabled:         DefStateEnabled,
 	}
-	sp := NewGossipStateProvider("testchannelid", servicesAdapater, coord, gossipMetrics.StateMetrics, blocking, stateConfig)
+	sp := NewGossipStateProvider(logger, "testchannelid", servicesAdapater, coord, gossipMetrics.StateMetrics, blocking, stateConfig)
 	if sp == nil {
 		gRPCServer.Stop()
 		return nil, port
@@ -446,16 +449,17 @@ func newPeerNodeWithGossipWithValidatorWithMetrics(id int, committer committer.C
 // add metrics provider for metrics testing
 func newPeerNodeWithGossipWithMetrics(id int, committer committer.Committer,
 	acceptor peerIdentityAcceptor, g peerNodeGossipSupport, gossipMetrics *metrics.GossipMetrics) *peerNode {
-	node, _ := newPeerNodeWithGossipWithValidatorWithMetrics(id, committer, acceptor, g,
+	logger := flogging.MustGetLogger(gutil.StateLogger)
+	node, _ := newPeerNodeWithGossipWithValidatorWithMetrics(logger, id, committer, acceptor, g,
 		&validator.MockValidator{}, gossipMetrics)
 	return node
 }
 
 // Constructing pseudo peer node, simulating only gossip and state transfer part
-func newPeerNodeWithGossipWithValidator(id int, committer committer.Committer,
+func newPeerNodeWithGossipWithValidator(logger gutil.Logger, id int, committer committer.Committer,
 	acceptor peerIdentityAcceptor, g peerNodeGossipSupport, v txvalidator.Validator, bootPorts ...int) *peerNode {
 	gossipMetrics := metrics.NewGossipMetrics(&disabled.Provider{})
-	node, _ := newPeerNodeWithGossipWithValidatorWithMetrics(id, committer, acceptor, g, v, gossipMetrics, bootPorts...)
+	node, _ := newPeerNodeWithGossipWithValidatorWithMetrics(logger, id, committer, acceptor, g, v, gossipMetrics, bootPorts...)
 	return node
 }
 
@@ -468,7 +472,8 @@ func newPeerNode(id int, committer committer.Committer, acceptor peerIdentityAcc
 func newBootNode(id int, committer committer.Committer, acceptor peerIdentityAcceptor) (node *peerNode, port int) {
 	v := &validator.MockValidator{}
 	gossipMetrics := metrics.NewGossipMetrics(&disabled.Provider{})
-	return newPeerNodeWithGossipWithValidatorWithMetrics(id, committer, acceptor, nil, v, gossipMetrics)
+	logger := flogging.MustGetLogger(gutil.StateLogger)
+	return newPeerNodeWithGossipWithValidatorWithMetrics(logger, id, committer, acceptor, nil, v, gossipMetrics)
 }
 
 func TestNilDirectMsg(t *testing.T) {
@@ -772,17 +777,6 @@ func TestHaltChainProcessing(t *testing.T) {
 		}
 	}
 
-	buf := gbytes.NewBuffer()
-	logging, err := flogging.New(flogging.Config{
-		LogSpec: "debug",
-		Writer:  buf,
-	})
-	assert.NoError(t, err, "failed to create logging")
-
-	defer func(l gossiputil.Logger) { logger = l }(logger)
-	l := logging.Logger("state_test")
-	logger = l
-
 	mc := &mockCommitter{Mock: &mock.Mock{}}
 	mc.On("CommitLegacy", mock.Anything)
 	mc.On("LedgerHeight", mock.Anything).Return(uint64(1), nil)
@@ -797,13 +791,21 @@ func TestHaltChainProcessing(t *testing.T) {
 	v.On("Validate").Return(&errors2.VSCCExecutionFailureError{
 		Err: errors.New("foobar"),
 	}).Once()
-	peerNode := newPeerNodeWithGossipWithValidator(0, mc, noopPeerIdentityAcceptor, g, v)
+
+	buf := gbytes.NewBuffer()
+
+	logger := flogging.MustGetLogger(gutil.StateLogger).WithOptions(zap.Hooks(func(entry zapcore.Entry) error {
+		buf.Write([]byte(entry.Message))
+		buf.Write([]byte("\n"))
+		return nil
+	}))
+	peerNode := newPeerNodeWithGossipWithValidator(logger, 0, mc, noopPeerIdentityAcceptor, g, v)
 	defer peerNode.shutdown()
 	gossipMsgs <- newBlockMsg(1)
 
-	assertLogged(t, buf, "Got error while committing")
-	assertLogged(t, buf, "Aborting chain processing")
-	assertLogged(t, buf, "foobar")
+	gom := gomega.NewGomegaWithT(t)
+	gom.Eventually(buf, time.Minute).Should(gbytes.Say("Failed executing VSCC due to foobar"))
+	gom.Eventually(buf, time.Minute).Should(gbytes.Say("Aborting chain processing"))
 }
 
 func TestFailures(t *testing.T) {
@@ -1411,7 +1413,8 @@ func TestTransferOfPrivateRWSet(t *testing.T) {
 		StateChannelSize:     DefStateChannelSize,
 		StateEnabled:         DefStateEnabled,
 	}
-	st := NewGossipStateProvider(chainID, servicesAdapater, coord1, stateMetrics, blocking, stateConfig)
+	logger := flogging.MustGetLogger(gutil.StateLogger)
+	st := NewGossipStateProvider(logger, chainID, servicesAdapater, coord1, stateMetrics, blocking, stateConfig)
 	defer st.Stop()
 
 	// Mocked state request message
@@ -1657,11 +1660,13 @@ func TestTransferOfPvtDataBetweenPeers(t *testing.T) {
 		StateChannelSize:     DefStateChannelSize,
 		StateEnabled:         DefStateEnabled,
 	}
-	peer1State := NewGossipStateProvider(chainID, mediator, peers["peer1"].coord, stateMetrics, blocking, stateConfig)
+	logger := flogging.MustGetLogger(gutil.StateLogger)
+	peer1State := NewGossipStateProvider(logger, chainID, mediator, peers["peer1"].coord, stateMetrics, blocking, stateConfig)
 	defer peer1State.Stop()
 
 	mediator = &ServicesMediator{GossipAdapter: peers["peer2"], MCSAdapter: cryptoService}
-	peer2State := NewGossipStateProvider(chainID, mediator, peers["peer2"].coord, stateMetrics, blocking, stateConfig)
+	logger = flogging.MustGetLogger(gutil.StateLogger)
+	peer2State := NewGossipStateProvider(logger, chainID, mediator, peers["peer2"].coord, stateMetrics, blocking, stateConfig)
 	defer peer2State.Stop()
 
 	// Make sure state was replicated
@@ -1731,8 +1736,3 @@ func waitUntilTrueOrTimeout(t *testing.T, predicate func() bool, timeout time.Du
 	}
 	t.Log("Stop waiting until timeout or true")
 }
-
-func assertLogged(t *testing.T, buf *gbytes.Buffer, msg string) {
-	observed := func() bool { return strings.Contains(string(buf.Contents()), msg) }
-	waitUntilTrueOrTimeout(t, observed, 30*time.Second)
-}
```
