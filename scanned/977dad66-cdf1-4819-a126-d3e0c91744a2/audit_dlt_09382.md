# [?] fix(validator): Fix race condition and possible deadlock in ABCI middleware (#1537)

## Summary
Severity: Unknown
Chain: Berachain
Component: berachain/beacon-kit
Published: 2024-06-19
Source: https://github.com/berachain/beacon-kit/commit/7247d6bdd66add8ec7ee3ceead7a2b9092ba182b
Type: security-commit

## Details
fix(validator): Fix race condition and possible deadlock in ABCI middleware (#1537)

## Patch
### mod/beacon/validator/service.go
```diff
@@ -222,10 +222,10 @@ func (s *Service[
 	blk, sidecars, err := s.RequestBlockForProposal(
 		req.Context(), req.Data(),
 	)
-
 	if err != nil {
 		s.logger.Error("failed to build block", "err", err)
 	}
+
 	// Send the built block back on the feed.
 	s.blkFeed.Send(asynctypes.NewEvent(
 		req.Context(), events.BeaconBlockBuilt, blk, err,
```

### mod/runtime/pkg/middleware/abci.go
```diff
@@ -23,6 +23,7 @@ package middleware
 import (
 	"context"
 	"encoding/json"
+	"sync"
 	"time"
 
 	appmodulev2 "cosmossdk.io/core/appmodule/v2"
@@ -100,10 +101,10 @@ func (h *ABCIMiddleware[
 	req *cmtabci.PrepareProposalRequest,
 ) (*cmtabci.PrepareProposalResponse, error) {
 	var (
-		err           error
-		startTime     = time.Now()
-		sidecarsBz    []byte
-		beaconBlockBz []byte
+		wg                          sync.WaitGroup
+		startTime                   = time.Now()
+		beaconBlockErr, sidecarsErr error
+		beaconBlockBz, sidecarsBz   []byte
 	)
 	defer h.metrics.measurePrepareProposalDuration(startTime)
 
@@ -113,14 +114,25 @@ func (h *ABCIMiddleware[
 		ctx, events.NewSlot, math.Slot(req.Height),
 	))
 
-	beaconBlockBz, err = h.waitforBeaconBlk(ctx)
-	if err != nil {
-		return nil, err
-	}
+	// Using a wait group instead of an errgroup to ensure we drain
+	// the associated channels for the beacon block and sidecars.
+	//nolint:mnd // bet.
+	wg.Add(2)
+	go func() {
+		defer wg.Done()
+		beaconBlockBz, beaconBlockErr = h.waitforBeaconBlk(ctx)
+	}()
 
-	sidecarsBz, err = h.waitForSidecars(ctx)
-	if err != nil {
-		return nil, err
+	go func() {
+		defer wg.Done()
+		sidecarsBz, sidecarsErr = h.waitForSidecars(ctx)
+	}()
+
+	wg.Wait()
+	if beaconBlockErr != nil {
+		return nil, beaconBlockErr
+	} else if sidecarsErr != nil {
+		return nil, sidecarsErr
 	}
 
 	return &cmtabci.PrepareProposalResponse{
@@ -139,7 +151,11 @@ func (h *ABCIMiddleware[
 	case err := <-h.prepareProposalErrCh:
 		return nil, err
 	case sidecars := <-h.prepareProposalSidecarsCh:
-		sidecarsBz, err := h.blobGossiper.Publish(gCtx, sidecars)
+		if sidecars.Error() != nil {
+			return nil, sidecars.Error()
+		}
+
+		sidecarsBz, err := h.blobGossiper.Publish(gCtx, sidecars.Data())
 		if err != nil {
 			h.logger.Error("failed to publish blobs", "error", err)
 		}
@@ -158,7 +174,13 @@ func (h *ABCIMiddleware[
 	case err := <-h.prepareProposalErrCh:
 		return nil, err
 	case beaconBlock := <-h.prepareProposalBlkCh:
-		beaconBlockBz, err := h.beaconBlockGossiper.Publish(gCtx, beaconBlock)
+		if beaconBlock.Error() != nil {
+			return nil, beaconBlock.Error()
+		}
+		beaconBlockBz, err := h.beaconBlockGossiper.Publish(
+			gCtx,
+			beaconBlock.Data(),
+		)
 		if err != nil {
 			h.logger.Error("failed to publish beacon block", "error", err)
 		}
```

### mod/runtime/pkg/middleware/middleware.go
```diff
@@ -99,9 +99,9 @@ type ABCIMiddleware[
 	// method.
 	prepareProposalErrCh chan error
 	// blkCh is used to communicate the beacon block to the EndBlock method.
-	prepareProposalBlkCh chan BeaconBlockT
+	prepareProposalBlkCh chan *asynctypes.Event[BeaconBlockT]
 	// sidecarsCh is used to communicate the sidecars to the EndBlock method.
-	prepareProposalSidecarsCh chan BlobSidecarsT
+	prepareProposalSidecarsCh chan *asynctypes.Event[BlobSidecarsT]
 	//
 	// FinalizeBlock
 	//
@@ -156,16 +156,22 @@ func NewABCIMiddleware[
 			NewNoopBlockGossipHandler[BeaconBlockT, encoding.ABCIRequest](
 			chainSpec,
 		),
-		logger:                    logger,
-		metrics:                   newABCIMiddlewareMetrics(telemetrySink),
-		blkFeed:                   blkFeed,
-		sidecarsFeed:              sidecarsFeed,
-		slotFeed:                  slotFeed,
-		valUpdatesCh:              make(chan transition.ValidatorUpdates),
-		finalizeBlockErrCh:        make(chan error, 1),
-		prepareProposalBlkCh:      make(chan BeaconBlockT, 1),
-		prepareProposalSidecarsCh: make(chan BlobSidecarsT, 1),
-		prepareProposalErrCh:      make(chan error, 1),
+		logger:             logger,
+		metrics:            newABCIMiddlewareMetrics(telemetrySink),
+		blkFeed:            blkFeed,
+		sidecarsFeed:       sidecarsFeed,
+		slotFeed:           slotFeed,
+		valUpdatesCh:       make(chan transition.ValidatorUpdates),
+		finalizeBlockErrCh: make(chan error, 1),
+		prepareProposalBlkCh: make(
+			chan *asynctypes.Event[BeaconBlockT],
+			1,
+		),
+		prepareProposalSidecarsCh: make(
+			chan *asynctypes.Event[BlobSidecarsT],
+			1,
+		),
+		prepareProposalErrCh: make(chan error, 1),
 	}
 }
 
@@ -204,18 +210,14 @@ func (am *ABCIMiddleware[
 			return
 		case blk := <-subBlkCh:
 			if blk.Type() == events.BeaconBlockBuilt {
-				if blk.Error() != nil {
-					am.prepareProposalErrCh <- blk.Error()
-					continue
-				}
-				am.prepareProposalBlkCh <- blk.Data()
+				am.prepareProposalBlkCh <- blk
 			}
 		case sidecars := <-subSidecarsCh:
 			if sidecars.Error() != nil {
 				am.prepareProposalErrCh <- sidecars.Error()
 				continue
 			}
-			am.prepareProposalSidecarsCh <- sidecars.Data()
+			am.prepareProposalSidecarsCh <- sidecars
 		}
 	}
 }
```
