# [?] p2p/enode: avoid crashing for invalid IP (#21981)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2020-12-09
Source: https://github.com/celo-org/celo-blockchain/commit/817a3fb5622c8704116e9847661c16f9f3d785c6
Type: security-commit

## Details
p2p/enode: avoid crashing for invalid IP (#21981)

The database panicked for invalid IPs. This is usually no problem
because all code paths leading to node DB access verify the IP, but it's
dangerous because improper validation can turn this panic into a DoS
vulnerability. The quick fix here is to just turn database accesses
using invalid IP into a noop. This isn't great, but I'm planning to
remove the node DB for discv5 long-term, so it should be fine to have
this quick fix for half a year.

Fixes #21849

## Patch
### p2p/enode/nodedb.go
```diff
@@ -61,6 +61,10 @@ const (
 	dbVersion        = 9
 )
 
+var (
+	errInvalidIP = errors.New("invalid IP")
+)
+
 var zeroIP = make(net.IP, 16)
 
 // DB is the node database, storing previously seen nodes and any collected metadata about
@@ -359,43 +363,67 @@ func (db *DB) expireNodes() {
 // LastPingReceived retrieves the time of the last ping packet received from
 // a remote node.
 func (db *DB) LastPingReceived(id ID, ip net.IP) time.Time {
+	if ip = ip.To16(); ip == nil {
+		return time.Time{}
+	}
 	return time.Unix(db.fetchInt64(nodeItemKey(id, ip, dbNodePing)), 0)
 }
 
 // UpdateLastPingReceived updates the last time we tried contacting a remote node.
 func (db *DB) UpdateLastPingReceived(id ID, ip net.IP, instance time.Time) error {
+	if ip = ip.To16(); ip == nil {
+		return errInvalidIP
+	}
 	return db.storeInt64(nodeItemKey(id, ip, dbNodePing), instance.Unix())
 }
 
 // LastPongReceived retrieves the time of the last successful pong from remote node.
 func (db *DB) LastPongReceived(id ID, ip net.IP) time.Time {
+	if ip = ip.To16(); ip == nil {
+		return time.Time{}
+	}
 	// Launch expirer
 	db.ensureExpirer()
 	return time.Unix(db.fetchInt64(nodeItemKey(id, ip, dbNodePong)), 0)
 }
 
 // UpdateLastPongReceived updates the last pong time of a node.
 func (db *DB) UpdateLastPongReceived(id ID, ip net.IP, instance time.Time) error {
+	if ip = ip.To16(); ip == nil {
+		return errInvalidIP
+	}
 	return db.storeInt64(nodeItemKey(id, ip, dbNodePong), instance.Unix())
 }
 
 // FindFails retrieves the number of findnode failures since bonding.
 func (db *DB) FindFails(id ID, ip net.IP) int {
+	if ip = ip.To16(); ip == nil {
+		return 0
+	}
 	return int(db.fetchInt64(nodeItemKey(id, ip, dbNodeFindFails)))
 }
 
 // UpdateFindFails updates the number of findnode failures since bonding.
 func (db *DB) UpdateFindFails(id ID, ip net.IP, fails int) error {
+	if ip = ip.To16(); ip == nil {
+		return errInvalidIP
+	}
 	return db.storeInt64(nodeItemKey(id, ip, dbNodeFindFails), int64(fails))
 }
 
 // FindFailsV5 retrieves the discv5 findnode failure counter.
 func (db *DB) FindFailsV5(id ID, ip net.IP) int {
+	if ip = ip.To16(); ip == nil {
+		return 0
+	}
 	return int(db.fetchInt64(v5Key(id, ip, dbNodeFindFails)))
 }
 
 // UpdateFindFailsV5 stores the discv5 findnode failure counter.
 func (db *DB) UpdateFindFailsV5(id ID, ip net.IP, fails int) error {
+	if ip = ip.To16(); ip == nil {
+		return errInvalidIP
+	}
 	return db.storeInt64(v5Key(id, ip, dbNodeFindFails), int64(fails))
 }
 
```
