# [?] service.head race condition fix (#10741)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2022-05-27
Source: https://github.com/OffchainLabs/prysm/commit/adabd1fa4f9acf356a5ce06a4f0fe391db174037
Type: security-commit

## Details
service.head race condition fix (#10741)

* added various read mutex locks for service.head

* added RLocks around all calls to s.headRoot()

* added RLocks around all calls to s.headBlock()

* reduce lock surface-> Stop(),handleEpochBoundary()

* refactor Stop() to +performance, -lock_surface

* Apply suggestions from code review

Co-authored-by: terencechain <terence@prysmaticlabs.com>

* fixed indentation

Co-authored-by: terencechain <terence@prysmaticlabs.com>
Co-authored-by: Raul Jordan <raul@prysmaticlabs.com>
Co-authored-by: Radosław Kapka <rkapka@wp.pl>

## Patch
### beacon-chain/blockchain/head.go
```diff
@@ -133,10 +133,12 @@ func (s *Service) saveHead(ctx context.Context, headRoot [32]byte, headBlock int
 	}
 
 	// A chain re-org occurred, so we fire an event notifying the rest of the services.
-	headSlot := s.HeadSlot()
-	newHeadSlot := headBlock.Block().Slot()
+	s.headLock.RLock()
 	oldHeadRoot := s.headRoot()
 	oldStateRoot := s.headBlock().Block().StateRoot()
+	s.headLock.RUnlock()
+	headSlot := s.HeadSlot()
+	newHeadSlot := headBlock.Block().Slot()
 	newStateRoot := headBlock.Block().StateRoot()
 	if bytesutil.ToBytes32(headBlock.Block().ParentRoot()) != bytesutil.ToBytes32(r) {
 		log.WithFields(logrus.Fields{
```

### beacon-chain/blockchain/process_block.go
```diff
@@ -544,9 +544,13 @@ func (s *Service) handleEpochBoundary(ctx context.Context, postState state.Beaco
 			return err
 		}
 	} else if postState.Slot() >= s.nextEpochBoundarySlot {
-		if err := reportEpochMetrics(ctx, postState, s.head.state); err != nil {
+		s.headLock.RLock()
+		st := s.head.state
+		s.headLock.RUnlock()
+		if err := reportEpochMetrics(ctx, postState, st); err != nil {
 			return err
 		}
+
 		var err error
 		s.nextEpochBoundarySlot, err = slots.EpochStart(coreTime.NextEpoch(postState))
 		if err != nil {
```

### beacon-chain/blockchain/receive_attestation.go
```diff
@@ -164,21 +164,26 @@ func (s *Service) UpdateHead(ctx context.Context) error {
 	if err != nil {
 		log.WithError(err).Warn("Resolving fork due to new attestation")
 	}
+	s.headLock.RLock()
 	if s.headRoot() != newHeadRoot {
 		log.WithFields(logrus.Fields{
 			"oldHeadRoot": fmt.Sprintf("%#x", s.headRoot()),
 			"newHeadRoot": fmt.Sprintf("%#x", newHeadRoot),
 		}).Debug("Head changed due to attestations")
 	}
+	s.headLock.RUnlock()
 	s.notifyEngineIfChangedHead(ctx, newHeadRoot)
 	return nil
 }
 
 // This calls notify Forkchoice Update in the event that the head has changed
 func (s *Service) notifyEngineIfChangedHead(ctx context.Context, newHeadRoot [32]byte) {
+	s.headLock.RLock()
 	if newHeadRoot == [32]byte{} || s.headRoot() == newHeadRoot {
+		s.headLock.RUnlock()
 		return
 	}
+	s.headLock.RUnlock()
 
 	if !s.hasBlockInInitSyncOrDB(ctx, newHeadRoot) {
 		log.Debug("New head does not exist in DB. Do nothing")
```

### beacon-chain/blockchain/service.go
```diff
@@ -144,13 +144,18 @@ func (s *Service) Start() {
 func (s *Service) Stop() error {
 	defer s.cancel()
 
+	// lock before accessing s.head, s.head.state, s.head.state.FinalizedCheckpoint().Root
+	s.headLock.RLock()
 	if s.cfg.StateGen != nil && s.head != nil && s.head.state != nil {
+		r := s.head.state.FinalizedCheckpoint().Root
+		s.headLock.RUnlock()
 		// Save the last finalized state so that starting up in the following run will be much faster.
-		if err := s.cfg.StateGen.ForceCheckpoint(s.ctx, s.head.state.FinalizedCheckpoint().Root); err != nil {
+		if err := s.cfg.StateGen.ForceCheckpoint(s.ctx, r); err != nil {
 			return err
 		}
+	} else {
+		s.headLock.RUnlock()
 	}
-
 	// Save initial sync cached blocks to the DB before stop.
 	return s.cfg.BeaconDB.SaveBlocks(s.ctx, s.getInitSyncBlocks())
 }
@@ -231,8 +236,9 @@ func (s *Service) StartFromSavedState(saved state.BeaconState) error {
 			return errors.Wrap(err, "could not set finalized block as validated")
 		}
 	}
-
+	s.headLock.RLock()
 	h := s.headBlock().Block()
+	s.headLock.RUnlock()
 	if h.Slot() > fSlot {
 		log.WithFields(logrus.Fields{
 			"startSlot": fSlot,
```
