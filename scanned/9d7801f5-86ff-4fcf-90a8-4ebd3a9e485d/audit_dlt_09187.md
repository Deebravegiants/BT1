# [?] fix race condition caused by relayFinder.ctxCancel

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2022-04-27
Source: https://github.com/libp2p/go-libp2p/commit/3f6d77ddf9d5687a3137533e57c8e2bcde90fa04
Type: security-commit

## Details
fix race condition caused by relayFinder.ctxCancel

## Patch
### p2p/host/autorelay/relay_finder.go
```diff
@@ -61,8 +61,10 @@ type relayFinder struct {
 
 	conf *config
 
-	refCount  sync.WaitGroup
-	ctxCancel context.CancelFunc
+	refCount sync.WaitGroup
+
+	ctxCancel   context.CancelFunc
+	ctxCancelMx sync.Mutex
 
 	peerChan <-chan peer.AddrInfo
 
@@ -581,6 +583,8 @@ func (rf *relayFinder) relayAddrs(addrs []ma.Multiaddr) []ma.Multiaddr {
 }
 
 func (rf *relayFinder) Start() error {
+	rf.ctxCancelMx.Lock()
+	defer rf.ctxCancelMx.Unlock()
 	if rf.ctxCancel != nil {
 		return errors.New("relayFinder already running")
 	}
@@ -596,6 +600,8 @@ func (rf *relayFinder) Start() error {
 }
 
 func (rf *relayFinder) Stop() error {
+	rf.ctxCancelMx.Lock()
+	defer rf.ctxCancelMx.Unlock()
 	log.Debug("stopping relay finder")
 	if rf.ctxCancel != nil {
 		rf.ctxCancel()
```
