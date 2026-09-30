# [?] fix(net/nat): data race problem of `extAddr` (#3140)

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2025-01-17
Source: https://github.com/libp2p/go-libp2p/commit/613f5a7e5bd5cb5b3f14668ee36d740ef47c292c
Type: security-commit

## Details
fix(net/nat): data race problem of `extAddr` (#3140)

Co-authored-by: Marco Munizaga <git@marcopolo.io>

## Patch
### p2p/net/nat/nat.go
```diff
@@ -6,6 +6,7 @@ import (
 	"fmt"
 	"net/netip"
 	"sync"
+	"sync/atomic"
 	"time"
 
 	logging "github.com/ipfs/go-log/v2"
@@ -56,11 +57,11 @@ func DiscoverNAT(ctx context.Context) (*NAT, error) {
 	ctx, cancel := context.WithCancel(context.Background())
 	nat := &NAT{
 		nat:       natInstance,
-		extAddr:   extAddr,
 		mappings:  make(map[entry]int),
 		ctx:       ctx,
 		ctxCancel: cancel,
 	}
+	nat.extAddr.Store(&extAddr)
 	nat.refCount.Add(1)
 	go func() {
 		defer nat.refCount.Done()
@@ -77,7 +78,7 @@ type NAT struct {
 	natmu sync.Mutex
 	nat   nat.NAT
 	// External IP of the NAT. Will be renewed periodically (every CacheTime).
-	extAddr netip.Addr
+	extAddr atomic.Pointer[netip.Addr]
 
 	refCount  sync.WaitGroup
 	ctx       context.Context
@@ -103,15 +104,15 @@ func (nat *NAT) GetMapping(protocol string, port int) (addr netip.AddrPort, foun
 	nat.mappingmu.Lock()
 	defer nat.mappingmu.Unlock()
 
-	if !nat.extAddr.IsValid() {
+	if !nat.extAddr.Load().IsValid() {
 		return netip.AddrPort{}, false
 	}
 	extPort, found := nat.mappings[entry{protocol: protocol, port: port}]
 	// The mapping may have an invalid port.
 	if !found || extPort == 0 {
 		return netip.AddrPort{}, false
 	}
-	return netip.AddrPortFrom(nat.extAddr, uint16(extPort)), true
+	return netip.AddrPortFrom(*nat.extAddr.Load(), uint16(extPort)), true
 }
 
 // AddMapping attempts to construct a mapping on protocol and internal port.
@@ -206,7 +207,7 @@ func (nat *NAT) background() {
 				if err == nil {
 					extAddr, _ = netip.AddrFromSlice(extIP)
 				}
-				nat.extAddr = extAddr
+				nat.extAddr.Store(&extAddr)
 				nextAddrUpdate = time.Now().Add(CacheTime)
 			}
 			t.Reset(time.Until(minTime(nextAddrUpdate, nextMappingUpdate)))
```
