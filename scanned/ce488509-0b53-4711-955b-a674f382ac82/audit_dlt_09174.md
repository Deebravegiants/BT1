# [?] basichost: fix deadlock with addrs_manager (#3348)

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2025-07-30
Source: https://github.com/libp2p/go-libp2p/commit/26a5710d35c654f7a08f41d2a96cb4d59b0d2ba6
Type: security-commit

## Details
basichost: fix deadlock with addrs_manager (#3348)

## Patch
### config/config.go
```diff
@@ -623,7 +623,13 @@ func (cfg *Config) NewNode() (host.Host, error) {
 	}
 
 	if cfg.Routing != nil {
-		return &closableRoutedHost{App: app, RoutedHost: rh}, nil
+		return &closableRoutedHost{
+			closableBasicHost: closableBasicHost{
+				App:       app,
+				BasicHost: bh,
+			},
+			RoutedHost: rh,
+		}, nil
 	}
 	return &closableBasicHost{App: app, BasicHost: bh}, nil
 }
```

### config/host.go
```diff
@@ -20,11 +20,14 @@ func (h *closableBasicHost) Close() error {
 }
 
 type closableRoutedHost struct {
-	*fx.App
+	// closableBasicHost is embedded here so that interface assertions on
+	// BasicHost exported methods work correctly.
+	closableBasicHost
 	*routed.RoutedHost
 }
 
 func (h *closableRoutedHost) Close() error {
 	_ = h.App.Stop(context.Background())
+	// The routed host will close the basic host
 	return h.RoutedHost.Close()
 }
```

### libp2p_test.go
```diff
@@ -812,6 +812,23 @@ func TestCustomTCPDialer(t *testing.T) {
 	require.ErrorContains(t, err, expectedErr.Error())
 }
 
+func TestBasicHostInterfaceAssertion(t *testing.T) {
+	mockRouter := &mockPeerRouting{}
+	h, err := New(
+		NoListenAddrs,
+		Routing(func(host.Host) (routing.PeerRouting, error) { return mockRouter, nil }),
+		DisableRelay(),
+	)
+	require.NoError(t, err)
+	defer h.Close()
+
+	require.NotNil(t, h)
+	require.NotEmpty(t, h.ID())
+
+	_, ok := h.(interface{ AllAddrs() []ma.Multiaddr })
+	require.True(t, ok)
+}
+
 func BenchmarkAllAddrs(b *testing.B) {
 	h, err := New()
 
```

### p2p/host/basic/addrs_manager.go
```diff
@@ -53,7 +53,9 @@ type addrsManager struct {
 	addrsUpdatedChan chan struct{}
 
 	// triggerAddrsUpdateChan is used to trigger an addresses update.
-	triggerAddrsUpdateChan chan struct{}
+	triggerAddrsUpdateChan chan chan struct{}
+	// started is used to check whether the addrsManager has started.
+	started atomic.Bool
 	// triggerReachabilityUpdate is notified when reachable addrs are updated.
 	triggerReachabilityUpdate chan struct{}
 
@@ -87,7 +89,7 @@ func newAddrsManager(
 		observedAddrsManager:      observedAddrsManager,
 		natManager:                natmgr,
 		addrsFactory:              addrsFactory,
-		triggerAddrsUpdateChan:    make(chan struct{}, 1),
+		triggerAddrsUpdateChan:    make(chan chan struct{}, 1),
 		triggerReachabilityUpdate: make(chan struct{}, 1),
 		addrsUpdatedChan:          addrsUpdatedChan,
 		interfaceAddrs:            &interfaceAddrsCache{},
@@ -115,7 +117,6 @@ func (a *addrsManager) Start() error {
 			return fmt.Errorf("error starting addrs reachability tracker: %s", err)
 		}
 	}
-
 	return a.startBackgroundWorker()
 }
 
@@ -140,16 +141,24 @@ func (a *addrsManager) NetNotifee() network.Notifiee {
 	// Updating addrs in sync provides the nice property that
 	// host.Addrs() just after host.Network().Listen(x) will return x
 	return &network.NotifyBundle{
-		ListenF:      func(network.Network, ma.Multiaddr) { a.triggerAddrsUpdate() },
-		ListenCloseF: func(network.Network, ma.Multiaddr) { a.triggerAddrsUpdate() },
+		ListenF:      func(network.Network, ma.Multiaddr) { a.updateAddrsSync() },
+		ListenCloseF: func(network.Network, ma.Multiaddr) { a.updateAddrsSync() },
 	}
 }
 
-func (a *addrsManager) triggerAddrsUpdate() {
-	a.updateAddrs(false, nil)
+func (a *addrsManager) updateAddrsSync() {
+	// This prevents a deadlock where addrs updates before starting the manager are ignored
+	if !a.started.Load() {
+		return
+	}
+	ch := make(chan struct{})
 	select {
-	case a.triggerAddrsUpdateChan <- struct{}{}:
-	default:
+	case a.triggerAddrsUpdateChan <- ch:
+		select {
+		case <-ch:
+		case <-a.ctx.Done():
+		}
+	case <-a.ctx.Done():
 	}
 }
 
@@ -177,7 +186,7 @@ func (a *addrsManager) startBackgroundWorker() error {
 		}
 		err2 := autonatReachabilitySub.Close()
 		if err2 != nil {
-			err2 = fmt.Errorf("error closing autonat reachability: %w", err1)
+			err2 = fmt.Errorf("error closing autonat reachability: %w", err2)
 		}
 		err = fmt.Errorf("error subscribing to autonat reachability: %s", err)
 		return errors.Join(err, err1, err2)
@@ -200,9 +209,11 @@ func (a *addrsManager) startBackgroundWorker() error {
 		}
 	default:
 	}
+	// this ensures that listens concurrent with Start are reflected correctly after Start exits.
+	a.started.Store(true)
 	// update addresses before starting the worker loop. This ensures that any address updates
 	// before calling addrsManager.Start are correctly reported after Start returns.
-	a.updateAddrs(true, relayAddrs)
+	a.updateAddrs(relayAddrs)
 
 	a.wg.Add(1)
 	go a.background(autoRelayAddrsSub, autonatReachabilitySub, emitter, relayAddrs)
@@ -227,13 +238,18 @@ func (a *addrsManager) background(autoRelayAddrsSub, autonatReachabilitySub even
 	ticker := time.NewTicker(addrChangeTickrInterval)
 	defer ticker.Stop()
 	var previousAddrs hostAddrs
+	var notifCh chan struct{}
 	for {
-		currAddrs := a.updateAddrs(true, relayAddrs)
+		currAddrs := a.updateAddrs(relayAddrs)
+		if notifCh != nil {
+			close(notifCh)
+			notifCh = nil
+		}
 		a.notifyAddrsChanged(emitter, previousAddrs, currAddrs)
 		previousAddrs = currAddrs
 		select {
 		case <-ticker.C:
-		case <-a.triggerAddrsUpdateChan:
+		case notifCh = <-a.triggerAddrsUpdateChan:
 		case <-a.triggerReachabilityUpdate:
 		case e := <-autoRelayAddrsSub.Out():
 			if evt, ok := e.(event.EvtAutoRelayAddrsUpdated); ok {
@@ -250,26 +266,18 @@ func (a *addrsManager) background(autoRelayAddrsSub, autonatReachabilitySub even
 }
 
 // updateAddrs updates the addresses of the host and returns the new updated
-// addrs
-func (a *addrsManager) updateAddrs(updateRelayAddrs bool, relayAddrs []ma.Multiaddr) hostAddrs {
-	// Must lock while doing both recompute and update as this method is called from
-	// multiple goroutines.
-	a.addrsMx.Lock()
-	defer a.addrsMx.Unlock()
-
+// addrs. This must only be called from the background goroutine or from the Start method otherwise
+// we may end up with stale addrs.
+func (a *addrsManager) updateAddrs(relayAddrs []ma.Multiaddr) hostAddrs {
 	localAddrs := a.getLocalAddrs()
 	var currReachableAddrs, currUnreachableAddrs, currUnknownAddrs []ma.Multiaddr
 	if a.addrsReachabilityTracker != nil {
 		currReachableAddrs, currUnreachableAddrs, currUnknownAddrs = a.getConfirmedAddrs(localAddrs)
 	}
-	if !updateRelayAddrs {
-		relayAddrs = a.currentAddrs.relayAddrs
-	} else {
-		// Copy the callers slice
-		relayAddrs = slices.Clone(relayAddrs)
-	}
+	relayAddrs = slices.Clone(relayAddrs)
 	currAddrs := a.getAddrs(slices.Clone(localAddrs), relayAddrs)
 
+	a.addrsMx.Lock()
 	a.currentAddrs = hostAddrs{
 		addrs:            append(a.currentAddrs.addrs[:0], currAddrs...),
 		localAddrs:       append(a.currentAddrs.localAddrs[:0], localAddrs...),
@@ -278,6 +286,7 @@ func (a *addrsManager) updateAddrs(updateRelayAddrs bool, relayAddrs []ma.Multia
 		unknownAddrs:     append(a.currentAddrs.unknownAddrs[:0], currUnknownAddrs...),
 		relayAddrs:       append(a.currentAddrs.relayAddrs[:0], relayAddrs...),
 	}
+	a.addrsMx.Unlock()
 
 	return hostAddrs{
 		localAddrs:       localAddrs,
@@ -315,7 +324,8 @@ func (a *addrsManager) notifyAddrsChanged(emitter event.Emitter, previous, curre
 	if areAddrsDifferent(previous.reachableAddrs, current.reachableAddrs) ||
 		areAddrsDifferent(previous.unreachableAddrs, current.unreachableAddrs) ||
 		areAddrsDifferent(previous.unknownAddrs, current.unknownAddrs) {
-		log.Debugf("host reachable addrs updated: %s", current.localAddrs)
+		log.Debugf("host reachable addrs updated: reachable: %s, unreachable: %s, unknown: %s",
+			current.reachableAddrs, current.unreachableAddrs, current.unknownAddrs)
 		if err := emitter.Emit(event.EvtHostReachableAddrsChanged{
 			Reachable:   slices.Clone(current.reachableAddrs),
 			Unreachable: slices.Clone(current.unreachableAddrs),
```

### p2p/host/basic/addrs_manager_test.go
```diff
@@ -5,6 +5,7 @@ import (
 	"errors"
 	"fmt"
 	"slices"
+	"sync/atomic"
 	"testing"
 	"time"
 
@@ -13,6 +14,7 @@ import (
 	"github.com/libp2p/go-libp2p/p2p/host/eventbus"
 	"github.com/libp2p/go-libp2p/p2p/protocol/autonatv2"
 	ma "github.com/multiformats/go-multiaddr"
+	"github.com/multiformats/go-multiaddr/matest"
 	manet "github.com/multiformats/go-multiaddr/net"
 	"github.com/prometheus/client_golang/prometheus"
 	"github.com/stretchr/testify/assert"
@@ -239,7 +241,7 @@ func TestAddrsManager(t *testing.T) {
 			},
 			ListenAddrs: func() []ma.Multiaddr { return []ma.Multiaddr{lhquic, lhtcp} },
 		})
-		am.triggerAddrsUpdate()
+		am.updateAddrsSync()
 		require.EventuallyWithT(t, func(collect *assert.CollectT) {
 			expected := []ma.Multiaddr{publicQUIC, lhquic, lhtcp}
 			assert.ElementsMatch(collect, am.Addrs(), expected, "%s\n%s", am.Addrs(), expected)
@@ -315,7 +317,7 @@ func TestAddrsManager(t *testing.T) {
 			},
 			ListenAddrs: func() []ma.Multiaddr { return []ma.Multiaddr{lhquic, lhtcp} },
 		})
-		am.triggerAddrsUpdate()
+		am.updateAddrsSync()
 		expected := []ma.Multiaddr{lhquic, lhtcp, publicTCP, publicQUIC}
 		require.EventuallyWithT(t, func(collect *assert.CollectT) {
 			assert.ElementsMatch(collect, am.Addrs(), expected, "%s\n%s", am.Addrs(), expected)
@@ -343,7 +345,7 @@ func TestAddrsManager(t *testing.T) {
 			},
 			ListenAddrs: func() []ma.Multiaddr { return []ma.Multiaddr{lhquic} },
 		})
-		am.triggerAddrsUpdate()
+		am.updateAddrsSync()
 		expected := []ma.Multiaddr{lhquic}
 		expected = append(expected, quicAddrs[:maxObservedAddrsPerListenAddr]...)
 		require.EventuallyWithT(t, func(collect *assert.CollectT) {
@@ -428,12 +430,32 @@ func TestAddrsManager(t *testing.T) {
 		require.Contains(t, am.Addrs(), publicTCP)
 		require.NotContains(t, am.Addrs(), publicQUIC)
 		close(updateChan)
-		am.triggerAddrsUpdate()
+		am.updateAddrsSync()
 		require.EventuallyWithT(t, func(collect *assert.CollectT) {
 			assert.Contains(collect, am.Addrs(), publicQUIC)
 			assert.NotContains(collect, am.Addrs(), publicTCP)
 		}, 1*time.Second, 50*time.Millisecond)
 	})
+
+	t.Run("addrs factory depends on confirmed addrs", func(t *testing.T) {
+		var amp atomic.Pointer[addrsManager]
+		q1 := ma.StringCast("/ip4/1.1.1.1/udp/1/quic-v1")
+		addrsFactory := func(_ []ma.Multiaddr) []ma.Multiaddr {
+			if amp.Load() == nil {
+				return nil
+			}
+			// r is empty as there's no reachability tracker
+			r, _, _ := amp.Load().ConfirmedAddrs()
+			return append(r, q1)
+		}
+		am := newAddrsManagerTestCase(t, addrsManagerArgs{
+			AddrsFactory: addrsFactory,
+			ListenAddrs:  func() []ma.Multiaddr { return []ma.Multiaddr{lhquic, lhtcp} },
+		})
+		amp.Store(am.addrsManager)
+		am.updateAddrsSync()
+		matest.AssertEqualMultiaddrs(t, []ma.Multiaddr{q1}, am.Addrs())
+	})
 }
 
 func TestAddrsManagerReachabilityEvent(t *testing.T) {
```

### p2p/host/basic/basic_host.go
```diff
@@ -262,9 +262,6 @@ func NewHost(n network.Network, opts *HostOpts) (*BasicHost, error) {
 	if err != nil {
 		return nil, fmt.Errorf("failed to create address service: %w", err)
 	}
-	// register to be notified when the network's listen addrs change,
-	// so we can update our address set and push events if needed
-	h.Network().Notify(h.addressManager.NetNotifee())
 
 	if opts.EnableHolePunching {
 		if opts.EnableMetrics {
@@ -336,6 +333,9 @@ func (h *BasicHost) Start() {
 			log.Errorf("autonat v2 failed to start: %s", err)
 		}
 	}
+	// register to be notified when the network's listen addrs change,
+	// so we can update our address set and push events if needed
+	h.Network().Notify(h.addressManager.NetNotifee())
 	if err := h.addressManager.Start(); err != nil {
 		log.Errorf("address service failed to start: %s", err)
 	}
@@ -857,7 +857,6 @@ func (h *BasicHost) Close() error {
 		if h.cmgr != nil {
 			h.cmgr.Close()
 		}
-		h.addressManager.Close()
 
 		if h.ids != nil {
 			h.ids.Close()
@@ -882,6 +881,7 @@ func (h *BasicHost) Close() error {
 			log.Errorf("swarm close failed: %v", err)
 		}
 
+		h.addressManager.Close()
 		h.psManager.Close()
 		if h.Peerstore() != nil {
 			h.Peerstore().Close()
```

### p2p/host/basic/basic_host_test.go
```diff
@@ -737,7 +737,7 @@ func TestHostAddrChangeDetection(t *testing.T) {
 		lk.Lock()
 		currentAddrSet = i
 		lk.Unlock()
-		h.addressManager.triggerAddrsUpdate()
+		h.addressManager.updateAddrsSync()
 		evt := waitForAddrChangeEvent(ctx, sub, t)
 		if !updatedAddrEventsEqual(expectedEvents[i-1], evt) {
 			t.Errorf("change events not equal: \n\texpected: %v \n\tactual: %v", expectedEvents[i-1], evt)
```
