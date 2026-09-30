# [?] Fix P-chain validator set lookup race condition (#2672)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2024-01-28
Source: https://github.com/ava-labs/avalanchego/commit/68980eb24913b2331db4d020c065d8782df73119
Type: security-commit

## Details
Fix P-chain validator set lookup race condition (#2672)

Co-authored-by: Darioush Jalali <darioush.jalali@avalabs.org>

## Patch
### network/p2p/client.go
```diff
@@ -75,7 +75,7 @@ func (c *Client) AppRequest(
 	c.router.lock.Lock()
 	defer c.router.lock.Unlock()
 
-	appRequestBytes = c.prefixMessage(appRequestBytes)
+	appRequestBytes = PrefixMessage(c.handlerPrefix, appRequestBytes)
 	for nodeID := range nodeIDs {
 		requestID := c.router.requestID
 		if _, ok := c.router.pendingAppRequests[requestID]; ok {
@@ -112,7 +112,7 @@ func (c *Client) AppGossip(
 ) error {
 	return c.sender.SendAppGossip(
 		ctx,
-		c.prefixMessage(appGossipBytes),
+		PrefixMessage(c.handlerPrefix, appGossipBytes),
 	)
 }
 
@@ -125,7 +125,7 @@ func (c *Client) AppGossipSpecific(
 	return c.sender.SendAppGossipSpecific(
 		ctx,
 		nodeIDs,
-		c.prefixMessage(appGossipBytes),
+		PrefixMessage(c.handlerPrefix, appGossipBytes),
 	)
 }
 
@@ -153,7 +153,7 @@ func (c *Client) CrossChainAppRequest(
 		ctx,
 		chainID,
 		requestID,
-		c.prefixMessage(appRequestBytes),
+		PrefixMessage(c.handlerPrefix, appRequestBytes),
 	); err != nil {
 		return err
 	}
@@ -167,15 +167,14 @@ func (c *Client) CrossChainAppRequest(
 	return nil
 }
 
-// prefixMessage prefixes the original message with the handler identifier
-// corresponding to this client.
+// PrefixMessage prefixes the original message with the protocol identifier.
 //
 // Only gossip and request messages need to be prefixed.
 // Response messages don't need to be prefixed because request ids are tracked
 // which map to the expected response handler.
-func (c *Client) prefixMessage(src []byte) []byte {
-	messageBytes := make([]byte, len(c.handlerPrefix)+len(src))
-	copy(messageBytes, c.handlerPrefix)
-	copy(messageBytes[len(c.handlerPrefix):], src)
+func PrefixMessage(prefix, msg []byte) []byte {
+	messageBytes := make([]byte, len(prefix)+len(msg))
+	copy(messageBytes, prefix)
+	copy(messageBytes[len(prefix):], msg)
 	return messageBytes
 }
```

### network/p2p/gossip/gossip.go
```diff
@@ -14,11 +14,8 @@ import (
 
 	"go.uber.org/zap"
 
-	"google.golang.org/protobuf/proto"
-
 	"github.com/ava-labs/avalanchego/ids"
 	"github.com/ava-labs/avalanchego/network/p2p"
-	"github.com/ava-labs/avalanchego/proto/pb/sdk"
 	"github.com/ava-labs/avalanchego/utils"
 	"github.com/ava-labs/avalanchego/utils/buffer"
 	"github.com/ava-labs/avalanchego/utils/logging"
@@ -151,12 +148,7 @@ type PullGossiper[T Gossipable] struct {
 }
 
 func (p *PullGossiper[_]) Gossip(ctx context.Context) error {
-	bloom, salt := p.set.GetFilter()
-	request := &sdk.PullGossipRequest{
-		Filter: bloom,
-		Salt:   salt,
-	}
-	msgBytes, err := proto.Marshal(request)
+	msgBytes, err := MarshalAppRequest(p.set.GetFilter())
 	if err != nil {
 		return err
 	}
@@ -186,14 +178,14 @@ func (p *PullGossiper[_]) handleResponse(
 		return
 	}
 
-	response := &sdk.PullGossipResponse{}
-	if err := proto.Unmarshal(responseBytes, response); err != nil {
+	gossip, err := ParseAppResponse(responseBytes)
+	if err != nil {
 		p.log.Debug("failed to unmarshal gossip response", zap.Error(err))
 		return
 	}
 
 	receivedBytes := 0
-	for _, bytes := range response.Gossip {
+	for _, bytes := range gossip {
 		receivedBytes += len(bytes)
 
 		gossipable, err := p.marshaller.UnmarshalGossip(bytes)
@@ -235,7 +227,7 @@ func (p *PullGossiper[_]) handleResponse(
 		return
 	}
 
-	receivedCountMetric.Add(float64(len(response.Gossip)))
+	receivedCountMetric.Add(float64(len(gossip)))
 	receivedBytesMetric.Add(float64(receivedBytes))
 }
 
@@ -270,11 +262,8 @@ func (p *PushGossiper[T]) Gossip(ctx context.Context) error {
 		return nil
 	}
 
-	msg := &sdk.PushGossip{
-		Gossip: make([][]byte, 0, p.pending.Len()),
-	}
-
 	sentBytes := 0
+	gossip := make([][]byte, 0, p.pending.Len())
 	for sentBytes < p.targetGossipSize {
 		gossipable, ok := p.pending.PeekLeft()
 		if !ok {
@@ -288,12 +277,12 @@ func (p *PushGossiper[T]) Gossip(ctx context.Context) error {
 			return err
 		}
 
-		msg.Gossip = append(msg.Gossip, bytes)
+		gossip = append(gossip, bytes)
 		sentBytes += len(bytes)
 		p.pending.PopLeft()
 	}
 
-	msgBytes, err := proto.Marshal(msg)
+	msgBytes, err := MarshalAppGossip(gossip)
 	if err != nil {
 		return err
 	}
@@ -308,7 +297,7 @@ func (p *PushGossiper[T]) Gossip(ctx context.Context) error {
 		return fmt.Errorf("failed to get sent bytes metric: %w", err)
 	}
 
-	sentCountMetric.Add(float64(len(msg.Gossip)))
+	sentCountMetric.Add(float64(len(gossip)))
 	sentBytesMetric.Add(float64(sentBytes))
 
 	return p.client.AppGossip(ctx, msgBytes)
```

### network/p2p/gossip/handler.go
```diff
@@ -10,11 +10,8 @@ import (
 
 	"go.uber.org/zap"
 
-	"google.golang.org/protobuf/proto"
-
 	"github.com/ava-labs/avalanchego/ids"
 	"github.com/ava-labs/avalanchego/network/p2p"
-	"github.com/ava-labs/avalanchego/proto/pb/sdk"
 	"github.com/ava-labs/avalanchego/utils/bloom"
 	"github.com/ava-labs/avalanchego/utils/logging"
 )
@@ -51,17 +48,7 @@ type Handler[T Gossipable] struct {
 }
 
 func (h Handler[T]) AppRequest(_ context.Context, _ ids.NodeID, _ time.Time, requestBytes []byte) ([]byte, error) {
-	request := &sdk.PullGossipRequest{}
-	if err := proto.Unmarshal(requestBytes, request); err != nil {
-		return nil, err
-	}
-
-	salt, err := ids.ToID(request.Salt)
-	if err != nil {
-		return nil, err
-	}
-
-	filter, err := bloom.Parse(request.Filter)
+	filter, salt, err := ParseAppRequest(requestBytes)
 	if err != nil {
 		return nil, err
 	}
@@ -94,10 +81,6 @@ func (h Handler[T]) AppRequest(_ context.Context, _ ids.NodeID, _ time.Time, req
 		return nil, err
 	}
 
-	response := &sdk.PullGossipResponse{
-		Gossip: gossipBytes,
-	}
-
 	sentCountMetric, err := h.metrics.sentCount.GetMetricWith(pullLabels)
 	if err != nil {
 		return nil, fmt.Errorf("failed to get sent count metric: %w", err)
@@ -108,21 +91,21 @@ func (h Handler[T]) AppRequest(_ context.Context, _ ids.NodeID, _ time.Time, req
 		return nil, fmt.Errorf("failed to get sent bytes metric: %w", err)
 	}
 
-	sentCountMetric.Add(float64(len(response.Gossip)))
+	sentCountMetric.Add(float64(len(gossipBytes)))
 	sentBytesMetric.Add(float64(responseSize))
 
-	return proto.Marshal(response)
+	return MarshalAppResponse(gossipBytes)
 }
 
 func (h Handler[_]) AppGossip(ctx context.Context, nodeID ids.NodeID, gossipBytes []byte) {
-	msg := &sdk.PushGossip{}
-	if err := proto.Unmarshal(gossipBytes, msg); err != nil {
+	gossip, err := ParseAppGossip(gossipBytes)
+	if err != nil {
 		h.log.Debug("failed to unmarshal gossip", zap.Error(err))
 		return
 	}
 
 	receivedBytes := 0
-	for _, bytes := range msg.Gossip {
+	for _, bytes := range gossip {
 		receivedBytes += len(bytes)
 		gossipable, err := h.marshaller.UnmarshalGossip(bytes)
 		if err != nil {
@@ -164,6 +147,6 @@ func (h Handler[_]) AppGossip(ctx context.Context, nodeID ids.NodeID, gossipByte
 		return
 	}
 
-	receivedCountMetric.Add(float64(len(msg.Gossip)))
+	receivedCountMetric.Add(float64(len(gossip)))
 	receivedBytesMetric.Add(float64(receivedBytes))
 }
```

### network/p2p/gossip/message.go
```diff
@@ -0,0 +1,59 @@
+// Copyright (C) 2019-2024, Ava Labs, Inc. All rights reserved.
+// See the file LICENSE for licensing terms.
+
+package gossip
+
+import (
+	"google.golang.org/protobuf/proto"
+
+	"github.com/ava-labs/avalanchego/ids"
+	"github.com/ava-labs/avalanchego/proto/pb/sdk"
+	"github.com/ava-labs/avalanchego/utils/bloom"
+)
+
+func MarshalAppRequest(filter, salt []byte) ([]byte, error) {
+	request := &sdk.PullGossipRequest{
+		Filter: filter,
+		Salt:   salt,
+	}
+	return proto.Marshal(request)
+}
+
+func ParseAppRequest(bytes []byte) (*bloom.ReadFilter, ids.ID, error) {
+	request := &sdk.PullGossipRequest{}
+	if err := proto.Unmarshal(bytes, request); err != nil {
+		return nil, ids.Empty, err
+	}
+
+	salt, err := ids.ToID(request.Salt)
+	if err != nil {
+		return nil, ids.Empty, err
+	}
+
+	filter, err := bloom.Parse(request.Filter)
+	return filter, salt, err
+}
+
+func MarshalAppResponse(gossip [][]byte) ([]byte, error) {
+	return proto.Marshal(&sdk.PullGossipResponse{
+		Gossip: gossip,
+	})
+}
+
+func ParseAppResponse(bytes []byte) ([][]byte, error) {
+	response := &sdk.PullGossipResponse{}
+	err := proto.Unmarshal(bytes, response)
+	return response.Gossip, err
+}
+
+func MarshalAppGossip(gossip [][]byte) ([]byte, error) {
+	return proto.Marshal(&sdk.PushGossip{
+		Gossip: gossip,
+	})
+}
+
+func ParseAppGossip(bytes []byte) ([][]byte, error) {
+	msg := &sdk.PushGossip{}
+	err := proto.Unmarshal(bytes, msg)
+	return msg.Gossip, err
+}
```

### network/p2p/network.go
```diff
@@ -217,7 +217,7 @@ func (n *Network) NewClient(handlerID uint64, options ...ClientOption) *Client {
 	client := &Client{
 		handlerID:     handlerID,
 		handlerIDStr:  strconv.FormatUint(handlerID, 10),
-		handlerPrefix: binary.AppendUvarint(nil, handlerID),
+		handlerPrefix: ProtocolPrefix(handlerID),
 		sender:        n.sender,
 		router:        n.router,
 		options: &clientOptions{
@@ -281,3 +281,7 @@ type peerSampler struct {
 func (p peerSampler) Sample(_ context.Context, limit int) []ids.NodeID {
 	return p.peers.Sample(limit)
 }
+
+func ProtocolPrefix(handlerID uint64) []byte {
+	return binary.AppendUvarint(nil, handlerID)
+}
```

### network/p2p/router.go
```diff
@@ -399,18 +399,19 @@ func (r *router) CrossChainAppResponse(ctx context.Context, chainID ids.ID, requ
 // - A boolean indicating that parsing succeeded.
 //
 // Invariant: Assumes [r.lock] isn't held.
-func (r *router) parse(msg []byte) ([]byte, *meteredHandler, string, bool) {
-	handlerID, bytesRead := binary.Uvarint(msg)
-	if bytesRead <= 0 {
+func (r *router) parse(prefixedMsg []byte) ([]byte, *meteredHandler, string, bool) {
+	handlerID, msg, ok := ParseMessage(prefixedMsg)
+	if !ok {
 		return nil, nil, "", false
 	}
 
+	handlerStr := strconv.FormatUint(handlerID, 10)
+
 	r.lock.RLock()
 	defer r.lock.RUnlock()
 
-	handlerStr := strconv.FormatUint(handlerID, 10)
 	handler, ok := r.handlers[handlerID]
-	return msg[bytesRead:], handler, handlerStr, ok
+	return msg, handler, handlerStr, ok
 }
 
 // Invariant: Assumes [r.lock] isn't held.
@@ -432,3 +433,17 @@ func (r *router) clearCrossChainAppRequest(requestID uint32) (pendingCrossChainA
 	delete(r.pendingCrossChainAppRequests, requestID)
 	return callback, ok
 }
+
+// Parse a gossip or request message.
+//
+// Returns:
+// - The protocol ID.
+// - The unprefixed protocol message.
+// - A boolean indicating that parsing succeeded.
+func ParseMessage(msg []byte) (uint64, []byte, bool) {
+	handlerID, bytesRead := binary.Uvarint(msg)
+	if bytesRead <= 0 {
+		return 0, nil, false
+	}
+	return handlerID, msg[bytesRead:], true
+}
```

### vms/platformvm/network/network.go
```diff
@@ -24,7 +24,7 @@ import (
 	"github.com/ava-labs/avalanchego/vms/platformvm/txs/mempool"
 )
 
-const txGossipHandlerID = 0
+const TxGossipHandlerID = 0
 
 type Network interface {
 	common.AppHandler
@@ -80,7 +80,7 @@ func New(
 		config.MaxValidatorSetStaleness,
 	)
 	txGossipClient := p2pNetwork.NewClient(
-		txGossipHandlerID,
+		TxGossipHandlerID,
 		p2p.WithValidatorSampling(validators),
 	)
 	txGossipMetrics, err := gossip.NewMetrics(registerer, "tx")
@@ -154,7 +154,7 @@ func New(
 		appRequestHandler: validatorHandler,
 	}
 
-	if err := p2pNetwork.AddHandler(txGossipHandlerID, txGossipHandler); err != nil {
+	if err := p2pNetwork.AddHandler(TxGossipHandlerID, txGossipHandler); err != nil {
 		return nil, err
 	}
 
```

### vms/platformvm/vm.go
```diff
@@ -205,7 +205,10 @@ func (vm *VM) Initialize(
 		chainCtx.Log,
 		chainCtx.NodeID,
 		chainCtx.SubnetID,
-		chainCtx.ValidatorState,
+		validators.NewLockedState(
+			&chainCtx.Lock,
+			validatorManager,
+		),
 		txVerifier,
 		mempool,
 		txExecutorBackend.Config.PartialSyncPrimaryNetwork,
```

### vms/platformvm/vm_regression_test.go
```diff
@@ -14,26 +14,33 @@ import (
 
 	"github.com/stretchr/testify/require"
 
+	"golang.org/x/sync/errgroup"
+
 	"github.com/ava-labs/avalanchego/chains"
 	"github.com/ava-labs/avalanchego/chains/atomic"
 	"github.com/ava-labs/avalanchego/database"
 	"github.com/ava-labs/avalanchego/database/memdb"
 	"github.com/ava-labs/avalanchego/database/prefixdb"
 	"github.com/ava-labs/avalanchego/ids"
+	"github.com/ava-labs/avalanchego/network/p2p"
+	"github.com/ava-labs/avalanchego/network/p2p/gossip"
 	"github.com/ava-labs/avalanchego/snow/choices"
 	"github.com/ava-labs/avalanchego/snow/consensus/snowman"
 	"github.com/ava-labs/avalanchego/snow/engine/common"
 	"github.com/ava-labs/avalanchego/snow/snowtest"
 	"github.com/ava-labs/avalanchego/snow/uptime"
 	"github.com/ava-labs/avalanchego/snow/validators"
+	"github.com/ava-labs/avalanchego/utils/bloom"
 	"github.com/ava-labs/avalanchego/utils/constants"
 	"github.com/ava-labs/avalanchego/utils/crypto/bls"
 	"github.com/ava-labs/avalanchego/utils/crypto/secp256k1"
 	"github.com/ava-labs/avalanchego/utils/timer/mockable"
+	"github.com/ava-labs/avalanchego/version"
 	"github.com/ava-labs/avalanchego/vms/components/avax"
 	"github.com/ava-labs/avalanchego/vms/platformvm/block"
 	"github.com/ava-labs/avalanchego/vms/platformvm/config"
 	"github.com/ava-labs/avalanchego/vms/platformvm/metrics"
+	"github.com/ava-labs/avalanchego/vms/platformvm/network"
 	"github.com/ava-labs/avalanchego/vms/platformvm/reward"
 	"github.com/ava-labs/avalanchego/vms/platformvm/signer"
 	"github.com/ava-labs/avalanchego/vms/platformvm/state"
@@ -2218,6 +2225,72 @@ func TestSubnetValidatorSetAfterPrimaryNetworkValidatorRemoval(t *testing.T) {
 	require.NoError(err)
 }
 
+func TestValidatorSetRaceCondition(t *testing.T) {
+	require := require.New(t)
+	vm, _, _ := defaultVM(t, cortinaFork)
+	vm.ctx.Lock.Lock()
+	defer vm.ctx.Lock.Unlock()
+
+	nodeID := ids.GenerateTestNodeID()
+	require.NoError(vm.Connected(context.Background(), nodeID, version.CurrentApp))
+
+	protocolAppRequestBytest, err := gossip.MarshalAppRequest(
+		bloom.EmptyFilter.Marshal(),
+		ids.Empty[:],
+	)
+	require.NoError(err)
+
+	appRequestBytes := p2p.PrefixMessage(
+		p2p.ProtocolPrefix(network.TxGossipHandlerID),
+		protocolAppRequestBytest,
+	)
+
+	var (
+		eg          errgroup.Group
+		ctx, cancel = context.WithCancel(context.Background())
+	)
+	// keep 10 workers running
+	for i := 0; i < 10; i++ {
+		eg.Go(func() error {
+			for ctx.Err() == nil {
+				err := vm.AppRequest(
+					context.Background(),
+					nodeID,
+					0,
+					time.Now().Add(time.Hour),
+					appRequestBytes,
+				)
+				if err != nil {
+					return err
+				}
+			}
+			return nil
+		})
+	}
+
+	// If the validator set lock isn't held, the race detector should fail here.
+	for i := uint64(0); i < 1000; i++ {
+		blk, err := block.NewBanffStandardBlock(
+			time.Now(),
+			vm.state.GetLastAccepted(),
+			i,
+			nil,
+		)
+		require.NoError(err)
+
+		vm.state.SetLastAccepted(blk.ID())
+		vm.state.SetHeight(blk.Height())
+		vm.state.AddStatelessBlock(blk)
+	}
+
+	// If the validator set lock is grabbed, we need to make sure to release the
+	// lock to avoid a deadlock.
+	vm.ctx.Lock.Unlock()
+	cancel() // stop and wait for workers
+	require.NoError(eg.Wait())
+	vm.ctx.Lock.Lock()
+}
+
 func buildAndAcceptStandardBlock(vm *VM) error {
 	blk, err := vm.Builder.BuildBlock(context.Background())
 	if err != nil {
```

### vms/platformvm/vm_test.go
```diff
@@ -277,13 +277,14 @@ func defaultVM(t *testing.T, fork activeFork) (*VM, database.Database, *mutableS
 		return nil
 	}
 
+	dynamicConfigBytes := []byte(`{"network":{"max-validator-set-staleness":0}}`)
 	require.NoError(vm.Initialize(
 		context.Background(),
 		ctx,
 		chainDB,
 		genesisBytes,
 		nil,
-		nil,
+		dynamicConfigBytes,
 		msgChan,
 		nil,
 		appSender,
```
