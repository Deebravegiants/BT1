# [?] swarm/network/stream: fix DoS invalid hash length (#927)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2018-09-21
Source: https://github.com/celo-org/celo-blockchain/commit/d3f056bd68fb6a8e9ffa3938d5404c6a209e0313
Type: security-commit

## Details
swarm/network/stream: fix DoS invalid hash length (#927)

## Patch
### swarm/network/stream/messages.go
```diff
@@ -26,7 +26,7 @@ import (
 	bv "github.com/ethereum/go-ethereum/swarm/network/bitvector"
 	"github.com/ethereum/go-ethereum/swarm/spancontext"
 	"github.com/ethereum/go-ethereum/swarm/storage"
-	opentracing "github.com/opentracing/opentracing-go"
+	"github.com/opentracing/opentracing-go"
 )
 
 var syncBatchTimeout = 30 * time.Second
@@ -195,18 +195,24 @@ func (p *Peer) handleOfferedHashesMsg(ctx context.Context, req *OfferedHashesMsg
 	if err != nil {
 		return err
 	}
+
 	hashes := req.Hashes
-	want, err := bv.New(len(hashes) / HashSize)
+	lenHashes := len(hashes)
+	if lenHashes%HashSize != 0 {
+		return fmt.Errorf("error invalid hashes length (len: %v)", lenHashes)
+	}
+
+	want, err := bv.New(lenHashes / HashSize)
 	if err != nil {
-		return fmt.Errorf("error initiaising bitvector of length %v: %v", len(hashes)/HashSize, err)
+		return fmt.Errorf("error initiaising bitvector of length %v: %v", lenHashes/HashSize, err)
 	}
 
 	ctr := 0
 	errC := make(chan error)
 	ctx, cancel := context.WithTimeout(ctx, syncBatchTimeout)
 
 	ctx = context.WithValue(ctx, "source", p.ID().String())
-	for i := 0; i < len(hashes); i += HashSize {
+	for i := 0; i < lenHashes; i += HashSize {
 		hash := hashes[i : i+HashSize]
 
 		if wait := c.NeedData(ctx, hash); wait != nil {
```

### swarm/network/stream/streamer_test.go
```diff
@@ -19,6 +19,7 @@ package stream
 import (
 	"bytes"
 	"context"
+	"errors"
 	"testing"
 	"time"
 
@@ -55,11 +56,12 @@ func TestStreamerRequestSubscription(t *testing.T) {
 }
 
 var (
-	hash0     = sha3.Sum256([]byte{0})
-	hash1     = sha3.Sum256([]byte{1})
-	hash2     = sha3.Sum256([]byte{2})
-	hashesTmp = append(hash0[:], hash1[:]...)
-	hashes    = append(hashesTmp, hash2[:]...)
+	hash0         = sha3.Sum256([]byte{0})
+	hash1         = sha3.Sum256([]byte{1})
+	hash2         = sha3.Sum256([]byte{2})
+	hashesTmp     = append(hash0[:], hash1[:]...)
+	hashes        = append(hashesTmp, hash2[:]...)
+	corruptHashes = append(hashes[:40])
 )
 
 type testClient struct {
@@ -459,6 +461,71 @@ func TestStreamerUpstreamSubscribeLiveAndHistory(t *testing.T) {
 	}
 }
 
+func TestStreamerDownstreamCorruptHashesMsgExchange(t *testing.T) {
+	tester, streamer, _, teardown, err := newStreamerTester(t)
+	defer teardown()
+	if err != nil {
+		t.Fatal(err)
+	}
+
+	stream := NewStream("foo", "", true)
+
+	var tc *testClient
+
+	streamer.RegisterClientFunc("foo", func(p *Peer, t string, live bool) (Client, error) {
+		tc = newTestClient(t)
+		return tc, nil
+	})
+
+	peerID := tester.IDs[0]
+
+	err = streamer.Subscribe(peerID, stream, NewRange(5, 8), Top)
+	if err != nil {
+		t.Fatalf("Expected no error, got %v", err)
+	}
+
+	err = tester.TestExchanges(p2ptest.Exchange{
+		Label: "Subscribe message",
+		Expects: []p2ptest.Expect{
+			{
+				Code: 4,
+				Msg: &SubscribeMsg{
+					Stream:   stream,
+					History:  NewRange(5, 8),
+					Priority: Top,
+				},
+				Peer: peerID,
+			},
+		},
+	},
+		p2ptest.Exchange{
+			Label: "Corrupt offered hash message",
+			Triggers: []p2ptest.Trigger{
+				{
+					Code: 1,
+					Msg: &OfferedHashesMsg{
+						HandoverProof: &HandoverProof{
+							Handover: &Handover{},
+						},
+						Hashes: corruptHashes,
+						From:   5,
+						To:     8,
+						Stream: stream,
+					},
+					Peer: peerID,
+				},
+			},
+		})
+	if err != nil {
+		t.Fatal(err)
+	}
+
+	expectedError := errors.New("Message handler error: (msg code 1): error invalid hashes length (len: 40)")
+	if err := tester.TestDisconnected(&p2ptest.Disconnect{Peer: tester.IDs[0], Error: expectedError}); err != nil {
+		t.Fatal(err)
+	}
+}
+
 func TestStreamerDownstreamOfferedHashesMsgExchange(t *testing.T) {
 	tester, streamer, _, teardown, err := newStreamerTester(t)
 	defer teardown()
```
