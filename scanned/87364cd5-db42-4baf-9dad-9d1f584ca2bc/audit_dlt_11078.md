# [?] fix race condition

## Summary
Severity: Unknown
Chain: Kroma
Component: kroma-network/kroma
Published: 2023-10-25
Source: https://github.com/kroma-network/kroma/commit/d2ad25efde8b5ffe310e16baaff4e97dc4a4ae53
Type: security-commit

## Details
fix race condition

fix: import formatting; LastUpdate as atomic.Int64

fix ci/cd

## Patch
### op-node/p2p/store/scorebook.go
```diff
@@ -2,6 +2,7 @@ package store
 
 import (
 	"context"
+	"sync/atomic"
 	"time"
 
 	"github.com/ethereum-optimism/optimism/op-service/clock"
@@ -17,17 +18,18 @@ const (
 
 var scoresBase = ds.NewKey("/peers/scores")
 
+// LastUpdate requires atomic update operations. Use the helper functions SetLastUpdated and LastUpdated to modify and access this field.
 type scoreRecord struct {
-	PeerScores PeerScores `json:"peerScores"`
 	LastUpdate int64      `json:"lastUpdate"` // unix timestamp in seconds
+	PeerScores PeerScores `json:"peerScores"`
 }
 
 func (s *scoreRecord) SetLastUpdated(t time.Time) {
-	s.LastUpdate = t.Unix()
+	atomic.StoreInt64(&s.LastUpdate, t.Unix())
 }
 
 func (s *scoreRecord) LastUpdated() time.Time {
-	return time.Unix(s.LastUpdate, 0)
+	return time.Unix(atomic.LoadInt64(&s.LastUpdate), 0)
 }
 
 func (s *scoreRecord) MarshalBinary() (data []byte, err error) {
```
