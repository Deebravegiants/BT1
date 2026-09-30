# [?] fix: avoid a close deadlock in the natmanager

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2020-06-22
Source: https://github.com/libp2p/go-libp2p/commit/72770db2f68e57a3bb2a270bc069e162b8899b54
Type: security-commit

## Details
fix: avoid a close deadlock in the natmanager

Before, we would:

1. Receive a "listen close" event from an event handler, after the teardown started.
2. Try to add a child process to handle the event. This would block because we
were in the teardown.
3. In the teardown, try to unregister the event handler and deadlock

I've now:

* Removed the teardown.
* Switched to a single event loop.

Ideally, we'd remove goprocess entirely. But we'd need to refactor natmgr.

fixes #933

## Patch
### p2p/host/basic/natmgr.go
```diff
@@ -41,27 +41,22 @@ type natManager struct {
 	natmu sync.RWMutex
 	nat   *inat.NAT
 
-	ready chan struct{} // closed once the nat is ready to process port mappings
-
-	syncMu sync.Mutex
+	ready    chan struct{} // closed once the nat is ready to process port mappings
+	syncFlag chan struct{}
 
 	proc goprocess.Process // natManager has a process + children. can be closed.
 }
 
 func newNatManager(net network.Network) *natManager {
 	nmgr := &natManager{
-		net:   net,
-		ready: make(chan struct{}),
+		net:      net,
+		ready:    make(chan struct{}),
+		syncFlag: make(chan struct{}, 1),
 	}
 
-	nmgr.proc = goprocess.WithTeardown(func() error {
-		// on closing, unregister from network notifications.
-		net.StopNotify((*nmgrNetNotifiee)(nmgr))
-		return nil
-	})
+	nmgr.proc = goprocess.WithParent(goprocess.Background())
 
-	// discover the nat.
-	nmgr.discoverNAT()
+	nmgr.start()
 	return nmgr
 }
 
@@ -77,7 +72,7 @@ func (nmgr *natManager) Ready() <-chan struct{} {
 	return nmgr.ready
 }
 
-func (nmgr *natManager) discoverNAT() {
+func (nmgr *natManager) start() {
 	nmgr.proc.Go(func(worker goprocess.Process) {
 		// inat.DiscoverNAT blocks until the nat is found or a timeout
 		// is reached. we unfortunately cannot specify timeouts-- the
@@ -111,107 +106,113 @@ func (nmgr *natManager) discoverNAT() {
 		// we need to sign up here to avoid missing some notifs
 		// before the NAT has been found.
 		nmgr.net.Notify((*nmgrNetNotifiee)(nmgr))
-		nmgr.sync()
+		defer nmgr.net.StopNotify((*nmgrNetNotifiee)(nmgr))
+
+		nmgr.doSync() // sync one first.
+		for {
+			select {
+			case <-nmgr.syncFlag:
+				nmgr.doSync() // sync when our listen addresses chnage.
+			case <-worker.Closing():
+				return
+			}
+		}
 	})
 }
 
-// syncs the current NAT mappings, removing any outdated mappings and adding any
-// new mappings.
 func (nmgr *natManager) sync() {
-	nat := nmgr.NAT()
-	if nat == nil {
-		// Nothing to do.
-		return
+	select {
+	case nmgr.syncFlag <- struct{}{}:
+	default:
 	}
+}
 
-	nmgr.proc.Go(func(_ goprocess.Process) {
-		nmgr.syncMu.Lock()
-		defer nmgr.syncMu.Unlock()
-
-		ports := map[string]map[int]bool{
-			"tcp": map[int]bool{},
-			"udp": map[int]bool{},
+// doSync syncs the current NAT mappings, removing any outdated mappings and adding any
+// new mappings.
+func (nmgr *natManager) doSync() {
+	ports := map[string]map[int]bool{
+		"tcp": map[int]bool{},
+		"udp": map[int]bool{},
+	}
+	for _, maddr := range nmgr.net.ListenAddresses() {
+		// Strip the IP
+		maIP, rest := ma.SplitFirst(maddr)
+		if maIP == nil || rest == nil {
+			continue
 		}
-		for _, maddr := range nmgr.net.ListenAddresses() {
-			// Strip the IP
-			maIP, rest := ma.SplitFirst(maddr)
-			if maIP == nil || rest == nil {
-				continue
-			}
 
-			switch maIP.Protocol().Code {
-			case ma.P_IP6, ma.P_IP4:
-			default:
-				continue
-			}
+		switch maIP.Protocol().Code {
+		case ma.P_IP6, ma.P_IP4:
+		default:
+			continue
+		}
 
-			// Only bother if we're listening on a
-			// unicast/unspecified IP.
-			ip := net.IP(maIP.RawValue())
-			if !(ip.IsGlobalUnicast() || ip.IsUnspecified()) {
-				continue
-			}
+		// Only bother if we're listening on a
+		// unicast/unspecified IP.
+		ip := net.IP(maIP.RawValue())
+		if !(ip.IsGlobalUnicast() || ip.IsUnspecified()) {
+			continue
+		}
 
-			// Extract the port/protocol
-			proto, _ := ma.SplitFirst(rest)
-			if proto == nil {
-				continue
-			}
+		// Extract the port/protocol
+		proto, _ := ma.SplitFirst(rest)
+		if proto == nil {
+			continue
+		}
 
-			var protocol string
-			switch proto.Protocol().Code {
-			case ma.P_TCP:
-				protocol = "tcp"
-			case ma.P_UDP:
-				protocol = "udp"
-			default:
-				continue
-			}
+		var protocol string
+		switch proto.Protocol().Code {
+		case ma.P_TCP:
+			protocol = "tcp"
+		case ma.P_UDP:
+			protocol = "udp"
+		default:
+			continue
+		}
 
-			port, err := strconv.ParseUint(proto.Value(), 10, 16)
-			if err != nil {
-				// bug in multiaddr
-				panic(err)
-			}
-			ports[protocol][int(port)] = false
+		port, err := strconv.ParseUint(proto.Value(), 10, 16)
+		if err != nil {
+			// bug in multiaddr
+			panic(err)
 		}
+		ports[protocol][int(port)] = false
+	}
 
-		var wg sync.WaitGroup
-		defer wg.Wait()
-
-		// Close old mappings
-		for _, m := range nat.Mappings() {
-			mappedPort := m.InternalPort()
-			if _, ok := ports[m.Protocol()][mappedPort]; !ok {
-				// No longer need this mapping.
-				wg.Add(1)
-				go func(m inat.Mapping) {
-					defer wg.Done()
-					m.Close()
-				}(m)
-			} else {
-				// already mapped
-				ports[m.Protocol()][mappedPort] = true
-			}
+	var wg sync.WaitGroup
+	defer wg.Wait()
+
+	// Close old mappings
+	for _, m := range nmgr.nat.Mappings() {
+		mappedPort := m.InternalPort()
+		if _, ok := ports[m.Protocol()][mappedPort]; !ok {
+			// No longer need this mapping.
+			wg.Add(1)
+			go func(m inat.Mapping) {
+				defer wg.Done()
+				m.Close()
+			}(m)
+		} else {
+			// already mapped
+			ports[m.Protocol()][mappedPort] = true
 		}
+	}
 
-		// Create new mappings.
-		for proto, pports := range ports {
-			for port, mapped := range pports {
-				if mapped {
-					continue
-				}
-				wg.Add(1)
-				go func(proto string, port int) {
-					defer wg.Done()
-					_, err := nat.NewMapping(proto, port)
-					if err != nil {
-						log.Errorf("failed to port-map %s port %d: %s", proto, port, err)
-					}
-				}(proto, port)
+	// Create new mappings.
+	for proto, pports := range ports {
+		for port, mapped := range pports {
+			if mapped {
+				continue
 			}
+			wg.Add(1)
+			go func(proto string, port int) {
+				defer wg.Done()
+				_, err := nmgr.nat.NewMapping(proto, port)
+				if err != nil {
+					log.Errorf("failed to port-map %s port %d: %s", proto, port, err)
+				}
+			}(proto, port)
 		}
-	})
+	}
 }
 
 // NAT returns the natManager's nat object. this may be nil, if
```
