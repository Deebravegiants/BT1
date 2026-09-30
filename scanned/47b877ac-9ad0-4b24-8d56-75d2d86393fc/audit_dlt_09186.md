# [?] fix race condition in holepunch service (#1473)

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2022-05-02
Source: https://github.com/libp2p/go-libp2p/commit/f5330dabf188149c751888e6686ee9b4ec39f31c
Type: security-commit

## Details
fix race condition in holepunch service (#1473)

Co-authored-by: watjurk <watjurk@gmail.com>

## Patch
### p2p/protocol/holepunch/svc.go
```diff
@@ -45,9 +45,11 @@ type Service struct {
 	ctx       context.Context
 	ctxCancel context.CancelFunc
 
-	host        host.Host
-	ids         identify.IDService
-	holePuncher *holePuncher
+	host host.Host
+	ids  identify.IDService
+
+	holePuncherMx sync.Mutex
+	holePuncher   *holePuncher
 
 	hasPublicAddrsChan chan struct{}
 
@@ -138,7 +140,9 @@ func (s *Service) watchForPublicAddr() {
 			if e.(event.EvtLocalReachabilityChanged).Reachability != network.ReachabilityPrivate {
 				continue
 			}
+			s.holePuncherMx.Lock()
 			s.holePuncher = newHolePuncher(s.host, s.ids, s.tracer)
+			s.holePuncherMx.Unlock()
 			close(s.hasPublicAddrsChan)
 			return
 		}
@@ -147,7 +151,12 @@ func (s *Service) watchForPublicAddr() {
 
 // Close closes the Hole Punch Service.
 func (s *Service) Close() error {
-	err := s.holePuncher.Close()
+	var err error
+	s.holePuncherMx.Lock()
+	if s.holePuncher != nil {
+		err = s.holePuncher.Close()
+	}
+	s.holePuncherMx.Unlock()
 	s.tracer.Close()
 	s.host.RemoveStreamHandler(Protocol)
 	s.ctxCancel()
@@ -257,5 +266,8 @@ func (s *Service) handleNewStream(str network.Stream) {
 // TODO: find a solution for this.
 func (s *Service) DirectConnect(p peer.ID) error {
 	<-s.hasPublicAddrsChan
-	return s.holePuncher.DirectConnect(p)
+	s.holePuncherMx.Lock()
+	holePuncher := s.holePuncher
+	s.holePuncherMx.Unlock()
+	return holePuncher.DirectConnect(p)
 }
```
