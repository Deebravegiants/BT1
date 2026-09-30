# [?] fix(holepunch): defer mutex unlock to avoid deadlock on shutdown (#3504)

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2026-05-13
Source: https://github.com/libp2p/go-libp2p/commit/3bfc5492c5b765e906c196633c3ac44ef7c777ae
Type: security-commit

## Details
fix(holepunch): defer mutex unlock to avoid deadlock on shutdown (#3504)

## Patch
### p2p/protocol/holepunch/svc.go
```diff
@@ -143,13 +143,13 @@ func (s *Service) waitForPublicAddr() {
 	}
 
 	s.holePuncherMx.Lock()
+	defer s.holePuncherMx.Unlock()
 	if s.ctx.Err() != nil {
 		// service is closed
 		return
 	}
 	s.holePuncher = newHolePuncher(s.host, s.ids, s.listenAddrs, s.tracer, s.filter)
 	s.holePuncher.directDialTimeout = s.directDialTimeout
-	s.holePuncherMx.Unlock()
 	close(s.hasPublicAddrsChan)
 }
 
```

### p2p/protocol/holepunch/svc_close_test.go
```diff
@@ -0,0 +1,70 @@
+package holepunch
+
+import (
+	"context"
+	"testing"
+	"time"
+
+	"github.com/libp2p/go-libp2p/core/host"
+	"github.com/libp2p/go-libp2p/core/network"
+	"github.com/libp2p/go-libp2p/core/peer"
+	"github.com/libp2p/go-libp2p/core/protocol"
+
+	ma "github.com/multiformats/go-multiaddr"
+)
+
+type closeTestHost struct {
+	host.Host
+}
+
+func (closeTestHost) ID() peer.ID                                         { return peer.ID("close-test-peer") }
+func (closeTestHost) Addrs() []ma.Multiaddr                               { return nil }
+func (closeTestHost) SetStreamHandler(protocol.ID, network.StreamHandler) {}
+func (closeTestHost) RemoveStreamHandler(protocol.ID)                     {}
+
+func TestWaitForPublicAddr_NoDeadlockOnCancel(t *testing.T) {
+	ctx, cancel := context.WithCancel(context.Background())
+	enteredListenAddrs := make(chan struct{})
+	releaseListenAddrs := make(chan struct{})
+	done := make(chan struct{})
+
+	s := &Service{
+		ctx:                ctx,
+		ctxCancel:          cancel,
+		host:               closeTestHost{},
+		hasPublicAddrsChan: make(chan struct{}),
+		listenAddrs: func() []ma.Multiaddr {
+			close(enteredListenAddrs)
+			<-releaseListenAddrs
+			return []ma.Multiaddr{ma.StringCast("/ip4/1.2.3.4/tcp/1234")}
+		},
+	}
+
+	s.refCount.Add(1)
+	go func() {
+		s.waitForPublicAddr()
+		close(done)
+	}()
+
+	<-enteredListenAddrs
+	cancel()
+	close(releaseListenAddrs)
+	<-done
+
+	if !s.holePuncherMx.TryLock() {
+		t.Fatal("holePuncherMx remained locked after cancellation path")
+	}
+	s.holePuncherMx.Unlock()
+
+	closed := make(chan struct{})
+	go func() {
+		_ = s.Close()
+		close(closed)
+	}()
+
+	select {
+	case <-closed:
+	case <-time.After(time.Second):
+		t.Fatal("Close blocked after waitForPublicAddr cancellation")
+	}
+}
```
