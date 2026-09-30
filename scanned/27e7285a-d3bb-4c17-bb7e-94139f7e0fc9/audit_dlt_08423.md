# [?] p2p/test: fix Switch test race condition (#4893)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2020-05-26
Source: https://github.com/cometbft/cometbft/commit/f4978466b999f21b06e80713d66004a252bf69ad
Type: security-commit

## Details
p2p/test: fix Switch test race condition (#4893)

## Patch
### p2p/switch.go
```diff
@@ -320,6 +320,9 @@ func (sw *Switch) Peers() IPeerSet {
 // TODO: make record depending on reason.
 func (sw *Switch) StopPeerForError(peer Peer, reason interface{}) {
 	sw.Logger.Error("Stopping peer for error", "peer", peer, "err", reason)
+	if peer == nil {
+		return
+	}
 	sw.stopAndRemovePeer(peer, reason)
 
 	if peer.IsPersistent() {
```

### p2p/switch_test.go
```diff
@@ -706,11 +706,15 @@ func TestSwitchInitPeerIsNotCalledBeforeRemovePeer(t *testing.T) {
 	defer rp.Stop()
 	_, err = rp.Dial(sw.NetAddress())
 	require.NoError(t, err)
-	// wait till the switch adds rp to the peer set
-	time.Sleep(50 * time.Millisecond)
 
-	// stop peer asynchronously
-	go sw.StopPeerForError(sw.Peers().Get(rp.ID()), "test")
+	// wait till the switch adds rp to the peer set, then stop the peer asynchronously
+	for {
+		time.Sleep(20 * time.Millisecond)
+		if peer := sw.Peers().Get(rp.ID()); peer != nil {
+			go sw.StopPeerForError(peer, "test")
+			break
+		}
+	}
 
 	// simulate peer reconnecting to us
 	_, err = rp.Dial(sw.NetAddress())
```
