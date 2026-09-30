# [?] les, tests: fix vflux fuzzer by removing unnecessary panic (#24537)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2022-03-16
Source: https://github.com/ethereum/go-ethereum/commit/7a80cf6543330c73c4fe1c1dc9ca6872e7325d0f
Type: security-commit

## Details
les, tests: fix vflux fuzzer by removing unnecessary panic (#24537)

## Patch
### les/vflux/server/clientpool.go
```diff
@@ -34,7 +34,7 @@ import (
 var (
 	ErrNotConnected    = errors.New("client not connected")
 	ErrNoPriority      = errors.New("priority too low to raise capacity")
-	ErrCantFindMaximum = errors.New("Unable to find maximum allowed capacity")
+	ErrCantFindMaximum = errors.New("unable to find maximum allowed capacity")
 )
 
 // ClientPool implements a client database that assigns a priority to each client
@@ -177,7 +177,7 @@ func (cp *ClientPool) Unregister(peer clientPeer) {
 	cp.ns.SetField(peer.Node(), cp.setup.clientField, nil)
 }
 
-// setConnectedBias sets the connection bias, which is applied to already connected clients
+// SetConnectedBias sets the connection bias, which is applied to already connected clients
 // So that already connected client won't be kicked out very soon and we can ensure all
 // connected clients can have enough time to request or sync some data.
 func (cp *ClientPool) SetConnectedBias(bias time.Duration) {
```

### tests/fuzzers/vflux/clientpool-fuzzer.go
```diff
@@ -267,9 +267,7 @@ func FuzzClientPool(input []byte) int {
 				bias      = f.randomDelay()
 				requested = f.randomBool()
 			)
-			if _, err := pool.SetCapacity(f.peers[index].node, reqCap, bias, requested); err == vfs.ErrCantFindMaximum {
-				panic(nil)
-			}
+			pool.SetCapacity(f.peers[index].node, reqCap, bias, requested)
 			doLog("Set capacity", "id", f.peers[index].node.ID(), "reqcap", reqCap, "bias", bias, "requested", requested)
 		case 7:
 			index := f.randomByte()
```
