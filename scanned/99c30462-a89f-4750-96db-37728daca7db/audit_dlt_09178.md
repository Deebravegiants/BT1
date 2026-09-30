# [?] pstoremanager: fix race condition when removing peers from peer store (#2644)

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2023-11-17
Source: https://github.com/libp2p/go-libp2p/commit/284469128bd11280e58f7a28b1726f0dd54b7c36
Type: security-commit

## Details
pstoremanager: fix race condition when removing peers from peer store (#2644)

## Patch
### p2p/host/basic/basic_host.go
```diff
@@ -171,12 +171,11 @@ func NewHost(n network.Network, opts *HostOpts) (*BasicHost, error) {
 		opts.EventBus = eventbus.NewBus()
 	}
 
-	psManager, err := pstoremanager.NewPeerstoreManager(n.Peerstore(), opts.EventBus)
+	psManager, err := pstoremanager.NewPeerstoreManager(n.Peerstore(), opts.EventBus, n)
 	if err != nil {
 		return nil, err
 	}
 	hostCtx, cancel := context.WithCancel(context.Background())
-
 	h := &BasicHost{
 		network:                 n,
 		psManager:               psManager,
```

### p2p/host/pstoremanager/pstoremanager.go
```diff
@@ -41,6 +41,7 @@ func WithCleanupInterval(t time.Duration) Option {
 type PeerstoreManager struct {
 	pstore   peerstore.Peerstore
 	eventBus event.Bus
+	network  network.Network
 
 	cancel   context.CancelFunc
 	refCount sync.WaitGroup
@@ -49,11 +50,12 @@ type PeerstoreManager struct {
 	cleanupInterval time.Duration
 }
 
-func NewPeerstoreManager(pstore peerstore.Peerstore, eventBus event.Bus, opts ...Option) (*PeerstoreManager, error) {
+func NewPeerstoreManager(pstore peerstore.Peerstore, eventBus event.Bus, network network.Network, opts ...Option) (*PeerstoreManager, error) {
 	m := &PeerstoreManager{
 		pstore:      pstore,
 		gracePeriod: time.Minute,
 		eventBus:    eventBus,
+		network:     network,
 	}
 	for _, opt := range opts {
 		if err := opt(m); err != nil {
@@ -107,14 +109,21 @@ func (m *PeerstoreManager) background(ctx context.Context, sub event.Subscriptio
 				}
 			case network.Connected:
 				// If we reconnect to the peer before we've cleared the information, keep it.
+				// This is an optimization to keep the disconnected map small.
+				// We still need to check that a peer is actually disconnected before removing it from the peer store.
 				delete(disconnected, p)
 			}
 		case <-ticker.C:
 			now := time.Now()
 			for p, disconnectTime := range disconnected {
 				if disconnectTime.Add(m.gracePeriod).Before(now) {
-					m.pstore.RemovePeer(p)
-					delete(disconnected, p)
+					// Check that the peer is actually not connected at this point.
+					// This avoids a race condition where the Connected notification
+					// is processed after this time has fired.
+					if m.network.Connectedness(p) != network.Connected {
+						m.pstore.RemovePeer(p)
+						delete(disconnected, p)
+					}
 				}
 			}
 		case <-ctx.Done():
```

### p2p/host/pstoremanager/pstoremanager_test.go
```diff
@@ -9,6 +9,7 @@ import (
 	"github.com/libp2p/go-libp2p/core/peer"
 	"github.com/libp2p/go-libp2p/p2p/host/eventbus"
 	"github.com/libp2p/go-libp2p/p2p/host/pstoremanager"
+	swarmt "github.com/libp2p/go-libp2p/p2p/net/swarm/testing"
 
 	"github.com/stretchr/testify/require"
 	"go.uber.org/mock/gomock"
@@ -23,7 +24,7 @@ func TestGracePeriod(t *testing.T) {
 	eventBus := eventbus.NewBus()
 	pstore := NewMockPeerstore(ctrl)
 	const gracePeriod = 250 * time.Millisecond
-	man, err := pstoremanager.NewPeerstoreManager(pstore, eventBus, pstoremanager.WithGracePeriod(gracePeriod))
+	man, err := pstoremanager.NewPeerstoreManager(pstore, eventBus, swarmt.GenSwarm(t), pstoremanager.WithGracePeriod(gracePeriod))
 	require.NoError(t, err)
 	defer man.Close()
 	man.Start()
@@ -51,7 +52,7 @@ func TestReconnect(t *testing.T) {
 	eventBus := eventbus.NewBus()
 	pstore := NewMockPeerstore(ctrl)
 	const gracePeriod = 200 * time.Millisecond
-	man, err := pstoremanager.NewPeerstoreManager(pstore, eventBus, pstoremanager.WithGracePeriod(gracePeriod))
+	man, err := pstoremanager.NewPeerstoreManager(pstore, eventBus, swarmt.GenSwarm(t), pstoremanager.WithGracePeriod(gracePeriod))
 	require.NoError(t, err)
 	defer man.Close()
 	man.Start()
@@ -77,7 +78,7 @@ func TestClose(t *testing.T) {
 	eventBus := eventbus.NewBus()
 	pstore := NewMockPeerstore(ctrl)
 	const gracePeriod = time.Hour
-	man, err := pstoremanager.NewPeerstoreManager(pstore, eventBus, pstoremanager.WithGracePeriod(gracePeriod))
+	man, err := pstoremanager.NewPeerstoreManager(pstore, eventBus, swarmt.GenSwarm(t), pstoremanager.WithGracePeriod(gracePeriod))
 	require.NoError(t, err)
 	man.Start()
 
```
