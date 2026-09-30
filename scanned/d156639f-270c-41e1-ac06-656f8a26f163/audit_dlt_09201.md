# [?] mocknet: fix data race

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2019-03-06
Source: https://github.com/libp2p/go-libp2p/commit/58f40b9d11276968df215e22649ad079957bc602
Type: security-commit

## Details
mocknet: fix data race

## Patch
### p2p/net/mock/mock_link.go
```diff
@@ -76,15 +76,21 @@ func (l *link) Peers() []peer.ID {
 }
 
 func (l *link) SetOptions(o LinkOptions) {
+	l.Lock()
+	defer l.Unlock()
 	l.opts = o
 	l.ratelimiter.UpdateBandwidth(l.opts.Bandwidth)
 }
 
 func (l *link) Options() LinkOptions {
+	l.RLock()
+	defer l.RUnlock()
 	return l.opts
 }
 
 func (l *link) GetLatency() time.Duration {
+	l.RLock()
+	defer l.RUnlock()
 	return l.opts.Latency
 }
 
```
