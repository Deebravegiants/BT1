# [?] quicreuse: remove workaround for quic-go listener close deadlock (#2746)

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2024-03-22
Source: https://github.com/libp2p/go-libp2p/commit/f12c3ce169de6184e692dad3463afe1762036504
Type: security-commit

## Details
quicreuse: remove workaround for quic-go listener close deadlock (#2746)

## Patch
### p2p/transport/quicreuse/listener.go
```diff
@@ -30,7 +30,6 @@ type protoConf struct {
 
 type quicListener struct {
 	l         *quic.Listener
-	closeMx   sync.Mutex
 	transport refCountedQuicTransport
 	running   chan struct{}
 	addrs     []ma.Multiaddr
@@ -125,13 +124,7 @@ func (l *quicListener) Add(tlsConf *tls.Config, allowWindowIncrease func(conn qu
 
 func (l *quicListener) Run() error {
 	defer close(l.running)
-	defer func() {
-		// transport close is not safe to use concurrently with listener close.
-		// remove after https://github.com/quic-go/quic-go/issues/4266 is fixed.
-		l.closeMx.Lock()
-		defer l.closeMx.Unlock()
-		l.transport.DecreaseCount()
-	}()
+	defer l.transport.DecreaseCount()
 	for {
 		conn, err := l.l.Accept(context.Background())
 		if err != nil {
@@ -154,12 +147,7 @@ func (l *quicListener) Run() error {
 }
 
 func (l *quicListener) Close() error {
-	// listener close is not safe to use concurrently with transport close.
-	// remove after https://github.com/quic-go/quic-go/issues/4266 is fixed.
-	l.closeMx.Lock()
 	err := l.l.Close()
-	l.closeMx.Unlock()
-
 	<-l.running // wait for Run to return
 	return err
 }
```
