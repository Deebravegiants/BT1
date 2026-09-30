# [?] server: add addressesMtx to fix race condition

## Summary
Severity: Unknown
Chain: Bitcoin
Component: btcsuite/btcd
Published: 2019-11-09
Source: https://github.com/btcsuite/btcd/commit/c2ca0a408e09db7f46b760c3cb8a280ede58d54a
Type: security-commit

## Details
server: add addressesMtx to fix race condition

## Patch
### server.go
```diff
@@ -273,6 +273,7 @@ type serverPeer struct {
 	sentAddrs      bool
 	isWhitelisted  bool
 	filter         *bloom.Filter
+	addressesMtx   sync.RWMutex
 	knownAddresses map[string]struct{}
 	banScore       connmgr.DynamicBanScore
 	quit           chan struct{}
@@ -305,14 +306,18 @@ func (sp *serverPeer) newestBlock() (*chainhash.Hash, int32, error) {
 // addKnownAddresses adds the given addresses to the set of known addresses to
 // the peer to prevent sending duplicate addresses.
 func (sp *serverPeer) addKnownAddresses(addresses []*wire.NetAddress) {
+	sp.addressesMtx.Lock()
 	for _, na := range addresses {
 		sp.knownAddresses[addrmgr.NetAddressKey(na)] = struct{}{}
 	}
+	sp.addressesMtx.Unlock()
 }
 
 // addressKnown true if the given address is already known to the peer.
 func (sp *serverPeer) addressKnown(na *wire.NetAddress) bool {
+	sp.addressesMtx.RLock()
 	_, exists := sp.knownAddresses[addrmgr.NetAddressKey(na)]
+	sp.addressesMtx.RUnlock()
 	return exists
 }
 
```
