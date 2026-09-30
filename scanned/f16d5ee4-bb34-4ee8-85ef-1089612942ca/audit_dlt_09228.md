# [?] fix(peering): fix a race condition

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2020-05-26
Source: https://github.com/ipfs/kubo/commit/87a293f6801b176d9a947c3bf49c511e3dd98dce
Type: security-commit

## Details
fix(peering): fix a race condition

## Patch
### peering/peering.go
```diff
@@ -47,6 +47,24 @@ type peerHandler struct {
 	nextDelay time.Duration
 }
 
+// setAddrs sets the addresses for this peer.
+func (ph *peerHandler) setAddrs(addrs []multiaddr.Multiaddr) {
+	// Not strictly necessary, but it helps to not trust the calling code.
+	addrCopy := make([]multiaddr.Multiaddr, len(addrs))
+	copy(addrCopy, addrs)
+
+	ph.mu.Lock()
+	defer ph.mu.Unlock()
+	ph.addrs = addrCopy
+}
+
+// getAddrs returns a shared slice of addresses for this peer. Do not modify.
+func (ph *peerHandler) getAddrs() []multiaddr.Multiaddr {
+	ph.mu.Lock()
+	defer ph.mu.Unlock()
+	return ph.addrs
+}
+
 // stop permanently stops the peer handler.
 func (ph *peerHandler) stop() {
 	ph.cancel()
@@ -69,11 +87,7 @@ func (ph *peerHandler) nextBackoff() time.Duration {
 
 func (ph *peerHandler) reconnect() {
 	// Try connecting
-
-	ph.mu.Lock()
-	addrs := append(([]multiaddr.Multiaddr)(nil), ph.addrs...)
-	ph.mu.Unlock()
-
+	addrs := ph.getAddrs()
 	logger.Debugw("reconnecting", "peer", ph.peer, "addrs", addrs)
 
 	err := ph.host.Connect(ph.ctx, peer.AddrInfo{ID: ph.peer, Addrs: addrs})
@@ -193,7 +207,7 @@ func (ps *PeeringService) AddPeer(info peer.AddrInfo) {
 
 	if handler, ok := ps.peers[info.ID]; ok {
 		logger.Infow("updating addresses", "peer", info.ID, "addrs", info.Addrs)
-		handler.addrs = info.Addrs
+		handler.setAddrs(info.Addrs)
 	} else {
 		logger.Infow("peer added", "peer", info.ID, "addrs", info.Addrs)
 		ps.host.ConnManager().Protect(info.ID, connmgrTag)
```
