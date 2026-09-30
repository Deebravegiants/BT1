# [?] swarm/network: fix data race warning on TestBzzHandshakeLightNode (#18459)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-01-17
Source: https://github.com/celo-org/celo-blockchain/commit/81e26d5a4837077d5fff17e7b461061b134a4a00
Type: security-commit

## Details
swarm/network: fix data race warning on TestBzzHandshakeLightNode (#18459)

## Patch
### swarm/network/protocol.go
```diff
@@ -168,7 +168,7 @@ func (b *Bzz) APIs() []rpc.API {
 func (b *Bzz) RunProtocol(spec *protocols.Spec, run func(*BzzPeer) error) func(*p2p.Peer, p2p.MsgReadWriter) error {
 	return func(p *p2p.Peer, rw p2p.MsgReadWriter) error {
 		// wait for the bzz protocol to perform the handshake
-		handshake, _ := b.GetHandshake(p.ID())
+		handshake, _ := b.GetOrCreateHandshake(p.ID())
 		defer b.removeHandshake(p.ID())
 		select {
 		case <-handshake.done:
@@ -213,7 +213,7 @@ func (b *Bzz) performHandshake(p *protocols.Peer, handshake *HandshakeMsg) error
 // runBzz is the p2p protocol run function for the bzz base protocol
 // that negotiates the bzz handshake
 func (b *Bzz) runBzz(p *p2p.Peer, rw p2p.MsgReadWriter) error {
-	handshake, _ := b.GetHandshake(p.ID())
+	handshake, _ := b.GetOrCreateHandshake(p.ID())
 	if !<-handshake.init {
 		return fmt.Errorf("%08x: bzz already started on peer %08x", b.localAddr.Over()[:4], p.ID().Bytes()[:4])
 	}
@@ -303,7 +303,7 @@ func (b *Bzz) removeHandshake(peerID enode.ID) {
 }
 
 // GetHandshake returns the bzz handhake that the remote peer with peerID sent
-func (b *Bzz) GetHandshake(peerID enode.ID) (*HandshakeMsg, bool) {
+func (b *Bzz) GetOrCreateHandshake(peerID enode.ID) (*HandshakeMsg, bool) {
 	b.mtx.Lock()
 	defer b.mtx.Unlock()
 	handshake, found := b.handshakes[peerID]
```

### swarm/network/protocol_test.go
```diff
@@ -21,6 +21,7 @@ import (
 	"fmt"
 	"os"
 	"testing"
+	"time"
 
 	"github.com/ethereum/go-ethereum/log"
 	"github.com/ethereum/go-ethereum/p2p"
@@ -224,7 +225,7 @@ func TestBzzHandshakeLightNode(t *testing.T) {
 	for _, test := range lightNodeTests {
 		t.Run(test.name, func(t *testing.T) {
 			randomAddr := RandomAddr()
-			pt := newBzzHandshakeTester(t, 1, randomAddr, false)
+			pt := newBzzHandshakeTester(nil, 1, randomAddr, false) // TODO change signature - t is not used anywhere
 			node := pt.Nodes[0]
 			addr := NewAddr(node)
 
@@ -237,8 +238,14 @@ func TestBzzHandshakeLightNode(t *testing.T) {
 				t.Fatal(err)
 			}
 
-			if pt.bzz.handshakes[node.ID()].LightNode != test.lightNode {
-				t.Fatalf("peer LightNode flag is %v, should be %v", pt.bzz.handshakes[node.ID()].LightNode, test.lightNode)
+			select {
+
+			case <-pt.bzz.handshakes[node.ID()].done:
+				if pt.bzz.handshakes[node.ID()].LightNode != test.lightNode {
+					t.Fatalf("peer LightNode flag is %v, should be %v", pt.bzz.handshakes[node.ID()].LightNode, test.lightNode)
+				}
+			case <-time.After(10 * time.Second):
+				t.Fatal("test timeout")
 			}
 		})
 	}
```
