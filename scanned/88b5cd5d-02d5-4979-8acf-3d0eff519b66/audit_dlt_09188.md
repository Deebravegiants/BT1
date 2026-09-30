# [?] fix race condition in AutoRelay candidate handling (#1383)

## Summary
Severity: Unknown
Chain: libp2p
Component: libp2p/go-libp2p
Published: 2022-04-10
Source: https://github.com/libp2p/go-libp2p/commit/b4064b4bf834e3759164b6069fd939c183c89046
Type: security-commit

## Details
fix race condition in AutoRelay candidate handling (#1383)

## Patch
### p2p/host/autorelay/relay_finder.go
```diff
@@ -281,12 +281,16 @@ func (rf *relayFinder) tryNode(ctx context.Context, pi peer.AddrInfo) (supportsR
 
 func (rf *relayFinder) handleNewCandidate(ctx context.Context) {
 	rf.relayMx.Lock()
-	defer rf.relayMx.Unlock()
-	if len(rf.candidates) == 0 {
+	numRelays := len(rf.relays)
+	rf.relayMx.Unlock()
+	// We're already connected to our desired number of relays. Nothing to do here.
+	if numRelays == rf.conf.desiredRelays {
 		return
 	}
-	// We're already connected to our desired number of relays. Nothing to do here.
-	if len(rf.relays) == rf.conf.desiredRelays {
+
+	rf.candidateMx.Lock()
+	defer rf.candidateMx.Unlock()
+	if len(rf.candidates) == 0 {
 		return
 	}
 
@@ -468,12 +472,10 @@ func (rf *relayFinder) usingRelay(p peer.ID) bool {
 // selectCandidates returns an ordered slice of relay candidates.
 // Callers should attempt to obtain reservations with the candidates in this order.
 func (rf *relayFinder) selectCandidates() []*candidate {
-	rf.candidateMx.Lock()
 	var candidates []*candidate
 	for _, cand := range rf.candidates {
 		candidates = append(candidates, cand)
 	}
-	rf.candidateMx.Unlock()
 
 	// TODO: better relay selection strategy; this just selects random relays,
 	// but we should probably use ping latency as the selection metric
@@ -541,7 +543,9 @@ func (rf *relayFinder) Start() error {
 
 func (rf *relayFinder) Stop() error {
 	log.Debug("stopping relay finder")
-	rf.ctxCancel()
+	if rf.ctxCancel != nil {
+		rf.ctxCancel()
+	}
 	rf.refCount.Wait()
 	rf.ctxCancel = nil
 	return nil
```
