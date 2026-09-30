# [?] Fix race condition in sequencer stopping logic (#11769)

## Summary
Severity: Unknown
Chain: Boba
Component: bobanetwork/boba
Published: 2024-09-10
Source: https://github.com/bobanetwork/boba/commit/7e97b67d43f2d89021eb49b01b55e22097d18d40
Type: security-commit

## Details
Fix race condition in sequencer stopping logic (#11769)

* Fix race condition in sequencer stopping logic

* Add channel to signal that latestHead has been updated

* Fix test

* Store latest sealed separately, as latest gets cleared by engine.PayloadSuccessEvent

* Cleanup tests

* Add assertions on latest block ref variables

* Re-check if sequencer is active

## Patch
### op-node/rollup/sequencing/sequencer.go
```diff
@@ -111,8 +111,11 @@ type Sequencer struct {
 	nextAction   time.Time
 	nextActionOK bool
 
-	latest     BuildingState
-	latestHead eth.L2BlockRef
+	latest       BuildingState
+	latestSealed eth.L2BlockRef
+	latestHead   eth.L2BlockRef
+
+	latestHeadSet chan struct{}
 
 	// toBlockRef converts a payload to a block-ref, and is only configurable for test-purposes
 	toBlockRef func(rollupCfg *rollup.Config, payload *eth.ExecutionPayload) (eth.L2BlockRef, error)
@@ -283,6 +286,7 @@ func (d *Sequencer) onBuildSealed(x engine.BuildSealedEvent) {
 		Ref:          x.Ref,
 	})
 	d.latest.Ref = x.Ref
+	d.latestSealed = x.Ref
 }
 
 func (d *Sequencer) onPayloadSealInvalid(x engine.PayloadSealInvalidEvent) {
@@ -425,7 +429,7 @@ func (d *Sequencer) onForkchoiceUpdate(x engine.ForkchoiceUpdateEvent) {
 	d.log.Debug("Sequencer is processing forkchoice update", "unsafe", x.UnsafeL2Head, "latest", d.latestHead)
 
 	if !d.active.Load() {
-		d.latestHead = x.UnsafeL2Head
+		d.setLatestHead(x.UnsafeL2Head)
 		return
 	}
 	// If the safe head has fallen behind by a significant number of blocks, delay creating new blocks
@@ -456,7 +460,15 @@ func (d *Sequencer) onForkchoiceUpdate(x engine.ForkchoiceUpdateEvent) {
 			d.nextAction = now
 		}
 	}
-	d.latestHead = x.UnsafeL2Head
+	d.setLatestHead(x.UnsafeL2Head)
+}
+
+func (d *Sequencer) setLatestHead(head eth.L2BlockRef) {
+	d.latestHead = head
+	if d.latestHeadSet != nil {
+		close(d.latestHeadSet)
+		d.latestHeadSet = nil
+	}
 }
 
 // StartBuildingBlock initiates a block building job on top of the given L2 head, safe and finalized blocks, and using the provided l1Origin.
@@ -646,12 +658,33 @@ func (d *Sequencer) forceStart() error {
 	return nil
 }
 
-func (d *Sequencer) Stop(ctx context.Context) (hash common.Hash, err error) {
+func (d *Sequencer) Stop(ctx context.Context) (common.Hash, error) {
 	if err := d.l.LockCtx(ctx); err != nil {
 		return common.Hash{}, err
 	}
+
+	if !d.active.Load() {
+		d.l.Unlock()
+		return common.Hash{}, ErrSequencerAlreadyStopped
+	}
+
+	// ensure latestHead has been updated to the latest sealed/gossiped block before stopping the sequencer
+	for d.latestHead.Hash != d.latestSealed.Hash {
+		latestHeadSet := make(chan struct{})
+		d.latestHeadSet = latestHeadSet
+		d.l.Unlock()
+		select {
+		case <-ctx.Done():
+			return common.Hash{}, ctx.Err()
+		case <-latestHeadSet:
+		}
+		if err := d.l.LockCtx(ctx); err != nil {
+			return common.Hash{}, err
+		}
+	}
 	defer d.l.Unlock()
 
+	// Stop() may have been called twice, so check if we are active after reacquiring the lock
 	if !d.active.Load() {
 		return common.Hash{}, ErrSequencerAlreadyStopped
 	}
```

### op-node/rollup/sequencing/sequencer_test.go
```diff
@@ -170,11 +170,37 @@ func TestSequencer_StartStop(t *testing.T) {
 	require.True(t, deps.asyncGossip.started, "async gossip is always started on initialization")
 	require.False(t, deps.seqState.active, "sequencer not active yet")
 
+	// latest refs should all be empty
+	require.Equal(t, common.Hash{}, seq.latest.Ref.Hash)
+	require.Equal(t, common.Hash{}, seq.latestSealed.Hash)
+	require.Equal(t, common.Hash{}, seq.latestHead.Hash)
+
+	// update the latestSealed
+	envelope := &eth.ExecutionPayloadEnvelope{
+		ExecutionPayload: &eth.ExecutionPayload{},
+	}
+	emitter.ExpectOnce(engine.PayloadProcessEvent{
+		Envelope: envelope,
+		Ref:      eth.L2BlockRef{Hash: common.Hash{0xaa}},
+	})
+	seq.OnEvent(engine.BuildSealedEvent{
+		Envelope: envelope,
+		Ref:      eth.L2BlockRef{Hash: common.Hash{0xaa}},
+	})
+	require.Equal(t, common.Hash{0xaa}, seq.latest.Ref.Hash)
+	require.Equal(t, common.Hash{0xaa}, seq.latestSealed.Hash)
+	require.Equal(t, common.Hash{}, seq.latestHead.Hash)
+
+	// update latestHead
+	emitter.AssertExpectations(t)
 	seq.OnEvent(engine.ForkchoiceUpdateEvent{
 		UnsafeL2Head:    eth.L2BlockRef{Hash: common.Hash{0xaa}},
 		SafeL2Head:      eth.L2BlockRef{},
 		FinalizedL2Head: eth.L2BlockRef{},
 	})
+	require.Equal(t, common.Hash{0xaa}, seq.latest.Ref.Hash)
+	require.Equal(t, common.Hash{0xaa}, seq.latestSealed.Hash)
+	require.Equal(t, common.Hash{0xaa}, seq.latestHead.Hash)
 
 	require.False(t, seq.Active())
 	// no action scheduled
@@ -346,6 +372,25 @@ func TestSequencer_StaleBuild(t *testing.T) {
 	_, ok = seq.NextAction()
 	require.False(t, ok, "optimistically published, but not ready to sequence next, until local processing completes")
 
+	// attempting to stop block building here should timeout, because the sealed block is different from the latestHead
+	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
+	defer cancel()
+	_, err := seq.Stop(ctx)
+	require.Error(t, err, "stop should have timed out")
+	require.ErrorIs(t, err, ctx.Err())
+
+	// reset latestSealed to the previous head
+	emitter.ExpectOnce(engine.PayloadProcessEvent{
+		Envelope: payloadEnvelope,
+		Ref:      head,
+	})
+	seq.OnEvent(engine.BuildSealedEvent{
+		Info:     payloadInfo,
+		Envelope: payloadEnvelope,
+		Ref:      head,
+	})
+	emitter.AssertExpectations(t)
+
 	// Now we stop the block building,
 	// before successful local processing of the committed block!
 	stopHead, err := seq.Stop(context.Background())
```
