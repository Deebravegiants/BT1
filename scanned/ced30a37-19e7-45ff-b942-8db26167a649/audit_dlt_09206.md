# [?] fix minor race condition in nat detection code

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2016-06-15
Source: https://github.com/libp2p/go-libp2p/commit/47808266ff204de00bf33fdb78490741818cc175
Type: security-commit

## Details
fix minor race condition in nat detection code

## Patch
### p2p/net/nat/nat.go
```diff
@@ -164,6 +164,7 @@ type mapping struct {
 
 	cached    ma.Multiaddr
 	cacheTime time.Time
+	cacheLk   sync.Mutex
 }
 
 func (m *mapping) NAT() *NAT {
@@ -203,8 +204,12 @@ func (m *mapping) InternalAddr() ma.Multiaddr {
 }
 
 func (m *mapping) ExternalAddr() (ma.Multiaddr, error) {
-	if time.Now().Sub(m.cacheTime) < CacheTime {
-		return m.cached, nil
+	m.cacheLk.Lock()
+	ctime := m.cacheTime
+	cval := m.cached
+	m.cacheLk.Unlock()
+	if time.Now().Sub(ctime) < CacheTime {
+		return cval, nil
 	}
 
 	if m.ExternalPort() == 0 { // dont even try right now.
@@ -234,8 +239,10 @@ func (m *mapping) ExternalAddr() (ma.Multiaddr, error) {
 
 	maddr2 := ipmaddr.Encapsulate(tcp)
 
+	m.cacheLk.Lock()
 	m.cached = maddr2
 	m.cacheTime = time.Now()
+	m.cacheLk.Unlock()
 	return maddr2, nil
 }
 
```
