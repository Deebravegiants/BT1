# [?] Node/Gacct: Fix deadlock when publishing xfers (#2843)

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2023-05-04
Source: https://github.com/wormhole-foundation/wormhole/commit/cfeda55cce3094942936aa4126d9c6a652a590c3
Type: security-commit

## Details
Node/Gacct: Fix deadlock when publishing xfers (#2843)

* Node/Gacct: Fix deadlock when publishing xfers

Change-Id: Ia4dd4eebb9c02fa81a98f368c527e15cca8574ac

* Fix lint errors

Change-Id: Iaef3fefca87de298edbbf43009584c30252b9fe7

## Patch
### node/cmd/guardiand/node.go
```diff
@@ -1049,7 +1049,7 @@ func runNode(cmd *cobra.Command, args []string) {
 	// If accountantCheckEnabled is set to true, token bridge transfers will not be signed and published until they
 	// are approved by the accountant smart contract.
 	acctLogger := logger.With(zap.String("component", "gacct"))
-	acctReadC, acctWriteC := makeChannelPair[*common.MessagePublication](0)
+	acctReadC, acctWriteC := makeChannelPair[*common.MessagePublication](accountant.MsgChannelCapacity)
 
 	var acct *accountant.Accountant
 	if *accountantContract != "" {
```

### node/pkg/accountant/accountant.go
```diff
@@ -17,7 +17,8 @@ import (
 	"github.com/certusone/wormhole/node/pkg/db"
 	gossipv1 "github.com/certusone/wormhole/node/pkg/proto/gossip/v1"
 	"github.com/certusone/wormhole/node/pkg/supervisor"
-	"github.com/certusone/wormhole/node/pkg/wormconn"
+	sdktypes "github.com/cosmos/cosmos-sdk/types"
+	sdktx "github.com/cosmos/cosmos-sdk/types/tx"
 	"github.com/wormhole-foundation/wormhole/sdk"
 	"github.com/wormhole-foundation/wormhole/sdk/vaa"
 
@@ -32,9 +33,22 @@ const (
 	TestNetMode = 2
 	DevNetMode  = 3
 	GoTestMode  = 4
+	MockMode    = 5
 )
 
+// MsgChannelCapacity specifies the capacity of the message channel used to publish messages released from the accountant.
+// This channel should not back up, but if it does, the accountant will start dropping messages, which would require reobservations.
+const MsgChannelCapacity = 5 * batchSize
+
 type (
+	AccountantWormchainConn interface {
+		Close()
+		SenderAddress() string
+		SubmitQuery(ctx context.Context, contractAddress string, query []byte) ([]byte, error)
+		SignAndBroadcastTx(ctx context.Context, msg sdktypes.Msg) (*sdktx.BroadcastTxResponse, error)
+		BroadcastTxResponseToString(txResp *sdktx.BroadcastTxResponse) string
+	}
+
 	// tokenBridgeKey is the key to the map of token bridges being monitored
 	tokenBridgeKey struct {
 		emitterChainId vaa.ChainID
@@ -74,7 +88,7 @@ type Accountant struct {
 	obsvReqWriteC        chan<- *gossipv1.ObservationRequest
 	contract             string
 	wsUrl                string
-	wormchainConn        *wormconn.ClientConn
+	wormchainConn        AccountantWormchainConn
 	enforceFlag          bool
 	gk                   *ecdsa.PrivateKey
 	gst                  *common.GuardianSetState
@@ -98,7 +112,7 @@ func NewAccountant(
 	obsvReqWriteC chan<- *gossipv1.ObservationRequest,
 	contract string, // the address of the smart contract on wormchain
 	wsUrl string, // the URL of the wormchain websocket interface
-	wormchainConn *wormconn.ClientConn, // used for communicating with the smart contract
+	wormchainConn AccountantWormchainConn, // used for communicating with the smart contract
 	enforceFlag bool, // whether or not accountant should be enforced
 	gk *ecdsa.PrivateKey, // the guardian key used for signing observation requests
 	gst *common.GuardianSetState, // used to get the current guardian set index when sending observation requests
@@ -134,7 +148,7 @@ func (acct *Accountant) Start(ctx context.Context) error {
 	emitterMap := sdk.KnownTokenbridgeEmitters
 	if acct.env == TestNetMode {
 		emitterMap = sdk.KnownTestnetTokenbridgeEmitters
-	} else if acct.env == DevNetMode || acct.env == GoTestMode {
+	} else if acct.env == DevNetMode || acct.env == GoTestMode || acct.env == MockMode {
 		emitterMap = sdk.KnownDevnetTokenbridgeEmitters
 	}
 
@@ -162,7 +176,12 @@ func (acct *Accountant) Start(ctx context.Context) error {
 	}
 
 	// Start the watcher to listen to transfer events from the smart contract.
-	if acct.env != GoTestMode {
+	if acct.env == MockMode {
+		// We're not in a runnable context, so we can't use supervisor.
+		go func() {
+			_ = acct.worker(ctx)
+		}()
+	} else if acct.env != GoTestMode {
 		if err := supervisor.Run(ctx, "acctworker", common.WrapWithScissors(acct.worker, "acctworker")); err != nil {
 			return fmt.Errorf("failed to start submit observation worker: %w", err)
 		}
@@ -265,11 +284,15 @@ func (acct *Accountant) SubmitObservation(msg *common.MessagePublication) (bool,
 	return !acct.enforceFlag, nil
 }
 
-// publishTransferAlreadyLocked publishes a pending transfer to the accountant channel and updates the timestamp. It assumes the caller holds the lock.
+// publishTransferAlreadyLocked publishes a pending transfer to the accountant channel and deletes it from the pending map. It assumes the caller holds the lock.
 func (acct *Accountant) publishTransferAlreadyLocked(pe *pendingEntry) {
 	if acct.enforceFlag {
-		acct.logger.Debug("publishTransferAlreadyLocked: notifying the processor", zap.String("msgId", pe.msgId))
-		acct.msgChan <- pe.msg
+		select {
+		case acct.msgChan <- pe.msg:
+			acct.logger.Debug("published transfer to channel", zap.String("msgId", pe.msgId))
+		default:
+			acct.logger.Error("unable to publish transfer because the channel is full", zap.String("msgId", pe.msgId))
+		}
 	}
 
 	acct.deletePendingTransferAlreadyLocked(pe.msgId)
```

### node/pkg/accountant/accountant_test.go
```diff
@@ -3,7 +3,9 @@ package accountant
 import (
 	"context"
 	"encoding/binary"
+	"encoding/json"
 	"math/big"
+	"sync"
 	"testing"
 	"time"
 
@@ -13,6 +15,9 @@ import (
 	ethCommon "github.com/ethereum/go-ethereum/common"
 	ethCrypto "github.com/ethereum/go-ethereum/crypto"
 
+	sdktypes "github.com/cosmos/cosmos-sdk/types"
+	sdktx "github.com/cosmos/cosmos-sdk/types/tx"
+
 	"github.com/certusone/wormhole/node/pkg/common"
 	"github.com/certusone/wormhole/node/pkg/db"
 	"github.com/certusone/wormhole/node/pkg/devnet"
@@ -26,35 +31,99 @@ const (
 	dontEnforceAccountant = false
 )
 
+type MockAccountantWormchainConn struct {
+	BroadcastTxResponse string
+
+	lock   sync.Mutex
+	txResp *sdktx.BroadcastTxResponse
+}
+
+func (c *MockAccountantWormchainConn) Close() {
+}
+
+func (c *MockAccountantWormchainConn) SenderAddress() string {
+	return "wormfakesigner"
+}
+
+func (c *MockAccountantWormchainConn) SubmitQuery(ctx context.Context, contractAddress string, query []byte) ([]byte, error) {
+	return []byte{}, nil
+}
+
+func (c *MockAccountantWormchainConn) SignAndBroadcastTx(ctx context.Context, msg sdktypes.Msg) (*sdktx.BroadcastTxResponse, error) {
+	for {
+		c.lock.Lock()
+		if c.txResp != nil {
+			resp := c.txResp
+			c.txResp = nil
+			c.lock.Unlock()
+			return resp, nil
+		}
+		c.lock.Unlock()
+		time.Sleep(50 * time.Millisecond)
+	}
+}
+
+func (c *MockAccountantWormchainConn) BroadcastTxResponseToString(txResp *sdktx.BroadcastTxResponse) string {
+	return c.BroadcastTxResponse
+}
+
+func (c *MockAccountantWormchainConn) SetTxResp(txResp *sdktx.BroadcastTxResponse) {
+	c.lock.Lock()
+	defer c.lock.Unlock()
+	c.txResp = txResp
+}
+
+func (c *MockAccountantWormchainConn) TxRespPending() bool {
+	c.lock.Lock()
+	defer c.lock.Unlock()
+	return c.txResp != nil
+}
+
+func (c *MockAccountantWormchainConn) WaitUntilTxRespConsumed() {
+	for {
+		stillPending := c.TxRespPending()
+		time.Sleep(50 * time.Millisecond)
+		if !stillPending {
+			break
+		}
+	}
+}
+
 func newAccountantForTest(
 	t *testing.T,
+	logger *zap.Logger,
 	ctx context.Context,
 	accountantCheckEnabled bool,
 	obsvReqWriteC chan<- *gossipv1.ObservationRequest,
 	acctWriteC chan<- *common.MessagePublication,
+	wormchainConn *MockAccountantWormchainConn,
 ) *Accountant {
-	logger := zap.NewNop()
 	var db db.MockAccountantDB
 
 	gk := devnet.InsecureDeterministicEcdsaKeyByIndex(ethCrypto.S256(), uint64(0))
 
 	gst := common.NewGuardianSetState(nil)
-	gs := &common.GuardianSet{}
+	gs := &common.GuardianSet{Keys: []ethCommon.Address{ethCommon.HexToAddress("0xbeFA429d57cD18b7F8A4d91A2da9AB4AF05d0FBe")}}
 	gst.Set(gs)
 
+	env := GoTestMode
+	if wormchainConn != nil {
+		env = MockMode
+	}
+
 	acct := NewAccountant(
 		ctx,
 		logger,
 		&db,
 		obsvReqWriteC,
 		"0xdeadbeef", // accountantContract
 		"none",       // accountantWS
-		nil,          // wormchainConn
+		wormchainConn,
 		accountantCheckEnabled,
 		gk,
 		gst,
 		acctWriteC,
-		GoTestMode,
+		env,
 	)
 
 	err := acct.Start(ctx)
@@ -103,9 +172,10 @@ func buildMockTransferPayloadBytes(
 
 func TestVaaFromUninterestingEmitter(t *testing.T) {
 	ctx := context.Background()
+	logger := zap.NewNop()
 	obsvReqWriteC := make(chan *gossipv1.ObservationRequest, 10)
 	acctChan := make(chan *common.MessagePublication, 10)
-	acct := newAccountantForTest(t, ctx, enforceAccountant, obsvReqWriteC, acctChan)
+	acct := newAccountantForTest(t, logger, ctx, enforceAccountant, obsvReqWriteC, acctChan, nil)
 	require.NotNil(t, acct)
 
 	emitterAddr, _ := vaa.StringToAddress("0x00")
@@ -130,9 +200,10 @@ func TestVaaFromUninterestingEmitter(t *testing.T) {
 
 func TestVaaForUninterestingPayloadType(t *testing.T) {
 	ctx := context.Background()
+	logger := zap.NewNop()
 	obsvReqWriteC := make(chan *gossipv1.ObservationRequest, 10)
 	acctChan := make(chan *common.MessagePublication, 10)
-	acct := newAccountantForTest(t, ctx, enforceAccountant, obsvReqWriteC, acctChan)
+	acct := newAccountantForTest(t, logger, ctx, enforceAccountant, obsvReqWriteC, acctChan, nil)
 	require.NotNil(t, acct)
 
 	emitterAddr, _ := vaa.StringToAddress("0x0290fb167208af455bb137780163b7b7a9a10c16")
@@ -157,9 +228,10 @@ func TestVaaForUninterestingPayloadType(t *testing.T) {
 
 func TestInterestingTransferShouldNotBeBlockedWhenNotEnforcingAccountant(t *testing.T) {
 	ctx := context.Background()
+	logger := zap.NewNop()
 	obsvReqWriteC := make(chan *gossipv1.ObservationRequest, 10)
 	acctChan := make(chan *common.MessagePublication, 10)
-	acct := newAccountantForTest(t, ctx, dontEnforceAccountant, obsvReqWriteC, acctChan)
+	acct := newAccountantForTest(t, logger, ctx, dontEnforceAccountant, obsvReqWriteC, acctChan, nil)
 	require.NotNil(t, acct)
 
 	emitterAddr, _ := vaa.StringToAddress("0000000000000000000000000290fb167208af455bb137780163b7b7a9a10c16")
@@ -200,9 +272,10 @@ func TestInterestingTransferShouldNotBeBlockedWhenNotEnforcingAccountant(t *test
 
 func TestInterestingTransferShouldBeBlockedWhenEnforcingAccountant(t *testing.T) {
 	ctx := context.Background()
+	logger := zap.NewNop()
 	obsvReqWriteC := make(chan *gossipv1.ObservationRequest, 10)
 	acctChan := make(chan *common.MessagePublication, 10)
-	acct := newAccountantForTest(t, ctx, enforceAccountant, obsvReqWriteC, acctChan)
+	acct := newAccountantForTest(t, logger, ctx, enforceAccountant, obsvReqWriteC, acctChan, nil)
 	require.NotNil(t, acct)
 
 	emitterAddr, _ := vaa.StringToAddress("0000000000000000000000000290fb167208af455bb137780163b7b7a9a10c16")
@@ -247,3 +320,82 @@ func TestInterestingTransferShouldBeBlockedWhenEnforcingAccountant(t *testing.T)
 	assert.Equal(t, 1, len(acct.msgChan))
 	assert.Equal(t, 0, len(acct.pendingTransfers))
 }
+
+func TestForDeadlock(t *testing.T) {
+	ctx := context.Background()
+	logger, _ := zap.NewDevelopment()
+	obsvReqWriteC := make(chan *gossipv1.ObservationRequest, 10)
+	acctChan := make(chan *common.MessagePublication, MsgChannelCapacity)
+	wormchainConn := MockAccountantWormchainConn{}
+	acct := newAccountantForTest(t, logger, ctx, enforceAccountant, obsvReqWriteC, acctChan, &wormchainConn)
+	require.NotNil(t, acct)
+
+	emitterAddr, _ := vaa.StringToAddress("0000000000000000000000000290fb167208af455bb137780163b7b7a9a10c16")
+
+	payloadBytes := buildMockTransferPayloadBytes(1,
+		vaa.ChainIDEthereum,
+		"0x707f9118e33a9b8998bea41dd0d46f38bb963fc8",
+		vaa.ChainIDPolygon,
+		"0x707f9118e33a9b8998bea41dd0d46f38bb963fc8",
+		1.25,
+	)
+
+	msg := common.MessagePublication{
+		TxHash:           hashFromString("0x06f541f5ecfc43407c31587aa6ac3a689e8960f36dc23c332db5510dfc6a4063"),
+		Timestamp:        time.Unix(int64(1654543099), 0),
+		Nonce:            uint32(1),
+		Sequence:         uint64(1683136244),
+		EmitterChain:     vaa.ChainIDEthereum,
+		EmitterAddress:   emitterAddr,
+		ConsistencyLevel: uint8(32),
+		Payload:          payloadBytes,
+	}
+
+	var txResp sdktx.BroadcastTxResponse
+	err := json.Unmarshal(createTxRespForCommitted(), &txResp)
+	require.NoError(t, err)
+	wormchainConn.SetTxResp(&txResp)
+
+	shouldPublish, err := acct.SubmitObservation(&msg)
+	require.NoError(t, err)
+	assert.Equal(t, false, shouldPublish)
+	assert.Equal(t, 1, len(acct.pendingTransfers))
+	assert.Equal(t, 0, len(acct.msgChan))
+
+	// Wait until the response gets received from the contract.
+	wormchainConn.WaitUntilTxRespConsumed()
+
+	assert.Equal(t, 1, len(acct.msgChan))
+
+	msg2 := common.MessagePublication{
+		TxHash:           hashFromString("0x06f541f5ecfc43407c31587aa6ac3a689e8960f36dc23c332db5510dfc6a4063"),
+		Timestamp:        time.Unix(int64(1654543099), 0),
+		Nonce:            uint32(1),
+		Sequence:         uint64(1683136244),
+		EmitterChain:     vaa.ChainIDEthereum,
+		EmitterAddress:   emitterAddr,
+		ConsistencyLevel: uint8(32),
+		Payload:          payloadBytes,
+	}
+
+	var txResp2 sdktx.BroadcastTxResponse
+	err = json.Unmarshal(createTxRespForCommitted(), &txResp2)
+	require.NoError(t, err)
+	wormchainConn.SetTxResp(&txResp2)
+
+	shouldPublish, _ = acct.SubmitObservation(&msg2)
+	require.NoError(t, err)
+	assert.Equal(t, false, shouldPublish)
+	assert.Equal(t, 1, len(acct.pendingTransfers))
+	assert.Equal(t, 1, len(acct.msgChan))
+
+	wormchainConn.WaitUntilTxRespConsumed()
+
+	assert.Equal(t, 2, len(acct.msgChan))
+
+	resultMsg := <-acctChan
+	assert.Equal(t, msg, *resultMsg)
+
+	resultMsg2 := <-acctChan
+	assert.Equal(t, msg2, *resultMsg2)
+}
```

### node/pkg/accountant/data_for_test.go
```diff
@@ -5206,3 +5206,211 @@ func createTransferKeysForTestingBatchTransferStatus(t *testing.T, num int) ([]T
 	respBytes = append(respBytes, []byte("]}")...)
 	return keys, respBytes
 }
+
+// createTxRespForCommitted creates a TxResponse as returned by the accountant contract for a transfer on ethereum that has been committed.
+func createTxRespForCommitted() []byte {
+	respJson := `
+	{
+  "tx_response": {
+    "height": 966,
+    "txhash": "673097FB69A0E78C8B542C5F9BD826BB7C55FAE9560972DE6B075612E2CCB0A5",
+    "codespace": "",
+    "code": 0,
+    "data": "0AD2010A242F636F736D7761736D2E7761736D2E76312E4D736745786563757465436F6E747261637412A9010AA6015B7B226B6579223A7B22656D69747465725F636861696E223A322C22656D69747465725F61646472657373223A2230303030303030303030303030303030303030303030303030323930666231363732303861663435356262313337373830313633623762376139613130633136222C2273657175656E6365223A313638333133363234347D2C22737461747573223A7B2274797065223A22636F6D6D6974746564227D7D5D",
+    "raw_log": "[{\"events\":[{\"type\":\"execute\",\"attributes\":[{\"key\":\"_contract_address\",\"value\":\"wormhole14hj2tavq8fpesdwxxcu44rty3hh90vhujrvcmstl4zr3txmfvw9srrg465\"}]},{\"type\":\"message\",\"attributes\":[{\"key\":\"action\",\"value\":\"/cosmwasm.wasm.v1.MsgExecuteContract\"},{\"key\":\"module\",\"value\":\"wasm\"},{\"key\":\"sender\",\"value\":\"wormhole1cyyzpxplxdzkeea7kwsydadg87357qna3zg3tq\"}]},{\"type\":\"wasm\",\"attributes\":[{\"key\":\"_contract_address\",\"value\":\"wormhole14hj2tavq8fpesdwxxcu44rty3hh90vhujrvcmstl4zr3txmfvw9srrg465\"},{\"key\":\"action\",\"value\":\"submit_observations\"},{\"key\":\"owner\",\"value\":\"wormhole1cyyzpxplxdzkeea7kwsydadg87357qna3zg3tq\"}]},{\"type\":\"wasm-Observation\",\"attributes\":[{\"key\":\"_contract_address\",\"value\":\"wormhole14hj2tavq8fpesdwxxcu44rty3hh90vhujrvcmstl4zr3txmfvw9srrg465\"},{\"key\":\"tx_hash\",\"value\":\"\\\"guolNsXRZxgwy0kSD5RHnjS1RZao3TafvCZmZnp2X0s=\\\"\"},{\"key\":\"timestamp\",\"value\":\"1683136244\"},{\"key\":\"nonce\",\"value\":\"0\"},{\"key\":\"emitter_chain\",\"value\":\"2\"},{\"key\":\"emitter_address\",\"value\":\"\\\"0000000000000000000000000290fb167208af455bb137780163b7b7a9a10c16\\\"\"},{\"key\":\"sequence\",\"value\":\"1683136244\"},{\"key\":\"consistency_level\",\"value\":\"15\"},{\"key\":\"payload\",\"value\":\"\\\"AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA3gtrOnZAAAAAAAAAAAAAAAAAAALYvmvwuqdOCpBwFmecrpGQ6A3QoAAgAAAAAAAAAAAAAAAMEIIJg/M0Vs576zoEb1qD+jTwJ9DCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==\\\"\"}]}]}]",
+    "logs": [
+      {
+        "msg_index": 0,
+        "log": "",
+        "events": [
+          {
+            "type": "execute",
+            "attributes": [
+              {
+                "key": "_contract_address",
+                "value": "wormhole14hj2tavq8fpesdwxxcu44rty3hh90vhujrvcmstl4zr3txmfvw9srrg465"
+              }
+            ]
+          },
+          {
+            "type": "message",
+            "attributes": [
+              {
+                "key": "action",
+                "value": "/cosmwasm.wasm.v1.MsgExecuteContract"
+              },
+              { "key": "module", "value": "wasm" },
+              {
+                "key": "sender",
+                "value": "wormhole1cyyzpxplxdzkeea7kwsydadg87357qna3zg3tq"
+              }
+            ]
+          },
+          {
+            "type": "wasm",
+            "attributes": [
+              {
+                "key": "_contract_address",
+                "value": "wormhole14hj2tavq8fpesdwxxcu44rty3hh90vhujrvcmstl4zr3txmfvw9srrg465"
+              },
+              { "key": "action", "value": "submit_observations" },
+              {
+                "key": "owner",
+                "value": "wormhole1cyyzpxplxdzkeea7kwsydadg87357qna3zg3tq"
+              }
+            ]
+          },
+          {
+            "type": "wasm-Observation",
+            "attributes": [
+              {
+                "key": "_contract_address",
+                "value": "wormhole14hj2tavq8fpesdwxxcu44rty3hh90vhujrvcmstl4zr3txmfvw9srrg465"
+              },
+              {
+                "key": "tx_hash",
+                "value": "\"guolNsXRZxgwy0kSD5RHnjS1RZao3TafvCZmZnp2X0s=\""
+              },
+              { "key": "timestamp", "value": "1683136244" },
+              { "key": "nonce", "value": "0" },
+              { "key": "emitter_chain", "value": "2" },
+              {
+                "key": "emitter_address",
+                "value": "\"0000000000000000000000000290fb167208af455bb137780163b7b7a9a10c16\""
+              },
+              { "key": "sequence", "value": "1683136244" },
+              { "key": "consistency_level", "value": "15" },
+              {
+                "key": "payload",
+                "value": "\"AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA3gtrOnZAAAAAAAAAAAAAAAAAAALYvmvwuqdOCpBwFmecrpGQ6A3QoAAgAAAAAAAAAAAAAAAMEIIJg/M0Vs576zoEb1qD+jTwJ9DCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==\""
+              }
+            ]
+          }
+        ]
+      }
+    ],
+    "info": "",
+    "gas_wanted": 2000000,
+    "gas_used": 156514,
+    "tx": null,
+    "timestamp": "",
+    "events": [
+      {
+        "type": "tx",
+        "attributes": [
+          { "key": "ZmVl", "value": null, "index": true },
+          {
+            "key": "ZmVlX3BheWVy",
+            "value": "d29ybWhvbGUxY3l5enB4cGx4ZHprZWVhN2t3c3lkYWRnODczNTdxbmEzemczdHE=",
+            "index": true
+          }
+        ]
+      },
+      {
+        "type": "tx",
+        "attributes": [
+          {
+            "key": "YWNjX3NlcQ==",
+            "value": "d29ybWhvbGUxY3l5enB4cGx4ZHprZWVhN2t3c3lkYWRnODczNTdxbmEzemczdHEvMjU=",
+            "index": true
+          }
+        ]
+      },
+      {
+        "type": "tx",
+        "attributes": [
+          {
+            "key": "c2lnbmF0dXJl",
+            "value": "R09qWUJ2RVVTclY0THQydWt3NURwRXU3Rlo1RURCMzRZUmdwYkhQYitmMEFKSjNFZ3RFZEJRaGV1dHdZVk90eU1VWUlpSkVpZytDeFV0WG8xemI1WEE9PQ==",
+            "index": true
+          }
+        ]
+      },
+      {
+        "type": "message",
+        "attributes": [
+          {
+            "key": "YWN0aW9u",
+            "value": "L2Nvc213YXNtLndhc20udjEuTXNnRXhlY3V0ZUNvbnRyYWN0",
+            "index": true
+          }
+        ]
+      },
+      {
+        "type": "message",
+        "attributes": [
+          { "key": "bW9kdWxl", "value": "d2FzbQ==", "index": true },
+          {
+            "key": "c2VuZGVy",
+            "value": "d29ybWhvbGUxY3l5enB4cGx4ZHprZWVhN2t3c3lkYWRnODczNTdxbmEzemczdHE=",
+            "index": true
+          }
+        ]
+      },
+      {
+        "type": "execute",
+        "attributes": [
+          {
+            "key": "X2NvbnRyYWN0X2FkZHJlc3M=",
+            "value": "d29ybWhvbGUxNGhqMnRhdnE4ZnBlc2R3eHhjdTQ0cnR5M2hoOTB2aHVqcnZjbXN0bDR6cjN0eG1mdnc5c3JyZzQ2NQ==",
+            "index": true
+          }
+        ]
+      },
+      {
+        "type": "wasm",
+        "attributes": [
+          {
+            "key": "X2NvbnRyYWN0X2FkZHJlc3M=",
+            "value": "d29ybWhvbGUxNGhqMnRhdnE4ZnBlc2R3eHhjdTQ0cnR5M2hoOTB2aHVqcnZjbXN0bDR6cjN0eG1mdnc5c3JyZzQ2NQ==",
+            "index": true
+          },
+          {
+            "key": "YWN0aW9u",
+            "value": "c3VibWl0X29ic2VydmF0aW9ucw==",
+            "index": true
+          },
+          {
+            "key": "b3duZXI=",
+            "value": "d29ybWhvbGUxY3l5enB4cGx4ZHprZWVhN2t3c3lkYWRnODczNTdxbmEzemczdHE=",
+            "index": true
+          }
+        ]
+      },
+      {
+        "type": "wasm-Observation",
+        "attributes": [
+          {
+            "key": "X2NvbnRyYWN0X2FkZHJlc3M=",
+            "value": "d29ybWhvbGUxNGhqMnRhdnE4ZnBlc2R3eHhjdTQ0cnR5M2hoOTB2aHVqcnZjbXN0bDR6cjN0eG1mdnc5c3JyZzQ2NQ==",
+            "index": true
+          },
+          {
+            "key": "dHhfaGFzaA==",
+            "value": "Imd1b2xOc1hSWnhnd3kwa1NENVJIbmpTMVJaYW8zVGFmdkNabVpucDJYMHM9Ig==",
+            "index": true
+          },
+          { "key": "dGltZXN0YW1w", "value": "MTY4MzEzNjI0NA==", "index": true },
+          { "key": "bm9uY2U=", "value": "MA==", "index": true },
+          { "key": "ZW1pdHRlcl9jaGFpbg==", "value": "Mg==", "index": true },
+          {
+            "key": "ZW1pdHRlcl9hZGRyZXNz",
+            "value": "IjAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAyOTBmYjE2NzIwOGFmNDU1YmIxMzc3ODAxNjNiN2I3YTlhMTBjMTYi",
+            "index": true
+          },
+          { "key": "c2VxdWVuY2U=", "value": "MTY4MzEzNjI0NA==", "index": true },
+          { "key": "Y29uc2lzdGVuY3lfbGV2ZWw=", "value": "MTU=", "index": true },
+          {
+            "key": "cGF5bG9hZA==",
+            "value": "IkFRQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUEzZ3RyT25aQUFBQUFBQUFBQUFBQUFBQUFBQUxZdm12d3VxZE9DcEJ3Rm1lY3JwR1E2QTNRb0FBZ0FBQUFBQUFBQUFBQUFBQU1FSUlKZy9NMFZzNTc2em9FYjFxRCtqVHdKOURDQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUE9PSI=",
+            "index": true
+          }
+        ]
+      }
+    ]
+  }
+}
+	`
+
+	return []byte(respJson)
+}
```

### node/pkg/accountant/submit_obs.go
```diff
@@ -11,7 +11,6 @@ import (
 	"time"
 
 	"github.com/certusone/wormhole/node/pkg/common"
-	"github.com/certusone/wormhole/node/pkg/wormconn"
 	"github.com/wormhole-foundation/wormhole/sdk/vaa"
 
 	ethCrypto "github.com/ethereum/go-ethereum/crypto"
@@ -296,7 +295,7 @@ func SubmitObservationsToContract(
 	gk *ecdsa.PrivateKey,
 	gsIndex uint32,
 	guardianIndex uint32,
-	wormchainConn *wormconn.ClientConn,
+	wormchainConn AccountantWormchainConn,
 	contract string,
 	msgs []*common.MessagePublication,
 ) (*sdktx.BroadcastTxResponse, error) {
```
