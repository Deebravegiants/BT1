# [?] fix race condition in getConnsToClose

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2021-09-02
Source: https://github.com/libp2p/go-libp2p/commit/4aeb0b901d50bd9a8ff372393983cd5ddddaee94
Type: security-commit

## Details
fix race condition in getConnsToClose

## Patch
### p2p/net/connmgr/connmgr.go
```diff
@@ -318,15 +318,13 @@ func (cm *BasicConnMgr) getConnsToClose() []network.Conn {
 		return nil
 	}
 
-	nconns := int(atomic.LoadInt32(&cm.connCount))
-	if nconns <= cm.cfg.lowWater {
+	if int(atomic.LoadInt32(&cm.connCount)) <= cm.cfg.lowWater {
 		log.Info("open connection count below limit")
 		return nil
 	}
 
-	npeers := cm.segments.countPeers()
-	candidates := make([]*peerInfo, 0, npeers)
-	ncandidates := 0
+	candidates := make([]peerInfo, 0, cm.segments.countPeers())
+	var ncandidates int
 	gracePeriodStart := time.Now().Add(-cm.cfg.gracePeriod)
 
 	cm.plk.RLock()
@@ -341,7 +339,9 @@ func (cm *BasicConnMgr) getConnsToClose() []network.Conn {
 				// skip peers in the grace period.
 				continue
 			}
-			candidates = append(candidates, inf)
+			// note that we're copying the entry here,
+			// but since inf.conns is a map, it will still point to the original object
+			candidates = append(candidates, *inf)
 			ncandidates += len(inf.conns)
 		}
 		s.Unlock()
@@ -381,7 +381,6 @@ func (cm *BasicConnMgr) getConnsToClose() []network.Conn {
 		// lock this to protect from concurrent modifications from connect/disconnect events
 		s := cm.segments.get(inf.id)
 		s.Lock()
-
 		if len(inf.conns) == 0 && inf.temp {
 			// handle temporary entries for early tags -- this entry has gone past the grace period
 			// and still holds no connections, so prune it.
@@ -390,8 +389,8 @@ func (cm *BasicConnMgr) getConnsToClose() []network.Conn {
 			for c := range inf.conns {
 				selected = append(selected, c)
 			}
+			target -= len(inf.conns)
 		}
-		target -= len(inf.conns)
 		s.Unlock()
 	}
 
```
