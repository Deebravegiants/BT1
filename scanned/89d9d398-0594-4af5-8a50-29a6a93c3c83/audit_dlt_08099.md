# [?] multi: fix deadlock in p2p race condition

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2025-06-22
Source: https://github.com/lightningnetwork/lnd/commit/3329308bce06723103a597b602953cb9e4fe558e
Type: security-commit

## Details
multi: fix deadlock in p2p race condition

In case we cannot guarantee that the peers has started up
completely we launch the disconnect method asynchronously.

## Patch
### peer/brontide.go
```diff
@@ -1591,6 +1591,10 @@ func (p *Brontide) WaitForDisconnect(ready chan struct{}) {
 // Disconnect terminates the connection with the remote peer. Additionally, a
 // signal is sent to the server and htlcSwitch indicating the resources
 // allocated to the peer can now be cleaned up.
+//
+// NOTE: Be aware that this method will block if the peer is still starting up.
+// Therefore consider starting it in a goroutine if you cannot guarantee that
+// the peer has finished starting up before calling this method.
 func (p *Brontide) Disconnect(reason error) {
 	if !atomic.CompareAndSwapInt32(&p.disconnect, 0, 1) {
 		return
@@ -1603,7 +1607,8 @@ func (p *Brontide) Disconnect(reason error) {
 	// started, otherwise we will skip reading it as this chan won't be
 	// closed, hence blocks forever.
 	if atomic.LoadInt32(&p.started) == 1 {
-		p.log.Debugf("Started, waiting on startReady signal")
+		p.log.Debugf("Peer hasn't finished starting up yet, waiting " +
+			"on startReady signal before closing connection")
 
 		select {
 		case <-p.startReady:
```

### server.go
```diff
@@ -4941,27 +4941,22 @@ func (s *server) connectToPersistentPeer(pubKeyStr string) {
 
 // removePeer removes the passed peer from the server's state of all active
 // peers.
+//
+// NOTE: Server mutex must be held when calling this function.
 func (s *server) removePeer(p *peer.Brontide) {
 	if p == nil {
 		return
 	}
 
-	srvrLog.Debugf("removing peer %v", p)
-
-	// As the peer is now finished, ensure that the TCP connection is
-	// closed and all of its related goroutines have exited.
-	p.Disconnect(fmt.Errorf("server: disconnecting peer %v", p))
-
-	// If this peer had an active persistent connection request, remove it.
-	if p.ConnReq() != nil {
-		s.connMgr.Remove(p.ConnReq().ID())
-	}
+	srvrLog.Debugf("Removing peer %v", p)
 
-	// Ignore deleting peers if we're shutting down.
+	// Exit early if we have already been instructed to shutdown, the peers
+	// will be disconnected in the server shutdown process.
 	if s.Stopped() {
 		return
 	}
 
+	// Capture the peer's public key and string representation.
 	pKey := p.PubKey()
 	pubSer := pKey[:]
 	pubStr := string(pubSer)
@@ -4974,22 +4969,45 @@ func (s *server) removePeer(p *peer.Brontide) {
 		delete(s.outboundPeers, pubStr)
 	}
 
-	// Remove the peer's access permission from the access manager.
-	peerPubStr := string(p.IdentityKey().SerializeCompressed())
-	s.peerAccessMan.removePeerAccess(peerPubStr)
+	// When removing the peer we make sure to disconnect it asynchronously
+	// to avoid blocking the main server goroutine because it is holding the
+	// server's mutex. Disconnecting the peer might block and wait until the
+	// peer has fully started up. This can happen if an inbound and outbound
+	// race condition occurs.
+	s.wg.Add(1)
+	go func() {
+		defer s.wg.Done()
 
-	// Copy the peer's error buffer across to the server if it has any items
-	// in it so that we can restore peer errors across connections.
-	if p.ErrorBuffer().Total() > 0 {
-		s.peerErrors[pubStr] = p.ErrorBuffer()
-	}
+		p.Disconnect(fmt.Errorf("server: disconnecting peer %v", p))
 
-	// Inform the peer notifier of a peer offline event so that it can be
-	// reported to clients listening for peer events.
-	var pubKey [33]byte
-	copy(pubKey[:], pubSer)
+		// If this peer had an active persistent connection request,
+		// remove it.
+		if p.ConnReq() != nil {
+			s.connMgr.Remove(p.ConnReq().ID())
+		}
+
+		// Remove the peer's access permission from the access manager.
+		peerPubStr := string(p.IdentityKey().SerializeCompressed())
+		s.peerAccessMan.removePeerAccess(peerPubStr)
+
+		// Copy the peer's error buffer across to the server if it has
+		// any items in it so that we can restore peer errors across
+		// connections. We need to look up the error after the peer has
+		// been disconnected because we write the error in the
+		// `Disconnect` method.
+		s.mu.Lock()
+		if p.ErrorBuffer().Total() > 0 {
+			s.peerErrors[pubStr] = p.ErrorBuffer()
+		}
+		s.mu.Unlock()
+
+		// Inform the peer notifier of a peer offline event so that it
+		// can be reported to clients listening for peer events.
+		var pubKey [33]byte
+		copy(pubKey[:], pubSer)
 
-	s.peerNotifier.NotifyPeerOffline(pubKey)
+		s.peerNotifier.NotifyPeerOffline(pubKey)
+	}()
 }
 
 // ConnectToPeer requests that the server connect to a Lightning Network peer
@@ -5130,7 +5148,10 @@ func (s *server) DisconnectPeer(pubKey *btcec.PublicKey) error {
 
 	// Remove the peer by calling Disconnect. Previously this was done with
 	// removePeer, which bypassed the peerTerminationWatcher.
-	peer.Disconnect(fmt.Errorf("server: DisconnectPeer called"))
+	//
+	// NOTE: We call it in a goroutine to avoid blocking the main server
+	// goroutine because we might hold the server's mutex.
+	go peer.Disconnect(fmt.Errorf("server: DisconnectPeer called"))
 
 	return nil
 }
```
