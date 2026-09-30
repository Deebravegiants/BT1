# [?] p2p/protocols: fix data race in TestProtocolHook (#19242)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-03-08
Source: https://github.com/celo-org/celo-blockchain/commit/f82185a4a186835e69dbbf2ed6117d116757da34
Type: security-commit

## Details
p2p/protocols: fix data race in TestProtocolHook (#19242)

dummyHook's fields were concurrently written by nodes and read by
the test. The simplest solution is to protect all fields with a mutex.

Enable: TestMultiplePeersDropSelf, TestMultiplePeersDropOther as they
seemingly accidentally stayed disabled during a refactor/rewrite
since 1836366ac19e30f157570e61342fae53bc6c8a57.

resolves ethersphere/go-ethereum#1286

## Patch
### p2p/protocols/accounting_simulation_test.go
```diff
@@ -161,7 +161,7 @@ func TestAccountingSimulation(t *testing.T) {
 type matrix struct {
 	n    int     //number of nodes
 	m    []int64 //array of balances
-	lock sync.RWMutex
+	lock sync.Mutex
 }
 
 // create a new matrix
```

### p2p/protocols/protocol_test.go
```diff
@@ -21,6 +21,7 @@ import (
 	"context"
 	"errors"
 	"fmt"
+	"sync"
 	"testing"
 	"time"
 
@@ -172,8 +173,11 @@ func protoHandshakeExchange(id enode.ID, proto *protoHandshake) []p2ptest.Exchan
 }
 
 func runProtoHandshake(t *testing.T, proto *protoHandshake, errs ...error) {
+	t.Helper()
 	pp := p2ptest.NewTestPeerPool()
 	s := protocolTester(pp)
+	defer s.Stop()
+
 	// TODO: make this more than one handshake
 	node := s.Nodes[0]
 	if err := s.TestExchanges(protoHandshakeExchange(node.ID(), proto)...); err != nil {
@@ -195,13 +199,17 @@ type dummyHook struct {
 	send  bool
 	err   error
 	waitC chan struct{}
+	mu    sync.Mutex
 }
 
 type dummyMsg struct {
 	Content string
 }
 
 func (d *dummyHook) Send(peer *Peer, size uint32, msg interface{}) error {
+	d.mu.Lock()
+	defer d.mu.Unlock()
+
 	d.peer = peer
 	d.size = size
 	d.msg = msg
@@ -210,6 +218,9 @@ func (d *dummyHook) Send(peer *Peer, size uint32, msg interface{}) error {
 }
 
 func (d *dummyHook) Receive(peer *Peer, size uint32, msg interface{}) error {
+	d.mu.Lock()
+	defer d.mu.Unlock()
+
 	d.peer = peer
 	d.size = size
 	d.msg = msg
@@ -263,6 +274,7 @@ func TestProtocolHook(t *testing.T) {
 	if err != nil {
 		t.Fatal(err)
 	}
+	testHook.mu.Lock()
 	if testHook.msg == nil || testHook.msg.(*dummyMsg).Content != "handshake" {
 		t.Fatal("Expected msg to be set, but it is not")
 	}
@@ -278,6 +290,7 @@ func TestProtocolHook(t *testing.T) {
 	if testHook.size != 11 { //11 is the length of the encoded message
 		t.Fatalf("Expected size to be %d, but it is %d ", 1, testHook.size)
 	}
+	testHook.mu.Unlock()
 
 	err = tester.TestExchanges(p2ptest.Exchange{
 		Triggers: []p2ptest.Trigger{
@@ -294,6 +307,8 @@ func TestProtocolHook(t *testing.T) {
 	if err != nil {
 		t.Fatal(err)
 	}
+
+	testHook.mu.Lock()
 	if testHook.msg == nil || testHook.msg.(*dummyMsg).Content != "response" {
 		t.Fatal("Expected msg to be set, but it is not")
 	}
@@ -306,6 +321,7 @@ func TestProtocolHook(t *testing.T) {
 	if testHook.size != 10 { //11 is the length of the encoded message
 		t.Fatalf("Expected size to be %d, but it is %d ", 1, testHook.size)
 	}
+	testHook.mu.Unlock()
 
 	testHook.err = fmt.Errorf("dummy error")
 	err = tester.TestExchanges(p2ptest.Exchange{
@@ -325,7 +341,6 @@ func TestProtocolHook(t *testing.T) {
 	if err != nil {
 		t.Fatalf("Expected a specific disconnect error, but got different one: %v", err)
 	}
-
 }
 
 //We need to test that if the hook is not defined, then message infrastructure
@@ -342,16 +357,19 @@ func TestNoHook(t *testing.T) {
 	ctx := context.TODO()
 	msg := &perBytesMsgSenderPays{Content: "testBalance"}
 	//send a message
-	err := peer.Send(ctx, msg)
-	if err != nil {
+
+	if err := peer.Send(ctx, msg); err != nil {
 		t.Fatal(err)
 	}
 	//simulate receiving a message
 	rw.msg = msg
-	peer.handleIncoming(func(ctx context.Context, msg interface{}) error {
+	handler := func(ctx context.Context, msg interface{}) error {
 		return nil
-	})
-	//all should just work and not result in any error
+	}
+
+	if err := peer.handleIncoming(handler); err != nil {
+		t.Fatal(err)
+	}
 }
 
 func TestProtoHandshakeVersionMismatch(t *testing.T) {
@@ -391,8 +409,11 @@ func moduleHandshakeExchange(id enode.ID, resp uint) []p2ptest.Exchange {
 }
 
 func runModuleHandshake(t *testing.T, resp uint, errs ...error) {
+	t.Helper()
 	pp := p2ptest.NewTestPeerPool()
 	s := protocolTester(pp)
+	defer s.Stop()
+
 	node := s.Nodes[0]
 	if err := s.TestExchanges(protoHandshakeExchange(node.ID(), &protoHandshake{42, "420"})...); err != nil {
 		t.Fatal(err)
@@ -471,8 +492,10 @@ func testMultiPeerSetup(a, b enode.ID) []p2ptest.Exchange {
 }
 
 func runMultiplePeers(t *testing.T, peer int, errs ...error) {
+	t.Helper()
 	pp := p2ptest.NewTestPeerPool()
 	s := protocolTester(pp)
+	defer s.Stop()
 
 	if err := s.TestExchanges(testMultiPeerSetup(s.Nodes[0].ID(), s.Nodes[1].ID())...); err != nil {
 		t.Fatal(err)
@@ -542,14 +565,14 @@ WAIT:
 	}
 
 }
-func XTestMultiplePeersDropSelf(t *testing.T) {
+func TestMultiplePeersDropSelf(t *testing.T) {
 	runMultiplePeers(t, 0,
 		fmt.Errorf("subprotocol error"),
 		fmt.Errorf("Message handler error: (msg code 3): dropped"),
 	)
 }
 
-func XTestMultiplePeersDropOther(t *testing.T) {
+func TestMultiplePeersDropOther(t *testing.T) {
 	runMultiplePeers(t, 1,
 		fmt.Errorf("Message handler error: (msg code 3): dropped"),
 		fmt.Errorf("subprotocol error"),
```

### p2p/testing/protocoltester.go
```diff
@@ -51,7 +51,7 @@ type ProtocolTester struct {
 // NewProtocolTester constructs a new ProtocolTester
 // it takes as argument the pivot node id, the number of dummy peers and the
 // protocol run function called on a peer connection by the p2p server
-func NewProtocolTester(id enode.ID, n int, run func(*p2p.Peer, p2p.MsgReadWriter) error) *ProtocolTester {
+func NewProtocolTester(id enode.ID, nodeCount int, run func(*p2p.Peer, p2p.MsgReadWriter) error) *ProtocolTester {
 	services := adapters.Services{
 		"test": func(ctx *adapters.ServiceContext) (node.Service, error) {
 			return &testNode{run}, nil
@@ -74,9 +74,9 @@ func NewProtocolTester(id enode.ID, n int, run func(*p2p.Peer, p2p.MsgReadWriter
 	}
 
 	node := net.GetNode(id).Node.(*adapters.SimNode)
-	peers := make([]*adapters.NodeConfig, n)
-	nodes := make([]*enode.Node, n)
-	for i := 0; i < n; i++ {
+	peers := make([]*adapters.NodeConfig, nodeCount)
+	nodes := make([]*enode.Node, nodeCount)
+	for i := 0; i < nodeCount; i++ {
 		peers[i] = adapters.RandomNodeConfig()
 		peers[i].Services = []string{"mock"}
 		nodes[i] = peers[i].Node()
@@ -100,9 +100,8 @@ func NewProtocolTester(id enode.ID, n int, run func(*p2p.Peer, p2p.MsgReadWriter
 }
 
 // Stop stops the p2p server
-func (t *ProtocolTester) Stop() error {
+func (t *ProtocolTester) Stop() {
 	t.Server.Stop()
-	return nil
 }
 
 // Connect brings up the remote peer node and connects it using the
```
