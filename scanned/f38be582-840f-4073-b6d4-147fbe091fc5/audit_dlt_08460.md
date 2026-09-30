# [?] bugfix(libs/header): fix data race in syncer (#1682)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2023-02-02
Source: https://github.com/celestiaorg/celestia-node/commit/da832b92f324648300d34b2e9ef9f311b2353333
Type: security-commit

## Details
bugfix(libs/header): fix data race in syncer (#1682)

## Patch
### libs/header/sync/sync.go
```diff
@@ -41,6 +41,8 @@ type Syncer[H header.Header] struct {
 	state   State
 	// signals to start syncing
 	triggerSync chan struct{}
+	// syncedHead is the latest synced header.
+	syncedHead H
 	// pending keeps ranges of valid new network headers awaiting to be appended to store
 	pending ranges[H]
 	// netReqLk ensures only one network head is requested at any moment
@@ -173,40 +175,42 @@ func (s *Syncer[H]) sync(ctx context.Context) {
 		return
 	}
 
-	head, err := s.store.Head(ctx)
-	if err != nil {
-		log.Errorw("getting head during sync", "err", err)
-		return
+	if s.syncedHead.IsZero() {
+		head, err := s.store.Head(ctx)
+		if err != nil {
+			log.Errorw("getting head during sync", "err", err)
+			return
+		}
+		s.syncedHead = head
 	}
-
-	if head.Height() >= newHead.Height() {
+	if s.syncedHead.Height() >= newHead.Height() {
 		log.Warnw("sync attempt to an already synced header",
-			"synced_height", head.Height(),
+			"synced_height", s.syncedHead.Height(),
 			"attempted_height", newHead.Height(),
 		)
 		log.Warn("PLEASE REPORT THIS AS A BUG")
 		return // should never happen, but just in case
 	}
 
 	log.Infow("syncing headers",
-		"from", head.Height(),
+		"from", s.syncedHead.Height(),
 		"to", newHead.Height())
-	err = s.doSync(ctx, head, newHead)
+	err := s.doSync(ctx, s.syncedHead, newHead)
 	if err != nil {
 		if errors.Is(err, context.Canceled) {
 			// don't log this error as it is normal case of Syncer being stopped
 			return
 		}
 
 		log.Errorw("syncing headers",
-			"from", head.Height(),
+			"from", s.syncedHead.Height(),
 			"to", newHead.Height(),
 			"err", err)
 		return
 	}
 
 	log.Infow("finished syncing",
-		"from", head.Height(),
+		"from", s.syncedHead.Height(),
 		"to", newHead.Height(),
 		"elapsed time", s.state.End.Sub(s.state.Start))
 }
@@ -246,7 +250,11 @@ func (s *Syncer[H]) processHeaders(ctx context.Context, from, to uint64) (int, e
 		return 0, err
 	}
 
-	return s.store.Append(ctx, headers...)
+	amount, err := s.store.Append(ctx, headers...)
+	if err == nil && amount > 0 {
+		s.syncedHead = headers[amount-1]
+	}
+	return amount, err
 }
 
 // findHeaders gets headers from either remote peers or from local cache of headers received by
```

### libs/header/sync/sync_test.go
```diff
@@ -85,20 +85,21 @@ func TestSyncCatchUp(t *testing.T) {
 	_, err = remoteStore.Append(ctx, suite.GenDummyHeaders(100)...)
 	require.NoError(t, err)
 
+	incomingHead := suite.GenDummyHeaders(1)[0]
 	// 3. syncer rcvs header from the future and starts catching-up
-	res := syncer.incomingNetHead(ctx, suite.GenDummyHeaders(1)[0])
+	res := syncer.incomingNetHead(ctx, incomingHead)
 	assert.Equal(t, pubsub.ValidationAccept, res)
 
 	time.Sleep(time.Millisecond * 10) // needs some to realize it is syncing
 	err = syncer.WaitSync(ctx)
 	require.NoError(t, err)
-
 	exp, err := remoteStore.Head(ctx)
 	require.NoError(t, err)
 
 	// 4. assert syncer caught-up
 	have, err := localStore.Head(ctx)
 	require.NoError(t, err)
+	assert.Equal(t, syncer.syncedHead.Height(), incomingHead.Height())
 	assert.Equal(t, exp.Height()+1, have.Height()) // plus one as we didn't add last header to remoteStore
 	assert.Empty(t, syncer.pending.Head())
 
@@ -156,7 +157,7 @@ func TestSyncPendingRangesWithMisses(t *testing.T) {
 	require.NoError(t, err)
 	_, err = localStore.GetByHeight(ctx, 43)
 	require.NoError(t, err)
-
+	require.Equal(t, syncer.syncedHead.Height(), int64(43))
 	exp, err := remoteStore.Head(ctx)
 	require.NoError(t, err)
 
```
