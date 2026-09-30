# [?] p2p/simulations: fix data race on swarm/network/simulations (#18464)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-01-22
Source: https://github.com/celo-org/celo-blockchain/commit/85a79b3ad3c5863f8612d25c246bcfad339f36b7
Type: security-commit

## Details
p2p/simulations: fix data race on swarm/network/simulations (#18464)

## Patch
### p2p/simulations/network.go
```diff
@@ -168,24 +168,28 @@ func (net *Network) Start(id enode.ID) error {
 // snapshots
 func (net *Network) startWithSnapshots(id enode.ID, snapshots map[string][]byte) error {
 	net.lock.Lock()
-	defer net.lock.Unlock()
 
 	node := net.getNode(id)
 	if node == nil {
+		net.lock.Unlock()
 		return fmt.Errorf("node %v does not exist", id)
 	}
 	if node.Up {
+		net.lock.Unlock()
 		return fmt.Errorf("node %v already up", id)
 	}
 	log.Trace("Starting node", "id", id, "adapter", net.nodeAdapter.Name())
 	if err := node.Start(snapshots); err != nil {
+		net.lock.Unlock()
 		log.Warn("Node startup failed", "id", id, "err", err)
 		return err
 	}
 	node.Up = true
 	log.Info("Started node", "id", id)
+	ev := NewEvent(node)
+	net.lock.Unlock()
 
-	net.events.Send(NewEvent(node))
+	net.events.Send(ev)
 
 	// subscribe to peer events
 	client, err := node.Client()
@@ -210,12 +214,14 @@ func (net *Network) watchPeerEvents(id enode.ID, events chan *p2p.PeerEvent, sub
 		// assume the node is now down
 		net.lock.Lock()
 		defer net.lock.Unlock()
+
 		node := net.getNode(id)
 		if node == nil {
 			return
 		}
 		node.Up = false
-		net.events.Send(NewEvent(node))
+		ev := NewEvent(node)
+		net.events.Send(ev)
 	}()
 	for {
 		select {
@@ -254,9 +260,11 @@ func (net *Network) Stop(id enode.ID) error {
 	net.lock.Lock()
 	node := net.getNode(id)
 	if node == nil {
+		net.lock.Unlock()
 		return fmt.Errorf("node %v does not exist", id)
 	}
 	if !node.Up {
+		net.lock.Unlock()
 		return fmt.Errorf("node %v already down", id)
 	}
 	node.Up = false
@@ -270,7 +278,10 @@ func (net *Network) Stop(id enode.ID) error {
 		return err
 	}
 	log.Info("Stopped node", "id", id, "err", err)
-	net.events.Send(ControlEvent(node))
+	net.lock.Lock()
+	ev := ControlEvent(node)
+	net.lock.Unlock()
+	net.events.Send(ev)
 	return nil
 }
 
```
