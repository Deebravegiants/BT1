# [?] fix: a deadlock caused by bsc protocol handeshake timeout (#1484)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2023-04-19
Source: https://github.com/bnb-chain/bsc/commit/2db1088cced0729419348e9f519a534daaee4b00
Type: security-commit

## Details
fix: a deadlock caused by bsc protocol handeshake timeout (#1484)

## Patch
### eth/handler_bsc.go
```diff
@@ -27,7 +27,7 @@ func (h *bscHandler) RunPeer(peer *bsc.Peer, hand bsc.Handler) error {
 		ps.lock.Lock()
 		if wait, ok := ps.bscWait[id]; ok {
 			delete(ps.bscWait, id)
-			wait <- peer
+			wait <- nil
 		}
 		ps.lock.Unlock()
 		return err
```

### eth/peerset.go
```diff
@@ -70,6 +70,7 @@ const (
 	// extensionWaitTimeout is the maximum allowed time for the extension wait to
 	// complete before dropping the connection as malicious.
 	extensionWaitTimeout = 10 * time.Second
+	tryWaitTimeout       = 100 * time.Millisecond
 )
 
 // peerSet represents the collection of active peers currently participating in
@@ -402,10 +403,26 @@ func (ps *peerSet) waitBscExtension(peer *eth.Peer) (*bsc.Peer, error) {
 		return peer, nil
 
 	case <-time.After(extensionWaitTimeout):
-		ps.lock.Lock()
-		delete(ps.bscWait, id)
-		ps.lock.Unlock()
-		return nil, errPeerWaitTimeout
+		// could be deadlock, so we use TryLock to avoid it.
+		if ps.lock.TryLock() {
+			delete(ps.bscWait, id)
+			ps.lock.Unlock()
+			return nil, errPeerWaitTimeout
+		}
+		// if TryLock failed, we wait for a while and try again.
+		for {
+			select {
+			case <-wait:
+				// discard the peer, even though the peer arrived.
+				return nil, errPeerWaitTimeout
+			case <-time.After(tryWaitTimeout):
+				if ps.lock.TryLock() {
+					delete(ps.bscWait, id)
+					ps.lock.Unlock()
+					return nil, errPeerWaitTimeout
+				}
+			}
+		}
 	}
 }
 
```

### p2p/peer.go
```diff
@@ -435,7 +435,7 @@ func (p *Peer) startProtocols(writeStart <-chan struct{}, writeErr chan<- error)
 				p.log.Trace(fmt.Sprintf("Protocol %s/%d returned", proto.Name, proto.Version))
 				err = errProtocolReturned
 			} else if !errors.Is(err, io.EOF) {
-				p.log.Trace(fmt.Sprintf("Protocol %s/%d failed", proto.Name, proto.Version), "err", err)
+				p.log.Warn(fmt.Sprintf("Protocol %s/%d failed", proto.Name, proto.Version), "err", err)
 			}
 			p.protoErr <- err
 		}()
```
